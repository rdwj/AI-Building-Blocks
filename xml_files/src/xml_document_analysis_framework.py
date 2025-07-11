#!/usr/bin/env python3
"""
XML Document Analysis Framework for LLM Agents

This framework provides a complete solution for analyzing XML documents and preparing
them for LLM-based processing. It includes:

1. Deterministic schema extraction
2. Chunking strategies for large files
3. LLM prompt templates for semantic understanding
4. Document type detection and specialized handlers
5. Incremental processing for memory-efficient analysis

Usage:
    framework = XMLAgentFramework()
    analysis = framework.analyze_document("path/to/file.xml")
    chunks = framework.chunk_document("path/to/file.xml", analysis)
    llm_prompts = framework.generate_llm_prompts(analysis, chunks)
"""

import xml.etree.ElementTree as ET
from xml.sax import make_parser, ContentHandler
from collections import defaultdict, Counter
import json
import re
import hashlib
from typing import Dict, List, Set, Any, Optional, Generator, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

@dataclass
class XMLElement:
    """Represents an XML element with all its metadata"""
    tag: str
    namespace: Optional[str]
    count: int
    depths: Set[int]
    attributes: Dict[str, Set[str]]
    text_samples: List[str]
    parent_elements: Set[str]
    child_elements: Set[str]
    paths: Set[str]
    line_numbers: List[int]

@dataclass
class DocumentSchema:
    """Complete document schema analysis"""
    document_type: str
    root_element: str
    namespaces: Dict[str, str]
    elements: Dict[str, XMLElement]
    structure_tree: Dict[str, Any]
    statistics: Dict[str, Any]
    specialized_info: Dict[str, Any]

@dataclass
class DocumentChunk:
    """A chunk of XML document for LLM processing"""
    chunk_id: str
    content: str
    element_path: str
    line_range: Tuple[int, int]
    size_bytes: int
    elements_contained: List[str]
    summary: str

class XMLStreamHandler(ContentHandler):
    """SAX handler for memory-efficient XML analysis"""
    
    def __init__(self, max_samples=5, max_text_length=200):
        super().__init__()
        self.elements = defaultdict(lambda: XMLElement(
            tag="", namespace=None, count=0, depths=set(), attributes=defaultdict(set),
            text_samples=[], parent_elements=set(), child_elements=set(),
            paths=set(), line_numbers=[]
        ))
        self.namespaces = {}
        self.element_stack = []
        self.path_stack = []
        self.current_text = ""
        self.max_samples = max_samples
        self.max_text_length = max_text_length
        self.line_number = 1
        
    def startNamespace(self, prefix, uri):
        if prefix:
            self.namespaces[prefix] = uri
        else:
            self.namespaces['default'] = uri
    
    def startElement(self, name, attrs):
        # Parse namespace and local name
        if ':' in name:
            namespace, local_name = name.split(':', 1)
        else:
            namespace, local_name = None, name
            
        # Update element info
        element_info = self.elements[local_name]
        element_info.tag = local_name
        element_info.namespace = namespace
        element_info.count += 1
        element_info.depths.add(len(self.element_stack))
        element_info.line_numbers.append(self.line_number)
        
        # Track path
        current_path = '/'.join(self.path_stack + [local_name])
        element_info.paths.add(current_path)
        
        # Parent-child relationships
        if self.element_stack:
            parent_tag = self.element_stack[-1]
            element_info.parent_elements.add(parent_tag)
            self.elements[parent_tag].child_elements.add(local_name)
        
        # Store attributes
        for attr_name in attrs.getNames():
            attr_value = attrs.getValue(attr_name)
            clean_attr = attr_name.split(':')[-1]  # Remove namespace prefix
            element_info.attributes[clean_attr].add(attr_value[:50])  # Limit length
        
        self.element_stack.append(local_name)
        self.path_stack.append(local_name)
        self.current_text = ""
    
    def endElement(self, name):
        local_name = name.split(':', 1)[-1] if ':' in name else name
        
        # Store text content if any
        if self.current_text.strip() and local_name in self.elements:
            element_info = self.elements[local_name]
            if len(element_info.text_samples) < self.max_samples:
                text = self.current_text.strip()[:self.max_text_length]
                element_info.text_samples.append(text)
        
        if self.element_stack:
            self.element_stack.pop()
        if self.path_stack:
            self.path_stack.pop()
        self.current_text = ""
    
    def characters(self, content):
        self.current_text += content
        # Count line numbers
        self.line_number += content.count('\n')

