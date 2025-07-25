#!/usr/bin/env python3
"""
Enhanced STIG Parser - Complete implementation for SCAP/ARF STIG files

This parser extracts comprehensive information from both Rule definitions 
and TestResults, including target extraction for Ansible playbook generation.
"""

import sys
import os
import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import re

# Add the XML parser to path
parent_dir = Path(__file__).parent.parent
xml_parser_path = parent_dir / "xml_files" / "src"
sys.path.append(str(xml_parser_path))

@dataclass
class TargetInfo:
    """Represents target information for Ansible playbook generation"""
    target_type: str
    target_name: str
    action_context: str
    ansible_module: str
    ansible_params: Dict[str, Any]

@dataclass
class ComplianceMapping:
    """Represents compliance framework mappings"""
    cci_refs: List[str]
    nist_refs: List[str]
    cis_refs: List[str]
    disa_refs: List[str]
    pcidss_refs: List[str]

@dataclass
class EnhancedSTIGFinding:
    """Represents a comprehensive STIG security finding"""
    # Basic identification
    rule_id: str
    group_id: Optional[str]
    version: Optional[str]
    
    # Status and severity
    severity: str
    status: str  # pass/fail/not_applicable/not_reviewed/unknown
    weight: Optional[str]
    
    # Rich content from rule definitions
    title: str
    description: str
    rationale: str
    check_text: str
    fix_text: str
    fixtext: str
    
    # Target information for Ansible
    target_info: Optional[TargetInfo]
    
    # Compliance mappings
    compliance: ComplianceMapping
    
    # Additional metadata
    references: List[str]
    platform_applicability: List[str]
    remediation_type: Optional[str]
    complexity: Optional[str]

