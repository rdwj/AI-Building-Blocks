#!/usr/bin/env python3
"""
XML Specialized Handlers System

This module provides a flexible framework for detecting and handling different XML document types.
Each handler provides specialized analysis and extraction logic for its document type.

Key features:
- Automatic document type detection
- Pluggable handler architecture
- Type-specific analysis and insights
- Standardized output format
"""

import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Type, Tuple
from dataclasses import dataclass, field
import re
from pathlib import Path
import json

@dataclass
class DocumentTypeInfo:
    """Information about a detected document type"""
    type_name: str
    confidence: float  # 0.0 to 1.0
    version: Optional[str] = None
    schema_uri: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SpecializedAnalysis:
    """Results from specialized handler analysis"""
    document_type: str
    key_findings: Dict[str, Any]
    recommendations: List[str]
    data_inventory: Dict[str, int]  # What types of data found and counts
    ai_use_cases: List[str]  # Potential AI/ML applications
    structured_data: Dict[str, Any]  # Extracted structured data
    quality_metrics: Dict[str, float]  # Data quality indicators

class XMLHandler(ABC):
    """Abstract base class for XML document handlers"""
    
    @abstractmethod
    def can_handle(self, root: ET.Element, namespaces: Dict[str, str]) -> Tuple[bool, float]:
        """
        Check if this handler can process the document
        Returns: (can_handle: bool, confidence: float)
        """
        pass
    
    @abstractmethod
    def detect_type(self, root: ET.Element, namespaces: Dict[str, str]) -> DocumentTypeInfo:
        """Detect specific document type and version"""
        pass
    
    @abstractmethod
    def analyze(self, root: ET.Element, file_path: str) -> SpecializedAnalysis:
        """Perform specialized analysis on the document"""
        pass
    
    @abstractmethod
    def extract_key_data(self, root: ET.Element) -> Dict[str, Any]:
        """Extract the most important data from this document type"""
        pass

class SCAPHandler(XMLHandler):
    """Handler for SCAP (Security Content Automation Protocol) documents"""
    
    def can_handle(self, root: ET.Element, namespaces: Dict[str, str]) -> Tuple[bool, float]:
        # Check for SCAP-specific namespaces and elements
        scap_indicators = [
            'http://scap.nist.gov/schema/',
            'asset-report-collection',
            'data-stream-collection',
            'xccdf',
            'oval'
        ]
        
        score = 0.0
        if any(uri in str(namespaces.values()) for uri in scap_indicators[:1]):
            score += 0.5
        if root.tag.endswith('asset-report-collection'):
            score += 0.3
        if 'xccdf' in str(namespaces.values()).lower():
            score += 0.2
            
        return score > 0.5, score
    
    def detect_type(self, root: ET.Element, namespaces: Dict[str, str]) -> DocumentTypeInfo:
        version = None
        schema_uri = None
        
        # Extract version from namespaces
        for prefix, uri in namespaces.items():
            if 'scap.nist.gov' in uri:
                schema_uri = uri
                # Extract version from URI if present
                version_match = re.search(r'/(\d+\.\d+)/?$', uri)
                if version_match:
                    version = version_match.group(1)
        
        return DocumentTypeInfo(
            type_name="SCAP Security Report",
            confidence=0.9,
            version=version,
            schema_uri=schema_uri,
            metadata={
                "standard": "NIST SCAP",
                "category": "security_compliance"
            }
        )
    
    def analyze(self, root: ET.Element, file_path: str) -> SpecializedAnalysis:
        findings = {}
        data_inventory = {}
        
        # Analyze SCAP-specific elements
        # Count security rules
        rules = root.findall('.//*[@id]')
        findings['total_rules'] = len(rules)
        
        # Count vulnerabilities/findings
        findings['vulnerabilities'] = self._count_vulnerabilities(root)
        
        # Extract compliance status
        findings['compliance_summary'] = self._extract_compliance_summary(root)
        
        recommendations = [
            "Use for automated compliance monitoring",
            "Extract failed rules for remediation workflows",
            "Trend analysis on compliance scores over time",
            "Risk scoring based on vulnerability severity"
        ]
        
        ai_use_cases = [
            "Automated compliance report generation",
            "Predictive risk analysis",
            "Remediation recommendation engine",
            "Compliance trend forecasting",
            "Security posture classification"
        ]
        
        return SpecializedAnalysis(
            document_type="SCAP Security Report",
            key_findings=findings,
            recommendations=recommendations,
            data_inventory=data_inventory,
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_key_data(root),
            quality_metrics=self._calculate_quality_metrics(root)
        )
    
    def extract_key_data(self, root: ET.Element) -> Dict[str, Any]:
        # Extract key SCAP data
        return {
            "scan_results": self._extract_scan_results(root),
            "system_info": self._extract_system_info(root),
            "compliance_scores": self._extract_compliance_scores(root)
        }
    
    def _count_vulnerabilities(self, root: ET.Element) -> Dict[str, int]:
        # Implementation for counting vulnerabilities by severity
        return {"high": 0, "medium": 0, "low": 0}
    
    def _extract_compliance_summary(self, root: ET.Element) -> Dict[str, Any]:
        # Implementation for extracting compliance summary
        return {}
    
    def _extract_scan_results(self, root: ET.Element) -> List[Dict[str, Any]]:
        # Implementation for extracting scan results
        return []
    
    def _extract_system_info(self, root: ET.Element) -> Dict[str, Any]:
        # Implementation for extracting system information
        return {}
    
    def _extract_compliance_scores(self, root: ET.Element) -> Dict[str, float]:
        # Implementation for extracting compliance scores
        return {}
    
    def _calculate_quality_metrics(self, root: ET.Element) -> Dict[str, float]:
        return {
            "completeness": 0.85,
            "consistency": 0.90,
            "data_density": 0.75
        }