class DocumentTypeDetector:
    """Detects and classifies XML document types"""
    
    DOCUMENT_PATTERNS = {
        'SCAP': {
            'root_elements': ['asset-report-collection', 'data-stream-collection'],
            'namespaces': ['http://scap.nist.gov', 'http://checklists.nist.gov/xccdf'],
            'description': 'Security Content Automation Protocol document'
        },
        'XCCDF': {
            'root_elements': ['Benchmark'],
            'namespaces': ['http://checklists.nist.gov/xccdf'],
            'description': 'Extensible Configuration Checklist Description Format'
        },
        'OVAL': {
            'root_elements': ['oval_definitions', 'oval_results'],
            'namespaces': ['http://oval.mitre.org/XMLSchema'],
            'description': 'Open Vulnerability and Assessment Language'
        },
        'SOAP': {
            'root_elements': ['Envelope'],
            'namespaces': ['http://schemas.xmlsoap.org/soap'],
            'description': 'SOAP web service message'
        },
        'XML_SCHEMA': {
            'root_elements': ['schema'],
            'namespaces': ['http://www.w3.org/2001/XMLSchema'],
            'description': 'XML Schema Definition'
        },
        'RSS': {
            'root_elements': ['rss', 'feed'],
            'namespaces': ['http://www.w3.org/2005/Atom'],
            'description': 'RSS/Atom feed'
        },
        'SVG': {
            'root_elements': ['svg'],
            'namespaces': ['http://www.w3.org/2000/svg'],
            'description': 'Scalable Vector Graphics'
        },
        'WSDL': {
            'root_elements': ['definitions'],
            'namespaces': ['http://schemas.xmlsoap.org/wsdl'],
            'description': 'Web Services Description Language'
        }
    }
    
    @classmethod
    def detect_type(cls, schema: DocumentSchema) -> str:
        """Detect document type based on schema analysis"""
        for doc_type, patterns in cls.DOCUMENT_PATTERNS.items():
            # Check root element
            if schema.root_element in patterns['root_elements']:
                return doc_type
            
            # Check namespaces
            for pattern_ns in patterns['namespaces']:
                for actual_ns in schema.namespaces.values():
                    if pattern_ns in actual_ns:
                        return doc_type
        
        return 'GENERIC_XML'

class XMLChunker:
    """Chunks XML documents for LLM processing"""
    
    def __init__(self, max_chunk_size=8000, overlap_size=200):
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
    
    def chunk_by_elements(self, file_path: str, schema: DocumentSchema) -> List[DocumentChunk]:
        """Chunk document by major structural elements"""
        chunks = []
        
        # Identify major structural elements (low frequency, high child count)
        major_elements = []
        for tag, element in schema.elements.items():
            if (element.count < 100 and len(element.child_elements) > 3 and 
                min(element.depths) <= 3):
                major_elements.append(tag)
        
        if not major_elements:
            # Fallback to size-based chunking
            return self.chunk_by_size(file_path)
        
        # Parse and chunk by major elements
        current_chunk = ""
        chunk_elements = []
        line_start = 1
        
        context = ET.iterparse(file_path, events=('start', 'end'))
        
        for event, elem in context:
            tag_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            
            if event == 'start' and tag_name in major_elements:
                if current_chunk and len(current_chunk) > 1000:  # Minimum chunk size
                    chunk_id = hashlib.md5(current_chunk.encode()).hexdigest()[:8]
                    chunks.append(DocumentChunk(
                        chunk_id=chunk_id,
                        content=current_chunk,
                        element_path=f"/{'/'.join(chunk_elements)}",
                        line_range=(line_start, line_start + current_chunk.count('\n')),
                        size_bytes=len(current_chunk.encode()),
                        elements_contained=chunk_elements.copy(),
                        summary=f"Contains {len(chunk_elements)} elements including {tag_name}"
                    ))
                    current_chunk = ""
                    chunk_elements = []
                    line_start += current_chunk.count('\n')
                
                chunk_elements.append(tag_name)
            
            if len(current_chunk) < self.max_chunk_size:
                current_chunk += ET.tostring(elem, encoding='unicode') if event == 'end' else ""
        
        # Add final chunk
        if current_chunk:
            chunk_id = hashlib.md5(current_chunk.encode()).hexdigest()[:8]
            chunks.append(DocumentChunk(
                chunk_id=chunk_id,
                content=current_chunk,
                element_path=f"/{'/'.join(chunk_elements)}",
                line_range=(line_start, line_start + current_chunk.count('\n')),
                size_bytes=len(current_chunk.encode()),
                elements_contained=chunk_elements,
                summary=f"Final chunk with {len(chunk_elements)} elements"
            ))
        
        return chunks
    
    def chunk_by_size(self, file_path: str) -> List[DocumentChunk]:
        """Fallback chunking by size with XML awareness"""
        chunks = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple size-based chunking with element boundary awareness
        start = 0
        chunk_num = 0
        
        while start < len(content):
            end = min(start + self.max_chunk_size, len(content))
            
            # Try to end at element boundary
            if end < len(content):
                # Find last complete element
                last_element_end = content.rfind('</', start, end)
                if last_element_end > start + self.max_chunk_size // 2:
                    element_end = content.find('>', last_element_end)
                    if element_end != -1:
                        end = element_end + 1
            
            chunk_content = content[start:end]
            chunk_id = f"chunk_{chunk_num:03d}"
            
            chunks.append(DocumentChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                element_path="size_based",
                line_range=(content[:start].count('\n') + 1, content[:end].count('\n') + 1),
                size_bytes=len(chunk_content.encode()),
                elements_contained=[],
                summary=f"Size-based chunk {chunk_num}"
            ))
            
            start = end - self.overlap_size if end < len(content) else end
            chunk_num += 1
        
        return chunks