class EnhancedSTIGParser:
    """Enhanced parser for STIG XML files with comprehensive extraction"""
    
    def __init__(self):
        self.findings = []
        self.rule_definitions = {}
        self.stig_metadata = {}
        self.namespaces = {
            'xccdf': 'http://checklists.nist.gov/xccdf/1.2',
            'arf': 'http://scap.nist.gov/schema/asset-reporting-format/1.1',
            'ds': 'http://scap.nist.gov/schema/scap/source/1.2',
            'oval': 'http://oval.mitre.org/XMLSchema/oval-definitions-5',
            'cpe': 'http://cpe.mitre.org/language/2.0'
        }
        
    def parse_stig_file(self, file_path: str) -> List[EnhancedSTIGFinding]:
        """
        Parse STIG XML file and extract comprehensive findings
        Handles both XCCDF and ARF format files
        """
        
        print(f"🔍 Parsing enhanced STIG file: {file_path}")
        
        try:
            # Parse XML with improved namespace handling
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Update namespaces from document
            self._extract_namespaces(root)
            
            print(f"📋 Detected namespaces: {list(self.namespaces.keys())}")
            
            # Extract metadata
            self.stig_metadata = self._extract_metadata(root)
            print(f"📄 Document metadata: {self.stig_metadata.get('format', 'Unknown')}")
            
            # Step 1: Extract rule definitions (rich content)
            print("🔄 Phase 1: Extracting rule definitions...")
            self._extract_rule_definitions(root)
            print(f"📚 Found {len(self.rule_definitions)} rule definitions")
            
            # Step 2: Extract test results and merge with definitions
            print("🔄 Phase 2: Extracting test results and merging...")
            self.findings = self._extract_and_merge_findings(root)
            print(f"✅ Created {len(self.findings)} enhanced findings")
            
            return self.findings
            
        except Exception as e:
            print(f"❌ Error parsing STIG file: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _extract_namespaces(self, root):
        """Extract and register namespaces from document"""
        # Get namespaces from root element
        for prefix, uri in root.nsmap.items() if hasattr(root, 'nsmap') else []:
            if prefix:
                self.namespaces[prefix] = uri
            else:
                self.namespaces['default'] = uri
        
        # Manual namespace detection for ElementTree
        for elem in root.iter():
            if '}' in elem.tag:
                namespace = elem.tag.split('}')[0][1:]
                local_name = elem.tag.split('}')[1]
                
                # Try to deduce prefix
                if 'xccdf' in namespace:
                    self.namespaces['xccdf'] = namespace
                elif 'arf' in namespace:
                    self.namespaces['arf'] = namespace
                elif 'oval' in namespace:
                    self.namespaces['oval'] = namespace
    
    def _extract_metadata(self, root) -> Dict[str, Any]:
        """Extract document metadata"""
        metadata = {}
        
        try:
            # Detect format
            if 'asset-report-collection' in root.tag:
                metadata['format'] = 'ARF'
            elif 'Benchmark' in root.tag or 'TestResult' in root.tag:
                metadata['format'] = 'XCCDF'
            else:
                metadata['format'] = 'Unknown'
            
            # Extract benchmark info
            for elem in root.iter():
                if 'Benchmark' in elem.tag:
                    metadata['benchmark_id'] = elem.get('id', '')
                    
                    # Look for title and description
                    for child in elem:
                        if 'title' in child.tag and child.text:
                            metadata['title'] = child.text.strip()
                        elif 'description' in child.tag and child.text:
                            metadata['description'] = child.text.strip()[:200]
                    break
        
        except Exception as e:
            print(f"⚠️  Metadata extraction error: {e}")
        
        return metadata
    
    def _extract_rule_definitions(self, root):
        """Extract comprehensive rule definitions"""
        self.rule_definitions = {}
        
        try:
            # Find all Rule elements
            rules_found = 0
            for elem in root.iter():
                if self._is_rule_element(elem):
                    rules_found += 1
                    rule_def = self._extract_single_rule_definition(elem)
                    if rule_def:
                        self.rule_definitions[rule_def['rule_id']] = rule_def
            
            print(f"🔍 Processed {rules_found} rule elements, extracted {len(self.rule_definitions)} definitions")
        
        except Exception as e:
            print(f"❌ Rule definition extraction error: {e}")
    
    def _is_rule_element(self, elem) -> bool:
        """Check if element is a Rule definition"""
        return ('Rule' in elem.tag and 
                elem.get('id') is not None and
                'rule' in elem.get('id', '').lower())
    
    def _extract_single_rule_definition(self, rule_elem) -> Optional[Dict[str, Any]]:
        """Extract comprehensive information from a single Rule element"""
        
        try:
            rule_id = rule_elem.get('id', '')
            if not rule_id:
                return None
            
            rule_def = {
                'rule_id': rule_id,
                'group_id': rule_elem.get('group_id'),
                'severity': rule_elem.get('severity', 'medium'),
                'weight': rule_elem.get('weight'),
                'title': '',
                'description': '',
                'rationale': '',
                'check_text': '',
                'fix_text': '',
                'fixtext': '',
                'references': [],
                'cci_refs': [],
                'nist_refs': [],
                'cis_refs': [],
                'disa_refs': [],
                'pcidss_refs': [],
                'platform_applicability': [],
                'remediation_type': None,
                'complexity': None
            }
            
            # Extract nested content
            for child in rule_elem.iter():
                tag_name = child.tag.split('}')[-1].lower()  # Remove namespace
                
                if tag_name == 'title' and child.text:
                    rule_def['title'] = child.text.strip()
                
                elif tag_name == 'description':
                    rule_def['description'] = self._extract_text_content(child)
                
                elif tag_name == 'rationale':
                    rule_def['rationale'] = self._extract_text_content(child)
                
                elif tag_name == 'check':
                    # Check content and check-content
                    check_text = self._extract_text_content(child)
                    if check_text:
                        rule_def['check_text'] = check_text
                
                elif tag_name == 'fix':
                    rule_def['fix_text'] = self._extract_text_content(child)
                    # Extract remediation type from system attribute
                    system = child.get('system', '')
                    if 'commands' in system:
                        rule_def['remediation_type'] = 'command'
                    elif 'ansible' in system:
                        rule_def['remediation_type'] = 'ansible'
                
                elif tag_name == 'fixtext':
                    rule_def['fixtext'] = self._extract_text_content(child)
                    # Extract complexity from fixref
                    fixref = child.get('fixref', '')
                    if fixref:
                        rule_def['complexity'] = self._determine_complexity(fixref)
                
                elif tag_name == 'reference':
                    href = child.get('href', '')
                    if href:
                        rule_def['references'].append(href)
                
                elif tag_name == 'ident':
                    system = child.get('system', '')
                    ident_text = child.text or ''
                    
                    if 'cyber.mil' in system and ident_text.startswith('CCI-'):
                        rule_def['cci_refs'].append(ident_text)
                    elif 'nist' in system.lower():
                        rule_def['nist_refs'].append(ident_text)
                    elif 'cis' in system.lower():
                        rule_def['cis_refs'].append(ident_text)
                    elif 'disa' in system.lower():
                        rule_def['disa_refs'].append(ident_text)
                    elif 'pci' in system.lower():
                        rule_def['pcidss_refs'].append(ident_text)
                
                elif tag_name == 'platform':
                    if child.get('idref'):
                        rule_def['platform_applicability'].append(child.get('idref'))
            
            return rule_def
        
        except Exception as e:
            print(f"⚠️  Single rule extraction error for {rule_elem.get('id', 'unknown')}: {e}")
            return None
    
    def _extract_text_content(self, elem) -> str:
        """Extract all text content from element, handling nested HTML"""
        if elem is None:
            return ""
        
        texts = []
        
        # Get direct text
        if elem.text:
            texts.append(elem.text.strip())
        
        # Get text from all children
        for child in elem.iter():
            if child.text and child.text.strip():
                texts.append(child.text.strip())
            if child.tail and child.tail.strip():
                texts.append(child.tail.strip())
        
        # Clean and join
        full_text = ' '.join(texts)
        # Remove extra whitespace
        full_text = re.sub(r'\s+', ' ', full_text)
        return full_text.strip()
    
    def _determine_complexity(self, fixref: str) -> str:
        """Determine complexity from fixref or other indicators"""
        if 'low' in fixref.lower():
            return 'low'
        elif 'medium' in fixref.lower():
            return 'medium'
        elif 'high' in fixref.lower():
            return 'high'
        else:
            return 'medium'  # default
    
    def _extract_and_merge_findings(self, root) -> List[EnhancedSTIGFinding]:
        """Extract test results and merge with rule definitions"""
        findings = []
        
        try:
            # Find TestResult elements
            test_results_found = 0
            for elem in root.iter():
                if 'TestResult' in elem.tag:
                    test_results_found += 1
                    print(f"🎯 Processing TestResult: {elem.get('id', 'no-id')}")
                    result_findings = self._extract_test_result_findings(elem)
                    findings.extend(result_findings)
            
            print(f"🔍 Processed {test_results_found} TestResult elements")
            
            # If no test results found, create findings from rule definitions only
            if not findings and self.rule_definitions:
                print("📋 No test results found, creating findings from rule definitions")
                for rule_id, rule_def in self.rule_definitions.items():
                    finding = self._create_finding_from_rule_def(rule_def, status='not_reviewed')
                    if finding:
                        findings.append(finding)
        
        except Exception as e:
            print(f"❌ Test result extraction error: {e}")
        
        return findings
    
    def _extract_test_result_findings(self, test_result_elem) -> List[EnhancedSTIGFinding]:
        """Extract findings from TestResult element and merge with rule definitions"""
        findings = []
        
        try:
            for rule_result in test_result_elem.iter():
                if 'rule-result' in rule_result.tag:
                    finding = self._create_finding_from_rule_result(rule_result)
                    if finding:
                        findings.append(finding)
        
        except Exception as e:
            print(f"⚠️  TestResult processing error: {e}")
        
        return findings
    
    def _create_finding_from_rule_result(self, rule_result_elem) -> Optional[EnhancedSTIGFinding]:
        """Create comprehensive finding from rule-result element"""
        
        try:
            # Extract basic result info
            rule_id = rule_result_elem.get('idref', '')
            if not rule_id:
                return None
            
            result = rule_result_elem.get('result', 'unknown')
            severity = rule_result_elem.get('severity', 'medium')
            weight = rule_result_elem.get('weight')
            
            # Get rule definition if available
            rule_def = self.rule_definitions.get(rule_id, {})
            
            # Create finding
            return self._create_enhanced_finding(
                rule_id=rule_id,
                status=result,
                severity=severity,
                weight=weight,
                rule_def=rule_def
            )
        
        except Exception as e:
            print(f"⚠️  Rule result processing error: {e}")
            return None
    
    def _create_finding_from_rule_def(self, rule_def: Dict[str, Any], status: str) -> Optional[EnhancedSTIGFinding]:
        """Create finding from rule definition only"""
        
        try:
            return self._create_enhanced_finding(
                rule_id=rule_def['rule_id'],
                status=status,
                severity=rule_def.get('severity', 'medium'),
                weight=rule_def.get('weight'),
                rule_def=rule_def
            )
        
        except Exception as e:
            print(f"⚠️  Rule def finding creation error: {e}")
            return None
    
    def _create_enhanced_finding(self, rule_id: str, status: str, severity: str, 
                               weight: Optional[str], rule_def: Dict[str, Any]) -> EnhancedSTIGFinding:
        """Create enhanced finding with all information"""
        
        # Extract target information
        target_info = self._extract_target_info(rule_id, rule_def)
        
        # Create compliance mapping
        compliance = ComplianceMapping(
            cci_refs=rule_def.get('cci_refs', []),
            nist_refs=rule_def.get('nist_refs', []),
            cis_refs=rule_def.get('cis_refs', []),
            disa_refs=rule_def.get('disa_refs', []),
            pcidss_refs=rule_def.get('pcidss_refs', [])
        )
        
        return EnhancedSTIGFinding(
            rule_id=rule_id,
            group_id=rule_def.get('group_id'),
            version=rule_def.get('version'),
            severity=severity,
            status=status,
            weight=weight,
            title=rule_def.get('title', f"Rule {rule_id}"),
            description=rule_def.get('description', 'No description available'),
            rationale=rule_def.get('rationale', 'No rationale available'),
            check_text=rule_def.get('check_text', 'No check text available'),
            fix_text=rule_def.get('fix_text', 'No fix text available'),
            fixtext=rule_def.get('fixtext', 'No fixtext available'),
            target_info=target_info,
            compliance=compliance,
            references=rule_def.get('references', []),
            platform_applicability=rule_def.get('platform_applicability', []),
            remediation_type=rule_def.get('remediation_type'),
            complexity=rule_def.get('complexity')
        )
    
    def _extract_target_info(self, rule_id: str, rule_def: Dict[str, Any]) -> Optional[TargetInfo]:
        """Extract target information for Ansible playbook generation"""
        
        try:
            # Clean rule ID for pattern matching
            clean_rule = rule_id.replace('xccdf_org.ssgproject.content_rule_', '')
            clean_rule = clean_rule.replace('xccdf_mil.disa.stig_rule_', '')
            
            # File ownership patterns
            if clean_rule.startswith('file_groupowner_'):
                path_component = clean_rule.replace('file_groupowner_', '')
                target_path = self._convert_path_component(path_component)
                return TargetInfo(
                    target_type='file_ownership',
                    target_name=target_path,
                    action_context='group=root',
                    ansible_module='file',
                    ansible_params={
                        'path': target_path,
                        'group': 'root',
                        'recurse': True if target_path.endswith('/*') else False
                    }
                )
            
            elif clean_rule.startswith('file_owner_'):
                path_component = clean_rule.replace('file_owner_', '')
                target_path = self._convert_path_component(path_component)
                return TargetInfo(
                    target_type='file_ownership',
                    target_name=target_path,
                    action_context='owner=root',
                    ansible_module='file',
                    ansible_params={
                        'path': target_path,
                        'owner': 'root',
                        'recurse': True if target_path.endswith('/*') else False
                    }
                )
            
            elif clean_rule.startswith('file_permissions_'):
                path_component = clean_rule.replace('file_permissions_', '')
                target_path = self._convert_path_component(path_component)
                # Extract expected permissions from rule content
                expected_mode = self._extract_expected_permissions(rule_def)
                return TargetInfo(
                    target_type='file_permission',
                    target_name=target_path,
                    action_context=f'mode={expected_mode}',
                    ansible_module='file',
                    ansible_params={
                        'path': target_path,
                        'mode': expected_mode
                    }
                )
            
            # Package patterns
            elif clean_rule.startswith('package_'):
                package_action = 'absent' if 'removed' in clean_rule else 'present'
                package_name = clean_rule.replace('package_', '').replace('_removed', '').replace('_installed', '')
                return TargetInfo(
                    target_type='package',
                    target_name=package_name,
                    action_context=f'state={package_action}',
                    ansible_module='yum',
                    ansible_params={
                        'name': package_name,
                        'state': package_action
                    }
                )
            
            # Service patterns
            elif clean_rule.startswith('service_'):
                service_action = 'stopped' if 'disabled' in clean_rule else 'started'
                service_name = clean_rule.replace('service_', '').replace('_disabled', '').replace('_enabled', '')
                return TargetInfo(
                    target_type='service',
                    target_name=service_name,
                    action_context=f'state={service_action}',
                    ansible_module='systemd',
                    ansible_params={
                        'name': service_name,
                        'state': service_action,
                        'enabled': service_action == 'started'
                    }
                )
            
            # Sysctl patterns
            elif clean_rule.startswith('sysctl_'):
                sysctl_param = clean_rule.replace('sysctl_', '').replace('_', '.')
                expected_value = self._extract_expected_sysctl_value(rule_def)
                return TargetInfo(
                    target_type='sysctl',
                    target_name=sysctl_param,
                    action_context=f'value={expected_value}',
                    ansible_module='sysctl',
                    ansible_params={
                        'name': sysctl_param,
                        'value': expected_value,
                        'state': 'present',
                        'reload': True
                    }
                )
            
            # Mount patterns
            elif 'mount' in clean_rule:
                mount_point = self._extract_mount_point(clean_rule, rule_def)
                mount_options = self._extract_mount_options(rule_def)
                return TargetInfo(
                    target_type='mount',
                    target_name=mount_point,
                    action_context=f'opts={mount_options}',
                    ansible_module='mount',
                    ansible_params={
                        'path': mount_point,
                        'opts': mount_options,
                        'state': 'mounted'
                    }
                )
            
            # Default fallback - try to extract from rule content
            else:
                return self._extract_target_from_content(clean_rule, rule_def)
        
        except Exception as e:
            print(f"⚠️  Target extraction error for {rule_id}: {e}")
            return None
    
    def _convert_path_component(self, path_component: str) -> str:
        """Convert path component to actual file path"""
        # Common conversions
        conversions = {
            'cron_hourly': '/etc/cron.hourly/*',
            'cron_daily': '/etc/cron.daily/*',
            'cron_weekly': '/etc/cron.weekly/*',
            'cron_monthly': '/etc/cron.monthly/*',
            'cron_d': '/etc/cron.d/*',
            'crontab': '/etc/crontab',
            'ssh_config': '/etc/ssh/ssh_config',
            'sshd_config': '/etc/ssh/sshd_config',
            'sudoers': '/etc/sudoers',
            'passwd': '/etc/passwd',
            'shadow': '/etc/shadow',
            'group': '/etc/group',
            'hosts': '/etc/hosts'
        }
        
        if path_component in conversions:
            return conversions[path_component]
        
        # Generic conversion
        return f"/etc/{path_component.replace('_', '/')}"
    
    def _extract_expected_permissions(self, rule_def: Dict[str, Any]) -> str:
        """Extract expected file permissions from rule content"""
        content = f"{rule_def.get('description', '')} {rule_def.get('check_text', '')} {rule_def.get('fix_text', '')}"
        
        # Look for octal permissions
        perm_match = re.search(r'\b0?([0-7]{3,4})\b', content)
        if perm_match:
            return perm_match.group(1)
        
        # Common defaults
        if 'config' in content.lower():
            return '0644'
        elif 'script' in content.lower() or 'executable' in content.lower():
            return '0755'
        else:
            return '0644'
    
    def _extract_expected_sysctl_value(self, rule_def: Dict[str, Any]) -> str:
        """Extract expected sysctl value from rule content"""
        content = f"{rule_def.get('description', '')} {rule_def.get('check_text', '')} {rule_def.get('fix_text', '')}"
        
        # Look for value assignments
        value_match = re.search(r'=\s*([0-9]+)', content)
        if value_match:
            return value_match.group(1)
        
        # Common defaults
        if 'disable' in content.lower() or 'off' in content.lower():
            return '0'
        elif 'enable' in content.lower() or 'on' in content.lower():
            return '1'
        else:
            return '1'
    
    def _extract_mount_point(self, rule_name: str, rule_def: Dict[str, Any]) -> str:
        """Extract mount point from rule"""
        if 'tmp' in rule_name:
            return '/tmp'
        elif 'var' in rule_name:
            return '/var'
        elif 'home' in rule_name:
            return '/home'
        else:
            return '/tmp'  # default
    
    def _extract_mount_options(self, rule_def: Dict[str, Any]) -> str:
        """Extract mount options from rule content"""
        content = f"{rule_def.get('description', '')} {rule_def.get('check_text', '')} {rule_def.get('fix_text', '')}"
        
        options = []
        if 'noexec' in content.lower():
            options.append('noexec')
        if 'nosuid' in content.lower():
            options.append('nosuid')
        if 'nodev' in content.lower():
            options.append('nodev')
        
        return ','.join(options) if options else 'defaults'
    
    def _extract_target_from_content(self, rule_name: str, rule_def: Dict[str, Any]) -> TargetInfo:
        """Extract target from rule content as fallback"""
        return TargetInfo(
            target_type='unknown',
            target_name=rule_name,
            action_context='manual_review_required',
            ansible_module='debug',
            ansible_params={
                'msg': f"Manual review required for rule: {rule_name}"
            }
        )
    
    def get_findings_by_severity(self, severity: str) -> List[EnhancedSTIGFinding]:
        """Filter findings by severity level"""
        return [f for f in self.findings if f.severity.lower() == severity.lower()]
    
    def get_failed_findings(self) -> List[EnhancedSTIGFinding]:
        """Get only findings that failed compliance checks"""
        return [f for f in self.findings if f.status in ['fail', 'error', 'unknown']]
    
    def get_findings_with_targets(self) -> List[EnhancedSTIGFinding]:
        """Get findings that have actionable targets for Ansible"""
        return [f for f in self.findings if f.target_info and f.target_info.target_type != 'unknown']
    
    def get_findings_summary(self) -> Dict[str, Any]:
        """Generate comprehensive summary statistics"""
        
        if not self.findings:
            return {"error": "No findings available"}
        
        severities = {}
        statuses = {}
        target_types = {}
        
        for finding in self.findings:
            # Count by severity
            sev = finding.severity.lower()
            severities[sev] = severities.get(sev, 0) + 1
            
            # Count by status
            stat = finding.status.lower()
            statuses[stat] = statuses.get(stat, 0) + 1
            
            # Count by target type
            if finding.target_info:
                target_type = finding.target_info.target_type
                target_types[target_type] = target_types.get(target_type, 0) + 1
        
        return {
            "total_findings": len(self.findings),
            "by_severity": severities,
            "by_status": statuses,
            "by_target_type": target_types,
            "failed_count": len(self.get_failed_findings()),
            "actionable_count": len(self.get_findings_with_targets()),
            "critical_count": len(self.get_findings_by_severity('critical')),
            "high_count": len(self.get_findings_by_severity('high')),
            "compliance_coverage": {
                "cci_mapped": len([f for f in self.findings if f.compliance.cci_refs]),
                "nist_mapped": len([f for f in self.findings if f.compliance.nist_refs]),
                "cis_mapped": len([f for f in self.findings if f.compliance.cis_refs])
            }
        }
    
    def export_findings_json(self, output_path: str):
        """Export enhanced findings to JSON"""
        
        findings_data = []
        for finding in self.findings:
            finding_dict = asdict(finding)
            
            # Truncate long descriptions for JSON export
            if len(finding_dict['description']) > 500:
                finding_dict['description'] = finding_dict['description'][:500] + "..."
            
            findings_data.append(finding_dict)
        
        export_data = {
            'metadata': self.stig_metadata,
            'summary': self.get_findings_summary(),
            'findings': findings_data
        }
        
        # Ensure parent directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"💾 Exported {len(findings_data)} enhanced findings to {output_path}")
    
    def export_ansible_targets(self, output_path: str):
        """Export Ansible target information for playbook generation"""
        
        actionable_findings = self.get_findings_with_targets()
        
        targets_data = []
        for finding in actionable_findings:
            if finding.target_info:
                targets_data.append({
                    'rule_id': finding.rule_id,
                    'severity': finding.severity,
                    'status': finding.status,
                    'title': finding.title,
                    'target_type': finding.target_info.target_type,
                    'target_name': finding.target_info.target_name,
                    'action_context': finding.target_info.action_context,
                    'ansible_module': finding.target_info.ansible_module,
                    'ansible_params': finding.target_info.ansible_params,
                    'compliance': asdict(finding.compliance)
                })
        
        # Ensure parent directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump({
                'metadata': {
                    'total_actionable': len(targets_data),
                    'extraction_date': str(Path(output_path).stat().st_mtime if Path(output_path).exists() else 'now')
                },
                'targets': targets_data
            }, f, indent=2)
        
        print(f"🎯 Exported {len(targets_data)} Ansible targets to {output_path}")

