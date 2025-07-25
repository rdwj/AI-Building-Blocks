#!/usr/bin/env python3
"""
Enhanced STIG Parser - Real implementation for STIG XML files

This parser handles SCAP/ARF format STIG files and extracts actual findings.
"""

import sys
import os
import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add the XML parser to path
parent_dir = Path(__file__).parent.parent
xml_parser_path = parent_dir / "xml_files" / "src"
sys.path.append(str(xml_parser_path))

@dataclass
class STIGFinding:
    """Represents a single STIG security finding"""
    rule_id: str
    severity: str
    title: str
    description: str
    check_text: str
    fix_text: str
    status: str  # pass/fail/not_applicable/not_reviewed
    references: List[str]
    group_id: Optional[str] = None
    version: Optional[str] = None
    weight: Optional[str] = None

class STIGParser:
    """Enhanced parser for STIG XML files"""
    
    def __init__(self):
        self.findings = []
        self.stig_metadata = {}
        self.namespaces = {}
        
    def parse_stig_file(self, file_path: str) -> List[STIGFinding]:
        """
        Parse STIG XML file and extract all findings
        Handles both XCCDF and ARF format files
        """
        
        print(f"🔍 Parsing STIG file: {file_path}")
        
        try:
            # Parse XML with namespace handling
            context = ET.iterparse(file_path, events=('start', 'start-ns'))
            
            # Collect namespaces
            for event, elem in context:
                if event == 'start-ns':
                    prefix, uri = elem
                    self.namespaces[prefix or 'default'] = uri
                    
                # Stop after collecting namespaces from root
                if event == 'start':
                    break
            
            print(f"📋 Detected namespaces: {list(self.namespaces.keys())}")
            
            # Now parse the full document
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Detect document format and parse accordingly
            if self._is_arf_format(root):
                print("📄 Detected ARF (Asset Reporting Format)")
                self.findings = self._parse_arf_format(root)
            elif self._is_xccdf_format(root):
                print("📄 Detected XCCDF format")
                self.findings = self._parse_xccdf_format(root)
            else:
                print("📄 Unknown format, attempting generic parsing")
                self.findings = self._parse_generic_format(root)
            
            print(f"✅ Extracted {len(self.findings)} findings")
            return self.findings
            
        except Exception as e:
            print(f"❌ Error parsing STIG file: {e}")
            return []
    
    def _is_arf_format(self, root) -> bool:
        """Check if document is ARF format"""
        return 'asset-report-collection' in root.tag or 'arf:' in root.tag
    
    def _is_xccdf_format(self, root) -> bool:
        """Check if document is XCCDF format"""
        return 'Benchmark' in root.tag or 'TestResult' in root.tag or 'xccdf' in root.tag
    
    def _parse_arf_format(self, root) -> List[STIGFinding]:
        """Parse ARF format STIG file"""
        findings = []
        
        try:
            # Search for TestResult elements in reports
            for elem in root.iter():
                if 'TestResult' in elem.tag:
                    elem_id = elem.get('id', 'no-id')
                    print(f"🎯 Found TestResult: {elem_id}")
                    test_findings = self._extract_test_result_findings(elem)
                    findings.extend(test_findings)
                    
                # Also look for rule-result elements
                elif 'rule-result' in elem.tag:
                    finding = self._extract_rule_result_finding(elem)
                    if finding:
                        findings.append(finding)
        
        except Exception as e:
            print(f"⚠️  ARF parsing error: {e}")
        
        return findings
    
    def _parse_xccdf_format(self, root) -> List[STIGFinding]:
        """Parse XCCDF format STIG file"""
        findings = []
        
        try:
            # Look for TestResult elements
            for test_result in root.iter():
                if 'TestResult' in test_result.tag:
                    test_findings = self._extract_test_result_findings(test_result)
                    findings.extend(test_findings)
                    
                # Look for Rule elements if no TestResult
                elif 'Rule' in test_result.tag:
                    rule_finding = self._extract_rule_finding(test_result)
                    if rule_finding:
                        findings.append(rule_finding)
        
        except Exception as e:
            print(f"⚠️  XCCDF parsing error: {e}")
        
        return findings
    
    def _parse_generic_format(self, root) -> List[STIGFinding]:
        """Generic parsing for unknown formats"""
        findings = []
        
        # Look for any elements that might contain findings
        for elem in root.iter():
            if any(keyword in elem.tag.lower() for keyword in ['rule', 'finding', 'check']):
                if elem.get('id') and any(text_elem.text for text_elem in elem.iter() if text_elem.text):
                    finding = self._extract_generic_finding(elem)
                    if finding:
                        findings.append(finding)
        
        return findings
    
    def _extract_test_result_findings(self, test_result_elem) -> List[STIGFinding]:
        """Extract findings from TestResult element"""
        findings = []
        
        try:
            # Look for rule-result elements
            for rule_result in test_result_elem.iter():
                if 'rule-result' in rule_result.tag:
                    finding = self._extract_rule_result_finding(rule_result)
                    if finding:
                        findings.append(finding)
        
        except Exception as e:
            print(f"⚠️  TestResult extraction error: {e}")
        
        return findings
    
    def _extract_rule_result_finding(self, rule_result_elem) -> Optional[STIGFinding]:
        """Extract finding from rule-result element"""
        
        try:
            # Get basic attributes
            rule_id = rule_result_elem.get('idref', 'unknown')
            result = rule_result_elem.get('result', 'unknown')
            severity = rule_result_elem.get('severity', 'unknown')
            weight = rule_result_elem.get('weight', '1.0')
            
            # Extract text content
            title = ""
            description = ""
            check_text = ""
            fix_text = ""
            
            # Look for nested elements
            for child in rule_result_elem.iter():
                if 'title' in child.tag.lower() and child.text:
                    title = child.text.strip()
                elif 'description' in child.tag.lower() and child.text:
                    description = child.text.strip()
                elif 'check' in child.tag.lower() and child.text:
                    check_text = child.text.strip()
                elif 'fix' in child.tag.lower() and child.text:
                    fix_text = child.text.strip()
            
            # Create finding if we have minimum required info
            if rule_id != 'unknown':
                return STIGFinding(
                    rule_id=rule_id,
                    severity=severity,
                    title=title or f"Rule {rule_id}",
                    description=description or "No description available",
                    check_text=check_text or "No check text available",
                    fix_text=fix_text or "No fix text available",
                    status=result,
                    references=[],
                    weight=weight
                )
        
        except Exception as e:
            print(f"⚠️  Rule result extraction error: {e}")
        
        return None
    
    def _extract_rule_finding(self, rule_elem) -> Optional[STIGFinding]:
        """Extract finding from Rule element"""
        
        try:
            rule_id = rule_elem.get('id', 'unknown')
            severity = rule_elem.get('severity', 'medium')
            weight = rule_elem.get('weight', '1.0')
            
            title = ""
            description = ""
            check_text = ""
            fix_text = ""
            references = []
            
            # Extract nested content
            for child in rule_elem.iter():
                tag_lower = child.tag.lower()
                if 'title' in tag_lower and child.text:
                    title = child.text.strip()
                elif 'description' in tag_lower and child.text:
                    description = child.text.strip()
                elif 'check' in tag_lower and child.text:
                    check_text = child.text.strip()
                elif 'fix' in tag_lower and child.text:
                    fix_text = child.text.strip()
                elif 'reference' in tag_lower and child.text:
                    references.append(child.text.strip())
            
            if rule_id != 'unknown':
                return STIGFinding(
                    rule_id=rule_id,
                    severity=severity,
                    title=title or f"Rule {rule_id}",
                    description=description or "No description available",
                    check_text=check_text or "No check text available",
                    fix_text=fix_text or "No fix text available",
                    status="not_reviewed",  # Default status for rules without results
                    references=references,
                    weight=weight
                )
        
        except Exception as e:
            print(f"⚠️  Rule extraction error: {e}")
        
        return None
    
    def _extract_generic_finding(self, elem) -> Optional[STIGFinding]:
        """Extract finding from generic element"""
        
        try:
            elem_id = elem.get('id', 'unknown')
            
            # Try to extract any text content
            texts = []
            for child in elem.iter():
                if child.text and child.text.strip():
                    texts.append(child.text.strip())
            
            combined_text = " ".join(texts[:3])  # First 3 text elements
            
            if elem_id != 'unknown' and combined_text:
                return STIGFinding(
                    rule_id=elem_id,
                    severity="unknown",
                    title=combined_text[:100],
                    description=combined_text,
                    check_text="Generic check",
                    fix_text="Generic fix",
                    status="unknown",
                    references=[]
                )
        
        except Exception as e:
            print(f"⚠️  Generic extraction error: {e}")
        
        return None
    
    def get_findings_by_severity(self, severity: str) -> List[STIGFinding]:
        """Filter findings by severity level"""
        return [f for f in self.findings if f.severity.lower() == severity.lower()]
    
    def get_failed_findings(self) -> List[STIGFinding]:
        """Get only findings that failed compliance checks"""
        return [f for f in self.findings if f.status in ['fail', 'error', 'unknown']]
    
    def get_findings_summary(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        
        if not self.findings:
            return {"error": "No findings available"}
        
        severities = {}
        statuses = {}
        
        for finding in self.findings:
            # Count by severity
            sev = finding.severity.lower()
            severities[sev] = severities.get(sev, 0) + 1
            
            # Count by status
            stat = finding.status.lower()
            statuses[stat] = statuses.get(stat, 0) + 1
        
        return {
            "total_findings": len(self.findings),
            "by_severity": severities,
            "by_status": statuses,
            "failed_count": len(self.get_failed_findings()),
            "critical_count": len(self.get_findings_by_severity('critical')),
            "high_count": len(self.get_findings_by_severity('high'))
        }
    
    def export_findings_json(self, output_path: str):
        """Export findings to JSON for LLM processing"""
        
        findings_data = []
        for finding in self.findings:
            findings_data.append({
                'rule_id': finding.rule_id,
                'severity': finding.severity,
                'title': finding.title[:200] + "..." if len(finding.title) > 200 else finding.title,
                'description': finding.description[:500] + "..." if len(finding.description) > 500 else finding.description,
                'check_text': finding.check_text[:300] + "..." if len(finding.check_text) > 300 else finding.check_text,
                'fix_text': finding.fix_text,
                'status': finding.status,
                'references': finding.references,
                'weight': finding.weight
            })
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump({
                'metadata': self.stig_metadata,
                'summary': self.get_findings_summary(),
                'findings': findings_data
            }, f, indent=2)
        
        print(f"💾 Exported {len(findings_data)} findings to {output_path}")

def test_stig_parser():
    """Test the STIG parser with sample files"""
    
    # Test with sample STIG file
    sample_files = [
        "../xml_files/sample_data/node2.example.com-STIG-20250710162433.xml",
        "../xml_files/sample_data/node2.example.com-PCI-20250710162255.xml"
    ]
    
    for sample_file in sample_files:
        if Path(sample_file).exists():
            print(f"\n🧪 Testing with {sample_file}")
            parser = STIGParser()
            findings = parser.parse_stig_file(sample_file)
            
            if findings:
                summary = parser.get_findings_summary()
                print(f"📊 Summary: {summary}")
                
                # Show first few findings
                for i, finding in enumerate(findings[:3]):
                    print(f"\n📋 Finding {i+1}:")
                    print(f"   ID: {finding.rule_id}")
                    print(f"   Severity: {finding.severity}")
                    print(f"   Status: {finding.status}")
                    print(f"   Title: {finding.title[:60]}...")
                
                # Export to JSON
                output_file = f"findings/{Path(sample_file).stem}_findings.json"
                parser.export_findings_json(output_file)
                
                return True
            else:
                print(f"❌ No findings extracted from {sample_file}")
    
    print("❌ No sample files found for testing")
    return False

if __name__ == "__main__":
    print("🧪 Testing Enhanced STIG Parser")
    print("=" * 50)
    
    success = test_stig_parser()
    
    if success:
        print("\n✅ STIG parser test completed!")
    else:
        print("\n❌ STIG parser test failed!")
