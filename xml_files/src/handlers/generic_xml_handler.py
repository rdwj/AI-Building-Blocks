#!/usr/bin/env python3
"""
Generic XML Handler

Fallback handler for processing any XML document type when no specialized
handler is available. Provides general-purpose XML analysis and structure
detection capabilities.

This handler serves as the default option and performs basic XML document
analysis including structure analysis, pattern detection, and data extraction.
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Tuple
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer import XMLHandler, DocumentTypeInfo, SpecializedAnalysis


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