def process_stig_file(file_path: str) -> bool:
    """Process a single STIG file"""
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"\n🧪 Processing enhanced parser with {file_path}")
    parser = EnhancedSTIGParser()
    findings = parser.parse_stig_file(file_path)
    
    if findings:
        summary = parser.get_findings_summary()
        print(f"📊 Enhanced Summary:")
        print(f"   Total Findings: {summary['total_findings']}")
        print(f"   Failed: {summary['failed_count']}")
        print(f"   Actionable: {summary['actionable_count']}")
        print(f"   By Severity: {summary['by_severity']}")
        print(f"   By Target Type: {summary['by_target_type']}")
        
        # Show enhanced findings
        print(f"\n📋 Sample Enhanced Findings:")
        for i, finding in enumerate(findings[:3]):
            print(f"\n   Finding {i+1}:")
            print(f"     ID: {finding.rule_id}")
            print(f"     Severity: {finding.severity}")
            print(f"     Status: {finding.status}")
            print(f"     Title: {finding.title[:60]}...")
            if finding.target_info:
                print(f"     Target: {finding.target_info.target_type} -> {finding.target_info.target_name}")
                print(f"     Ansible: {finding.target_info.ansible_module}")
            print(f"     Compliance: CCI={len(finding.compliance.cci_refs)}, NIST={len(finding.compliance.nist_refs)}")
        
        # Export enhanced data
        base_name = Path(file_path).stem
        # Create findings directory as peer to src directory
        script_dir = Path(__file__).parent
        output_dir = script_dir.parent / "findings"
        output_dir.mkdir(exist_ok=True)
        
        findings_file = output_dir / f"{base_name}_enhanced_findings.json"
        targets_file = output_dir / f"{base_name}_ansible_targets.json"
        
        parser.export_findings_json(str(findings_file))
        parser.export_ansible_targets(str(targets_file))
        
        print(f"\n📁 Output files created:")
        print(f"   Enhanced findings: {findings_file}")
        print(f"   Ansible targets: {targets_file}")
        
        return True
    else:
        print(f"❌ No enhanced findings extracted from {file_path}")
        return False