class RSSHandler(XMLHandler):
    """Handler for RSS feed documents"""
    
    def can_handle(self, root: ET.Element, namespaces: Dict[str, str]) -> Tuple[bool, float]:
        if root.tag == 'rss' or root.tag.endswith('}rss'):
            return True, 1.0
        if root.tag == 'feed':  # Atom feeds
            return True, 0.9
        return False, 0.0
    
    def detect_type(self, root: ET.Element, namespaces: Dict[str, str]) -> DocumentTypeInfo:
        version = root.get('version', '2.0')
        feed_type = 'RSS' if root.tag.endswith('rss') else 'Atom'
        
        return DocumentTypeInfo(
            type_name=f"{feed_type} Feed",
            confidence=1.0,
            version=version,
            metadata={
                "standard": feed_type,
                "category": "content_syndication"
            }
        )
    
    def analyze(self, root: ET.Element, file_path: str) -> SpecializedAnalysis:
        channel = root.find('.//channel') or root
        items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
        
        findings = {
            'total_items': len(items),
            'has_descriptions': sum(1 for item in items if item.find('.//description') is not None),
            'has_dates': sum(1 for item in items if item.find('.//pubDate') is not None),
            'categories': self._extract_categories(items)
        }
        
        recommendations = [
            "Use for content aggregation and analysis",
            "Extract for trend analysis and topic modeling",
            "Monitor for content updates and changes"
        ]
        
        ai_use_cases = [
            "Content categorization and tagging",
            "Trend detection and analysis",
            "Sentiment analysis on articles",
            "Topic modeling and clustering",
            "Content recommendation systems"
        ]
        
        return SpecializedAnalysis(
            document_type="RSS/Atom Feed",
            key_findings=findings,
            recommendations=recommendations,
            data_inventory={'articles': len(items), 'categories': len(findings['categories'])},
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_key_data(root),
            quality_metrics=self._calculate_feed_quality(root, items)
        )
    
    def extract_key_data(self, root: ET.Element) -> Dict[str, Any]:
        items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
        
        return {
            'feed_metadata': self._extract_feed_metadata(root),
            'items': [self._extract_item_data(item) for item in items[:10]]  # First 10 items
        }
    
    def _extract_categories(self, items) -> List[str]:
        categories = set()
        for item in items:
            for cat in item.findall('.//category'):
                if cat.text:
                    categories.add(cat.text)
        return list(categories)
    
    def _extract_feed_metadata(self, root: ET.Element) -> Dict[str, Any]:
        channel = root.find('.//channel') or root
        return {
            'title': getattr(channel.find('.//title'), 'text', None),
            'description': getattr(channel.find('.//description'), 'text', None),
            'link': getattr(channel.find('.//link'), 'text', None)
        }
    
    def _extract_item_data(self, item: ET.Element) -> Dict[str, Any]:
        return {
            'title': getattr(item.find('.//title'), 'text', None),
            'description': getattr(item.find('.//description'), 'text', None),
            'pubDate': getattr(item.find('.//pubDate'), 'text', None),
            'link': getattr(item.find('.//link'), 'text', None)
        }
    
    def _calculate_feed_quality(self, root: ET.Element, items: List[ET.Element]) -> Dict[str, float]:
        total = len(items)
        if total == 0:
            return {"completeness": 0.0, "consistency": 0.0, "data_density": 0.0}
        
        with_desc = sum(1 for item in items if item.find('.//description') is not None)
        with_date = sum(1 for item in items if item.find('.//pubDate') is not None)
        
        return {
            "completeness": (with_desc + with_date) / (2 * total),
            "consistency": 1.0 if with_desc == total else with_desc / total,
            "data_density": 0.8  # Typical for RSS feeds
        }