class LLMPromptGenerator:
    """Generates prompts for LLM analysis of XML documents"""
    
    SCHEMA_ANALYSIS_TEMPLATE = """
    Analyze this XML document schema and provide semantic understanding:

    DOCUMENT TYPE: {document_type}
    {description}

    SCHEMA OVERVIEW:
    - Root Element: {root_element}
    - Total Elements: {total_elements:,}
    - Maximum Depth: {max_depth}
    - File Size: {file_size_mb:.2f} MB

    NAMESPACES:
    {namespaces}

    KEY ELEMENTS:
    {elements_summary}

    STRUCTURAL HIERARCHY:
    {structure_tree}

    QUESTIONS FOR ANALYSIS:
    1. What is the primary purpose of this document?
    2. What are the key data entities and their relationships?
    3. What processing patterns would be most effective?
    4. What are the critical elements for data extraction?
    5. Are there any compliance or security considerations?

    Provide a comprehensive analysis addressing these questions and suggest 
    optimal strategies for automated processing of this document type.
    """
    
    CHUNK_ANALYSIS_TEMPLATE = """
    Analyze this XML document chunk in context:

    CHUNK INFO:
    - ID: {chunk_id}
    - Path: {element_path}
    - Size: {size_bytes:,} bytes
    - Line Range: {line_start}-{line_end}
    - Elements: {elements_contained}

    DOCUMENT CONTEXT:
    {document_context}

    CHUNK CONTENT:
    ```xml
    {content}
    ```

    ANALYSIS TASKS:
    1. Identify the main data entities in this chunk
    2. Extract key-value pairs and relationships
    3. Note any validation rules or constraints
    4. Identify dependencies on other document parts
    5. Suggest data extraction patterns

    Provide structured output suitable for automated processing.
    """
    
    @classmethod
    def generate_schema_prompt(cls, schema: DocumentSchema, file_size: int) -> str:
        """Generate prompt for overall schema analysis"""
        
        # Format namespaces
        ns_text = "\n".join([f"  {prefix}: {uri}" for prefix, uri in schema.namespaces.items()])
        
        # Format top elements
        sorted_elements = sorted(schema.elements.items(), 
                               key=lambda x: x[1].count, reverse=True)[:10]
        
        elements_text = ""
        for tag, element in sorted_elements:
            attrs = f"[{len(element.attributes)} attrs]" if element.attributes else "[no attrs]"
            children = f"[{len(element.child_elements)} children]" if element.child_elements else "[leaf]"
            text_info = "[has text]" if element.text_samples else "[no text]"
            
            elements_text += f"  {tag}: {element.count:,} occurrences {attrs} {children} {text_info}\n"
            
            if element.text_samples:
                sample = element.text_samples[0][:50]
                elements_text += f"    Sample: \"{sample}...\"\n"
        
        doc_type = DocumentTypeDetector.detect_type(schema)
        description = DocumentTypeDetector.DOCUMENT_PATTERNS.get(doc_type, {}).get('description', 'Unknown XML document type')
        
        return cls.SCHEMA_ANALYSIS_TEMPLATE.format(
            document_type=doc_type,
            description=description,
            root_element=schema.root_element,
            total_elements=sum(e.count for e in schema.elements.values()),
            max_depth=max(max(e.depths) for e in schema.elements.values() if e.depths),
            file_size_mb=file_size / (1024 * 1024),
            namespaces=ns_text,
            elements_summary=elements_text,
            structure_tree=json.dumps(schema.structure_tree, indent=2)
        )
    
    @classmethod
    def generate_chunk_prompt(cls, chunk: DocumentChunk, schema: DocumentSchema) -> str:
        """Generate prompt for chunk analysis"""
        
        # Create document context
        doc_type = DocumentTypeDetector.detect_type(schema)
        context = f"Document Type: {doc_type}\nRoot: {schema.root_element}\n"
        context += f"Total Elements: {len(schema.elements)}\n"
        
        return cls.CHUNK_ANALYSIS_TEMPLATE.format(
            chunk_id=chunk.chunk_id,
            element_path=chunk.element_path,
            size_bytes=chunk.size_bytes,
            line_start=chunk.line_range[0],
            line_end=chunk.line_range[1],
            elements_contained=", ".join(chunk.elements_contained),
            document_context=context,
            content=chunk.content[:6000]  # Limit content size
        )