def test_enhanced_parser():
    """Test the enhanced STIG parser with default sample files"""
    
    # Look for sample files in multiple possible locations relative to script
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    possible_locations = [
        project_root / "xml_files" / "sample_data",
        script_dir / "xml_files" / "sample_data", 
        script_dir.parent / "xml_files" / "sample_data",
        script_dir / "sample_data",
        project_root / "sample_data"
    ]
    
    sample_files = [
        "node2.example.com-STIG-20250710162433.xml",
        "node2.example.com-PCI-20250710162255.xml"
    ]
    
    found_files = []
    for location in possible_locations:
        for sample_file in sample_files:
            full_path = location / sample_file
            if full_path.exists():
                found_files.append(str(full_path))
                break
    
    if not found_files:
        print("❌ No sample files found for testing")
        print("📍 Searched in locations:")
        for location in possible_locations:
            print(f"   {location.resolve()}")
        return False
    
    success = True
    for file_path in found_files:
        if not process_stig_file(file_path):
            success = False
    
    return success

if __name__ == "__main__":
    print("🚀 Enhanced STIG Parser with Complete Extraction")
    print("=" * 60)
    
    # Check if file path provided as command line argument
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print(f"📂 Processing file: {file_path}")
        success = process_stig_file(file_path)
    else:
        print("🧪 Running in test mode (no file specified)")
        success = test_enhanced_parser()
    
    if success:
        print("\n✅ Enhanced STIG parser completed successfully!")
        print("📝 Check the findings/ directory for enhanced JSON exports")
    else:
        print("\n❌ Enhanced STIG parser failed!")
        print("\n💡 Usage:")
        print(f"   python {Path(__file__).name} <path_to_stig_file.xml>")
        print("   or")
        print(f"   python {Path(__file__).name}  # for test mode")