class SVGHandler(XMLHandler):
    """Handler for SVG (Scalable Vector Graphics) documents"""
    
    def can_handle(self, root: ET.Element, namespaces: Dict[str, str]) -> Tuple[bool, float]:
        if root.tag == '{http://www.w3.org/2000/svg}svg' or root.tag == 'svg':
            return True, 1.0
        return False, 0.0
    
    def detect_type(self, root: ET.Element, namespaces: Dict[str, str]) -> DocumentTypeInfo:
        return DocumentTypeInfo(
            type_name="SVG Graphics",
            confidence=1.0,
            version=root.get('version', '1.1'),
            schema_uri="http://www.w3.org/2000/svg",
            metadata={
                "standard": "W3C SVG",
                "category": "graphics"
            }
        )
    
    def analyze(self, root: ET.Element, file_path: str) -> SpecializedAnalysis:
        findings = {
            'dimensions': {
                'width': root.get('width'),
                'height': root.get('height'),
                'viewBox': root.get('viewBox')
            },
            'element_types': self._count_svg_elements(root),
            'has_animations': self._check_animations(root),
            'has_scripts': len(root.findall('.//script')) > 0,
            'complexity_score': self._calculate_complexity(root)
        }
        
        recommendations = [
            "Extract for design system documentation",
            "Analyze for accessibility improvements",
            "Convert to other formats for broader compatibility"
        ]
        
        ai_use_cases = [
            "Automatic icon/graphic classification",
            "Design pattern recognition",
            "Accessibility analysis",
            "Style extraction for design systems",
            "Vector graphic optimization"
        ]
        
        return SpecializedAnalysis(
            document_type="SVG Graphics",
            key_findings=findings,
            recommendations=recommendations,
            data_inventory=findings['element_types'],
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_key_data(root),
            quality_metrics=self._calculate_svg_quality(root)
        )
    
    def extract_key_data(self, root: ET.Element) -> Dict[str, Any]:
        return {
            'metadata': self._extract_svg_metadata(root),
            'structure': self._extract_structure(root),
            'styles': self._extract_styles(root)
        }
    
    def _count_svg_elements(self, root: ET.Element) -> Dict[str, int]:
        elements = {}
        for elem in root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            elements[tag] = elements.get(tag, 0) + 1
        return elements
    
    def _check_animations(self, root: ET.Element) -> bool:
        animation_tags = ['animate', 'animateTransform', 'animateMotion', 'set']
        # Extract namespace from root tag if present
        namespace = root.tag.split("}")[0][1:] if "}" in root.tag else ""
        for tag in animation_tags:
            search_path = f'.//{{{namespace}}}{tag}' if namespace else f'.//{tag}'
            if root.find(search_path) is not None:
                return True
        return False
    
    def _calculate_complexity(self, root: ET.Element) -> float:
        total_elements = len(list(root.iter()))
        return min(total_elements / 100.0, 1.0)
    
    def _extract_svg_metadata(self, root: ET.Element) -> Dict[str, Any]:
        metadata = {}
        for elem in root:
            if elem.tag.endswith('metadata'):
                # Extract metadata content
                pass
        return metadata
    
    def _extract_structure(self, root: ET.Element) -> Dict[str, Any]:
        return {
            'groups': len(root.findall('.//g')),
            'paths': len(root.findall('.//path')),
            'max_depth': self._calculate_max_depth(root)
        }
    
    def _extract_styles(self, root: ET.Element) -> Dict[str, Any]:
        return {
            'inline_styles': len([e for e in root.iter() if e.get('style')]),
            'classes': len(set(e.get('class', '') for e in root.iter() if e.get('class')))
        }
    
    def _calculate_max_depth(self, elem: ET.Element, depth: int = 0) -> int:
        if not list(elem):
            return depth
        return max(self._calculate_max_depth(child, depth + 1) for child in elem)
    
    def _calculate_svg_quality(self, root: ET.Element) -> Dict[str, float]:
        has_viewbox = 1.0 if root.get('viewBox') else 0.0
        has_title = 1.0 if root.find('.//title') is not None else 0.0
        
        return {
            "completeness": (has_viewbox + has_title) / 2,
            "accessibility": has_title,
            "scalability": has_viewbox
        }