class XMLAgentFramework:
    """Main framework class for XML document analysis"""
    
    def __init__(self, max_chunk_size=8000, max_samples=5):
        self.chunker = XMLChunker(max_chunk_size=max_chunk_size)
        self.max_samples = max_samples
        self.logger = logging.getLogger(__name__)
    
    def analyze_document(self, file_path: str) -> DocumentSchema:
        """Perform complete document analysis"""
        self.logger.info(f"Analyzing XML document: {file_path}")
        
        # Use SAX parser for memory efficiency
        parser = make_parser()
        handler = XMLStreamHandler(max_samples=self.max_samples)
        parser.setContentHandler(handler)
        parser.setFeature("http://xml.org/sax/features/namespaces", True)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            parser.parse(f)
        
        # Build structure tree
        structure_tree = self._build_structure_tree(handler.elements)
        
        # Get root element
        root_element = ""
        for tag, element in handler.elements.items():
            if not element.parent_elements:
                root_element = tag
                break
        
        # Gather statistics
        file_size = Path(file_path).stat().st_size
        total_elements = sum(e.count for e in handler.elements.values())
        
        statistics = {
            'file_size_bytes': file_size,
            'total_elements': total_elements,
            'unique_elements': len(handler.elements),
            'max_depth': max(max(e.depths) for e in handler.elements.values() if e.depths),
            'namespace_count': len(handler.namespaces)
        }
        
        # Convert defaultdicts for serialization
        elements_dict = {}
        for tag, element in handler.elements.items():
            elements_dict[tag] = XMLElement(
                tag=element.tag,
                namespace=element.namespace,
                count=element.count,
                depths=element.depths,
                attributes={k: v for k, v in element.attributes.items()},
                text_samples=element.text_samples,
                parent_elements=element.parent_elements,
                child_elements=element.child_elements,
                paths=element.paths,
                line_numbers=element.line_numbers
            )
        
        schema = DocumentSchema(
            document_type=DocumentTypeDetector.detect_type(None),  # Will be set after creation
            root_element=root_element,
            namespaces=handler.namespaces,
            elements=elements_dict,
            structure_tree=structure_tree,
            statistics=statistics,
            specialized_info={}
        )
        
        # Set document type
        schema.document_type = DocumentTypeDetector.detect_type(schema)
        
        return schema
    
    def chunk_document(self, file_path: str, schema: DocumentSchema) -> List[DocumentChunk]:
        """Chunk document for LLM processing"""
        return self.chunker.chunk_by_elements(file_path, schema)
    
    def generate_llm_prompts(self, schema: DocumentSchema, chunks: List[DocumentChunk], 
                           file_path: str) -> Dict[str, str]:
        """Generate all prompts for LLM analysis"""
        file_size = Path(file_path).stat().st_size
        
        prompts = {
            'schema_analysis': LLMPromptGenerator.generate_schema_prompt(schema, file_size)
        }
        
        # Generate chunk prompts
        for i, chunk in enumerate(chunks[:5]):  # Limit to first 5 chunks for demo
            prompts[f'chunk_{i:03d}'] = LLMPromptGenerator.generate_chunk_prompt(chunk, schema)
        
        return prompts
    
    def _build_structure_tree(self, elements: Dict[str, XMLElement]) -> Dict[str, Any]:
        """Build hierarchical structure representation"""
        tree = {}
        
        # Find root elements
        for tag, element in elements.items():
            if not element.parent_elements:
                tree[tag] = self._build_subtree(tag, elements)
        
        return tree
    
    def _build_subtree(self, tag: str, elements: Dict[str, XMLElement]) -> Dict[str, Any]:
        """Recursively build structure subtree"""
        element = elements[tag]
        
        node = {
            "count": element.count,
            "namespace": element.namespace,
            "attributes": list(element.attributes.keys()),
            "has_text": len(element.text_samples) > 0,
            "children": {}
        }
        
        for child_tag in element.child_elements:
            if child_tag in elements:
                node["children"][child_tag] = self._build_subtree(child_tag, elements)
        
        return node
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Complete document processing pipeline"""
        
        # Step 1: Analyze schema
        schema = self.analyze_document(file_path)
        self.logger.info(f"Document type detected: {schema.document_type}")
        
        # Step 2: Chunk document
        chunks = self.chunk_document(file_path, schema)
        self.logger.info(f"Created {len(chunks)} chunks")
        
        # Step 3: Generate LLM prompts
        prompts = self.generate_llm_prompts(schema, chunks, file_path)
        
        # Step 4: Return complete analysis package
        return {
            'schema': schema,
            'chunks': chunks,
            'prompts': prompts,
            'processing_strategy': self._suggest_processing_strategy(schema)
        }
    
    def _suggest_processing_strategy(self, schema: DocumentSchema) -> Dict[str, str]:
        """Suggest optimal processing strategy based on document type"""
        
        strategies = {
            'SCAP': {
                'approach': 'Security-focused analysis',
                'key_elements': ['rule', 'check', 'test', 'result'],
                'extraction_pattern': 'Extract compliance status and security findings'
            },
            'XCCDF': {
                'approach': 'Checklist processing',
                'key_elements': ['rule', 'select', 'check'],
                'extraction_pattern': 'Extract security configuration requirements'
            },
            'OVAL': {
                'approach': 'Vulnerability assessment',
                'key_elements': ['definition', 'test', 'object', 'state'],
                'extraction_pattern': 'Extract vulnerability definitions and test criteria'
            },
            'GENERIC_XML': {
                'approach': 'General XML processing',
                'key_elements': list(schema.elements.keys())[:5],
                'extraction_pattern': 'Extract structured data based on element hierarchy'
            }
        }
        
        return strategies.get(schema.document_type, strategies['GENERIC_XML'])

# Example usage and testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python xml_framework.py <xml_file>")
        sys.exit(1)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize framework
    framework = XMLAgentFramework(max_chunk_size=6000)
    
    # Process document
    try:
        result = framework.process_document(sys.argv[1])
        
        print(f"Document Type: {result['schema'].document_type}")
        print(f"Total Elements: {result['schema'].statistics['total_elements']:,}")
        print(f"Chunks Created: {len(result['chunks'])}")
        print(f"Processing Strategy: {result['processing_strategy']['approach']}")
        
        # Save analysis results
        output_file = Path(sys.argv[1]).stem + "_analysis.json"
        
        # Convert for JSON serialization
        serializable_result = {
            'schema': {
                'document_type': result['schema'].document_type,
                'root_element': result['schema'].root_element,
                'statistics': result['schema'].statistics,
                'namespaces': result['schema'].namespaces
            },
            'chunks_summary': [
                {
                    'chunk_id': chunk.chunk_id,
                    'size_bytes': chunk.size_bytes,
                    'element_path': chunk.element_path,
                    'summary': chunk.summary
                }
                for chunk in result['chunks']
            ],
            'processing_strategy': result['processing_strategy']
        }
        
        with open(output_file, 'w') as f:
            json.dump(serializable_result, f, indent=2)
        
        print(f"Analysis saved to: {output_file}")
        
        # Display first prompt
        print("\n=== SAMPLE SCHEMA ANALYSIS PROMPT ===")
        print(result['prompts']['schema_analysis'][:1000] + "...")
        
    except Exception as e:
        logging.error(f"Error processing document: {e}")
        sys.exit(1)