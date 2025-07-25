#!/usr/bin/env python3
"""
Debug hierarchical chunking issue
"""

import sys
import os
import xml.etree.ElementTree as ET

# Add src to path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.chunking import HierarchicalChunking, ChunkingConfig

def debug_hierarchical_chunking():
    """Debug why hierarchical chunking produces 0 chunks"""
    
    print("🔍 DEBUGGING HIERARCHICAL CHUNKING")
    print("=" * 50)
    
    # Test with SCAP file
    scap_file = "sample_data/test_files/small/scap/ios-sample-1.1.xccdf.xml"
    
    if not os.path.exists(scap_file):
        print(f"❌ File not found: {scap_file}")
        return
    
    # Parse the file
    tree = ET.parse(scap_file)
    root = tree.getroot()
    
    print(f"📄 File: {scap_file}")
    print(f"🌳 Root element: {root.tag}")
    
    # Create hierarchical chunker
    config = ChunkingConfig()
    chunker = HierarchicalChunking(config)
    
    # Test semantic boundaries detection
    print(f"\n🎯 Testing semantic boundaries detection")
    print("-" * 40)
    
    # Test with different document types
    test_types = [
        "SCAP Security Report",
        "SCAP/XSD Schema", 
        "ServiceNow Export",
        "Unknown Type"
    ]
    
    for doc_type in test_types:
        boundaries = chunker._get_semantic_boundaries(doc_type)
        print(f"Document type: '{doc_type}'")
        print(f"  Semantic boundaries: {boundaries}")
        
        # Test if any elements match these boundaries
        matching_elements = []
        for elem in root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            if tag in boundaries:
                matching_elements.append(tag)
        
        unique_matches = list(set(matching_elements))
        print(f"  Matching elements in file: {unique_matches[:10]}{'...' if len(unique_matches) > 10 else ''}")
        print(f"  Total matching elements: {len(matching_elements)}")
        print()
    
    # Examine actual elements in the file
    print(f"🔍 Analyzing actual elements in file")
    print("-" * 40)
    
    element_counts = {}
    for elem in root.iter():
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        element_counts[tag] = element_counts.get(tag, 0) + 1
    
    print(f"Top 15 elements in file:")
    for tag, count in sorted(element_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"  {tag}: {count}")
    
    # Test with a custom analysis that should work
    print(f"\n🛠️ Testing with custom semantic boundaries")
    print("-" * 40)
    
    # Create analysis dict with proper boundaries for this file
    analysis_dict = {
        'document_type': {'type_name': 'SCAP Security Report'},  # Use the working type
        'key_findings': {},
        'structured_data': {}
    }
    
    # Test chunking with this analysis
    try:
        chunks = chunker.chunk_document(scap_file, analysis_dict)
        print(f"✅ With 'SCAP Security Report' type: Generated {len(chunks)} chunks")
        
        if chunks:
            for i, chunk in enumerate(chunks[:3]):
                print(f"  Chunk {i+1}: {chunk.token_estimate} tokens, path: {chunk.element_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test with improved boundaries that match file content
    print(f"\n🎯 Testing with file-specific boundaries")
    print("-" * 40)
    
    # Override the semantic boundaries temporarily
    original_method = chunker._get_semantic_boundaries
    
    def custom_boundaries(doc_type):
        # Use elements that actually exist in our test files
        return ["Rule", "Group", "Benchmark", "complexType", "element", "incident", "sys_journal_field"]
    
    chunker._get_semantic_boundaries = custom_boundaries
    
    try:
        chunks = chunker.chunk_document(scap_file, analysis_dict)
        print(f"✅ With custom boundaries: Generated {len(chunks)} chunks")
        
        if chunks:
            for i, chunk in enumerate(chunks[:3]):
                print(f"  Chunk {i+1}: {chunk.token_estimate} tokens, path: {chunk.element_path}")
                print(f"    Elements: {chunk.elements_included[:5]}")
        
    except Exception as e:
        print(f"❌ Error with custom boundaries: {e}")
    finally:
        # Restore original method
        chunker._get_semantic_boundaries = original_method
    
    print(f"\n💡 DIAGNOSIS")
    print("-" * 20)
    print("The hierarchical chunking strategy fails because:")
    print("1. Document type detection doesn't match predefined semantic boundaries")
    print("2. Generic fallback boundaries don't match actual XML element names")
    print("3. No elements are identified as semantic boundaries")
    print("4. Without boundaries, no chunks are created")
    
    print(f"\n🔧 SOLUTIONS")
    print("-" * 20)
    print("1. Add more document types to semantic_boundaries mapping")
    print("2. Improve element name matching (handle namespaces better)")
    print("3. Add dynamic boundary detection based on file analysis")
    print("4. Provide fallback chunking when no boundaries found")

if __name__ == "__main__":
    debug_hierarchical_chunking()