class GenericXMLHandler(XMLHandler):
    """Fallback handler for generic XML documents"""
    
    def can_handle(self, root: ET.Element, namespaces: Dict[str, str]) -> Tuple[bool, float]:
        # This handler can handle any XML
        return True, 0.1  # Low confidence as it's a fallback
    
    def detect_type(self, root: ET.Element, namespaces: Dict[str, str]) -> DocumentTypeInfo:
        # Try to infer type from root element and namespaces
        root_tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag
        
        return DocumentTypeInfo(
            type_name=f"Generic XML ({root_tag})",
            confidence=0.5,
            metadata={
                "root_element": root_tag,
                "namespace_count": len(namespaces)
            }
        )
    
    def analyze(self, root: ET.Element, file_path: str) -> SpecializedAnalysis:
        findings = {
            'structure': self._analyze_structure(root),
            'data_patterns': self._detect_patterns(root),
            'attribute_usage': self._analyze_attributes(root)
        }
        
        recommendations = [
            "Review structure for data extraction opportunities",
            "Consider creating a specialized handler for this document type",
            "Analyze repeating patterns for structured data extraction"
        ]
        
        ai_use_cases = [
            "Schema learning and validation",
            "Data extraction and transformation",
            "Pattern recognition",
            "Anomaly detection in structure"
        ]
        
        return SpecializedAnalysis(
            document_type="Generic XML",
            key_findings=findings,
            recommendations=recommendations,
            data_inventory=self._inventory_data(root),
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_key_data(root),
            quality_metrics=self._analyze_quality(root)
        )
    
    def extract_key_data(self, root: ET.Element) -> Dict[str, Any]:
        return {
            'sample_data': self._extract_samples(root),
            'schema_inference': self._infer_schema(root)
        }
    
    def _analyze_structure(self, root: ET.Element) -> Dict[str, Any]:
        return {
            'max_depth': self._calculate_depth(root),
            'element_count': len(list(root.iter())),
            'unique_paths': len(self._get_unique_paths(root))
        }
    
    def _detect_patterns(self, root: ET.Element) -> Dict[str, Any]:
        # Detect repeating structures
        element_counts = {}
        for elem in root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            element_counts[tag] = element_counts.get(tag, 0) + 1
        
        return {
            'repeating_elements': {k: v for k, v in element_counts.items() if v > 5},
            'likely_records': [k for k, v in element_counts.items() if v > 10]
        }
    
    def _analyze_attributes(self, root: ET.Element) -> Dict[str, Any]:
        attr_usage = {}
        for elem in root.iter():
            for attr in elem.attrib:
                attr_usage[attr] = attr_usage.get(attr, 0) + 1
        return attr_usage
    
    def _inventory_data(self, root: ET.Element) -> Dict[str, int]:
        inventory = {}
        for elem in root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            inventory[tag] = inventory.get(tag, 0) + 1
        return inventory
    
    def _extract_samples(self, root: ET.Element, max_samples: int = 5) -> List[Dict[str, Any]]:
        samples = []
        for i, elem in enumerate(root.iter()):
            if i >= max_samples:
                break
            if elem.text and elem.text.strip():
                samples.append({
                    'path': self._get_path(elem),
                    'tag': elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag,
                    'text': elem.text.strip()[:100],
                    'attributes': dict(elem.attrib)
                })
        return samples
    
    def _infer_schema(self, root: ET.Element) -> Dict[str, Any]:
        # Basic schema inference
        return {
            'probable_record_types': self._detect_patterns(root)['likely_records'],
            'hierarchical': self._calculate_depth(root) > 3
        }
    
    def _calculate_depth(self, elem: ET.Element, depth: int = 0) -> int:
        if not list(elem):
            return depth
        return max(self._calculate_depth(child, depth + 1) for child in elem)
    
    def _get_unique_paths(self, root: ET.Element) -> set:
        paths = set()
        
        def traverse(elem, path):
            current_path = f"{path}/{elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag}"
            paths.add(current_path)
            for child in elem:
                traverse(child, current_path)
        
        traverse(root, "")
        return paths
    
    def _get_path(self, elem: ET.Element) -> str:
        # Simple path extraction (would need more complex logic for full path)
        return elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
    
    def _analyze_quality(self, root: ET.Element) -> Dict[str, float]:
        total_elements = len(list(root.iter()))
        elements_with_text = sum(1 for e in root.iter() if e.text and e.text.strip())
        elements_with_attrs = sum(1 for e in root.iter() if e.attrib)
        
        return {
            "data_density": elements_with_text / total_elements if total_elements > 0 else 0,
            "attribute_usage": elements_with_attrs / total_elements if total_elements > 0 else 0,
            "structure_consistency": 0.7  # Would need more analysis
        }

