#!/usr/bin/env python3
"""
XML Schema Analyzer for LLM Agent Framework

This tool deterministically analyzes XML files to extract:
1. Document structure and hierarchy
2. Element patterns and frequencies
3. Attribute schemas
4. Namespace information
5. Sample data for semantic understanding
6. Compact schema description for LLM consumption

Designed to handle large XML files efficiently.
"""

import xml.etree.ElementTree as ET
from collections import defaultdict, Counter
import json
import re
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, asdict
import itertools

@dataclass
class ElementInfo:
    """Information about an XML element"""
    tag: str
    count: int
    depth_levels: Set[int]
    attributes: Dict[str, Set[str]]  # attr_name -> set of observed values
    text_patterns: List[str]  # Sample text content
    parent_elements: Set[str]
    child_elements: Set[str]

@dataclass
class XMLSchema:
    """Complete XML schema information"""
    root_element: str
    namespaces: Dict[str, str]
    elements: Dict[str, ElementInfo]
    max_depth: int
    total_elements: int
    structure_tree: Dict[str, Any]
    sample_paths: List[str]

class XMLSchemaAnalyzer:
    def __init__(self, max_samples=5, max_text_length=100):
        self.max_samples = max_samples
        self.max_text_length = max_text_length
        self.elements = defaultdict(lambda: ElementInfo(
            tag="", count=0, depth_levels=set(), attributes=defaultdict(set),
            text_patterns=[], parent_elements=set(), child_elements=set()
        ))
        self.namespaces = {}
        self.structure_tree = {}
        self.sample_paths = []
        self.max_depth = 0

    def clean_tag(self, tag: str) -> str:
        """Remove namespace prefix from tag for cleaner analysis"""
        return tag.split('}')[-1] if '}' in tag else tag

    def get_namespace(self, tag: str) -> Optional[str]:
        """Extract namespace from tag"""
        if '}' in tag:
            return tag.split('}')[0][1:]  # Remove leading {
        return None

    def analyze_element(self, elem, depth=0, parent_tag=None, path=""):
        """Recursively analyze XML element"""
        self.max_depth = max(self.max_depth, depth)
        
        # Clean tag name
        clean_tag = self.clean_tag(elem.tag)
        full_path = f"{path}/{clean_tag}" if path else clean_tag
        
        # Store namespace info
        ns = self.get_namespace(elem.tag)
        if ns and ns not in self.namespaces:
            # Try to find prefix in element's namespace declarations
            for key, value in elem.attrib.items():
                if value == ns and key.startswith('xmlns:'):
                    self.namespaces[key[6:]] = ns
                elif key == 'xmlns' and value == ns:
                    self.namespaces['default'] = ns

        # Update element info
        element_info = self.elements[clean_tag]
        element_info.tag = clean_tag
        element_info.count += 1
        element_info.depth_levels.add(depth)
        
        # Add parent relationship
        if parent_tag:
            element_info.parent_elements.add(parent_tag)
            self.elements[parent_tag].child_elements.add(clean_tag)

        # Analyze attributes
        for attr_name, attr_value in elem.attrib.items():
            clean_attr = self.clean_tag(attr_name)
            element_info.attributes[clean_attr].add(attr_value[:50])  # Limit attr value length

        # Analyze text content
        if elem.text and elem.text.strip():
            text = elem.text.strip()[:self.max_text_length]
            if len(element_info.text_patterns) < self.max_samples:
                element_info.text_patterns.append(text)

        # Sample some interesting paths for LLM context
        if depth <= 3 and len(self.sample_paths) < 20:
            self.sample_paths.append(full_path)

        # Recursively analyze children
        for child in elem:
            self.analyze_element(child, depth + 1, clean_tag, full_path)

    def build_structure_tree(self) -> Dict[str, Any]:
        """Build hierarchical structure representation"""
        tree = {}
        
        for tag, info in self.elements.items():
            if not info.parent_elements:  # Root elements
                tree[tag] = self._build_subtree(tag)
        
        return tree

    def _build_subtree(self, tag: str) -> Dict[str, Any]:
        """Recursively build structure subtree"""
        info = self.elements[tag]
        node = {
            "count": info.count,
            "attributes": {k: f"{len(v)} unique values" for k, v in info.attributes.items()},
            "has_text": len(info.text_patterns) > 0,
            "children": {}
        }
        
        for child_tag in info.child_elements:
            node["children"][child_tag] = self._build_subtree(child_tag)
        
        return node

    def analyze_file(self, file_path: str) -> XMLSchema:
        """Analyze XML file and return schema information"""
        print(f"Analyzing XML file: {file_path}")
        
        # Parse XML iteratively for large files
        context = ET.iterparse(file_path, events=('start', 'end', 'start-ns'))
        
        root = None
        namespace_stack = [{}]
        
        for event, elem in context:
            if event == 'start-ns':
                # Handle namespace declarations
                prefix, uri = elem
                self.namespaces[prefix or 'default'] = uri
                namespace_stack[-1][prefix or 'default'] = uri
            
            elif event == 'start':
                if root is None:
                    root = elem
                    self.analyze_element(elem)
                    break  # Only analyze from root
        
        # Build structure tree
        self.structure_tree = self.build_structure_tree()
        
        # Convert elements dict for serialization
        elements_dict = {}
        for tag, info in self.elements.items():
            elements_dict[tag] = ElementInfo(
                tag=info.tag,
                count=info.count,
                depth_levels=sorted(info.depth_levels),
                attributes={k: list(v)[:5] for k, v in info.attributes.items()},  # Limit samples
                text_patterns=info.text_patterns[:3],  # Limit samples
                parent_elements=list(info.parent_elements),
                child_elements=list(info.child_elements)
            )

        return XMLSchema(
            root_element=self.clean_tag(root.tag) if root is not None else "",
            namespaces=self.namespaces,
            elements=elements_dict,
            max_depth=self.max_depth,
            total_elements=sum(info.count for info in self.elements.values()),
            structure_tree=self.structure_tree,
            sample_paths=self.sample_paths
        )

    def generate_llm_description(self, schema: XMLSchema) -> str:
        """Generate a concise description suitable for LLM consumption"""
        description = f"""XML Document Schema Analysis

Document Type: {schema.root_element}
Total Elements: {schema.total_elements:,}
Maximum Depth: {schema.max_depth}
Unique Element Types: {len(schema.elements)}

NAMESPACES:
{json.dumps(schema.namespaces, indent=2)}

DOCUMENT STRUCTURE:
Root: {schema.root_element}
Sample Paths: {', '.join(schema.sample_paths[:10])}

KEY ELEMENTS (Top 10 by frequency):
"""
        
        # Sort elements by count
        sorted_elements = sorted(schema.elements.items(), 
                               key=lambda x: x[1].count, reverse=True)[:10]
        
        for tag, info in sorted_elements:
            attrs_summary = f"[{len(info.attributes)} attrs]" if info.attributes else "[no attrs]"
            text_summary = "[has text]" if info.text_patterns else "[no text]"
            children_summary = f"[{len(info.child_elements)} children]" if info.child_elements else "[leaf]"
            
            description += f"\n- {tag}: {info.count:,} occurrences, depths {info.depth_levels} {attrs_summary} {text_summary} {children_summary}"
            
            # Show key attributes
            if info.attributes:
                key_attrs = list(info.attributes.keys())[:3]
                description += f"\n  Key attributes: {', '.join(key_attrs)}"
            
            # Show sample text
            if info.text_patterns:
                sample_text = info.text_patterns[0][:50]
                description += f"\n  Sample text: \"{sample_text}...\""

        description += f"\n\nHIERARCHICAL STRUCTURE:\n{json.dumps(schema.structure_tree, indent=2)}"
        
        return description

def analyze_xml_file(file_path: str, output_json: bool = False) -> str:
    """Main function to analyze XML file"""
    analyzer = XMLSchemaAnalyzer()
    schema = analyzer.analyze_file(file_path)
    
    if output_json:
        # Convert to dict for JSON serialization
        schema_dict = asdict(schema)
        # Convert sets to lists for JSON
        for element_info in schema_dict['elements'].values():
            element_info['depth_levels'] = list(element_info['depth_levels'])
            element_info['parent_elements'] = list(element_info['parent_elements'])
            element_info['child_elements'] = list(element_info['child_elements'])
            for attr_name in element_info['attributes']:
                element_info['attributes'][attr_name] = list(element_info['attributes'][attr_name])
        
        return json.dumps(schema_dict, indent=2)
    else:
        return analyzer.generate_llm_description(schema)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python xml_analyzer.py <xml_file> [--json]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_json = "--json" in sys.argv
    
    try:
        result = analyze_xml_file(file_path, output_json)
        print(result)
    except Exception as e:
        print(f"Error analyzing XML file: {e}")
        sys.exit(1)