class XMLDocumentAnalyzer:
    """Main analyzer that uses specialized handlers"""
    
    def __init__(self):
        # Use the new centralized handler registry
        try:
            from handlers import ALL_HANDLERS
            # Instantiate all handlers from the registry
            self.handlers = [handler_class() for handler_class in ALL_HANDLERS]
            print(f"🔄 Using new handler registry with {len(self.handlers)} handlers")
        except ImportError:
            # Fallback to old method if registry not available
            print("⚠️  Handler registry not available, using legacy handler loading")
            self.handlers: List[Type[XMLHandler]] = [
                SCAPHandler(),
                RSSHandler(),
                SVGHandler(),
                # Add more handlers here as needed
                GenericXMLHandler()  # Always last as fallback
            ]
            
            # Try to import additional handlers
            try:
                from additional_xml_handlers import (
                    MavenPOMHandler, Log4jConfigHandler, SpringConfigHandler,
                    DocBookHandler, SitemapHandler
                )
                # Insert before GenericXMLHandler
                self.handlers.insert(-1, MavenPOMHandler())
                self.handlers.insert(-1, Log4jConfigHandler())
                self.handlers.insert(-1, SpringConfigHandler())
                self.handlers.insert(-1, DocBookHandler())
                self.handlers.insert(-1, SitemapHandler())
            except ImportError:
                # Additional handlers not available
                pass
    
    def analyze_document(self, file_path: str) -> Dict[str, Any]:
        """Analyze an XML document using the appropriate handler"""
        
        # Parse the document
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            return {
                "error": f"Failed to parse XML: {e}",
                "file_path": file_path
            }
        
        # Extract namespaces
        namespaces = self._extract_namespaces(root)
        
        # Find the best handler
        best_handler = None
        best_confidence = 0.0
        
        for handler in self.handlers:
            can_handle, confidence = handler.can_handle(root, namespaces)
            if can_handle and confidence > best_confidence:
                best_handler = handler
                best_confidence = confidence
        
        if not best_handler:
            best_handler = self.handlers[-1]  # Use generic handler
        
        # Detect document type
        doc_type = best_handler.detect_type(root, namespaces)
        
        # Perform specialized analysis
        analysis = best_handler.analyze(root, file_path)
        
        # Combine results
        return {
            "file_path": file_path,
            "document_type": doc_type,
            "handler_used": best_handler.__class__.__name__,
            "confidence": best_confidence,
            "analysis": analysis,
            "namespaces": namespaces,
            "file_size": Path(file_path).stat().st_size
        }
    
    def _extract_namespaces(self, root: ET.Element) -> Dict[str, str]:
        """Extract all namespaces from the document"""
        namespaces = {}
        
        # Get namespaces from root element
        for key, value in root.attrib.items():
            if key.startswith('xmlns'):
                prefix = key.split(':')[1] if ':' in key else 'default'
                namespaces[prefix] = value
        
        # Also check for namespaces in element tags
        for elem in root.iter():
            if '}' in elem.tag:
                uri = elem.tag.split('}')[0][1:]
                # Try to find a prefix for this URI
                prefix = None
                for p, u in namespaces.items():
                    if u == uri:
                        prefix = p
                        break
                if not prefix:
                    prefix = f"ns{len(namespaces)}"
                    namespaces[prefix] = uri
        
        return namespaces

# Example usage
if __name__ == "__main__":
    analyzer = XMLDocumentAnalyzer()
    
    # Example: Analyze a file
    result = analyzer.analyze_document("sample_data/example.xml")
    
    print(json.dumps(result, indent=2, default=str))
