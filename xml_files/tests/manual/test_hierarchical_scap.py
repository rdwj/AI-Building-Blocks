#!/usr/bin/env python3
"""
Test hierarchical chunking strategy with SCAP document
"""

import sys
import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime

# Add src to path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.chunking import ChunkingOrchestrator, ChunkingConfig
from handlers.scap_handler import SCAPHandler

def test_hierarchical_with_scap():
    """Test hierarchical chunking with SCAP document"""
    
    # SCAP file to test with - try XCCDF instead of XSD
    scap_file = "sample_data/test_files/small/scap/ios-sample-1.1.xccdf.xml"
    
    print("📦 HIERARCHICAL CHUNKING WITH SCAP DOCUMENT")
    print("=" * 60)
    print(f"File: {scap_file}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if file exists
    if not os.path.exists(scap_file):
        print(f"❌ File not found: {scap_file}")
        return
    
    # First, analyze the file with SCAP handler
    print(f"\n🔒 Pre-analysis with SCAP Handler")
    print("-" * 40)
    
    handler = SCAPHandler()
    tree = ET.parse(scap_file)
    root = tree.getroot()
    namespaces = {prefix: uri for prefix, uri in root.nsmap.items()} if hasattr(root, 'nsmap') else {}
    
    # Test if SCAP handler can handle this
    can_handle, confidence = handler.can_handle(root, namespaces)
    print(f"SCAP Handler Recognition:")
    print(f"  Can Handle: {can_handle}")
    print(f"  Confidence: {confidence:.2%}")
    
    if can_handle:
        analysis_result = handler.analyze(root, scap_file)
        print(f"  Document Type: {analysis_result.document_type}")
        
        # Convert to dict format for chunking
        analysis_dict = {
            'document_type': {'type_name': analysis_result.document_type},
            'key_findings': analysis_result.key_findings,
            'structured_data': analysis_result.structured_data
        }
    else:
        # Use generic analysis
        print("  Using generic XML analysis...")
        analysis_dict = {
            'document_type': {'type_name': 'SCAP/XSD Schema'},
            'key_findings': {'elements': len(list(root.iter()))},
            'structured_data': {}
        }
    
    # Analyze file structure
    print(f"\n📋 Document Structure Analysis")
    print("-" * 40)
    elements = list(root.iter())
    print(f"Root Element: {root.tag}")
    print(f"Total Elements: {len(elements):,}")
    print(f"Namespaces: {len(namespaces)}")
    
    # Show element distribution
    element_counts = {}
    for elem in elements:
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        element_counts[tag] = element_counts.get(tag, 0) + 1
    
    print(f"Top element types:")
    for tag, count in sorted(element_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {tag}: {count}")
    
    # Test different chunking strategies on SCAP
    print(f"\n🔧 Testing Chunking Strategies")
    print("=" * 50)
    
    orchestrator = ChunkingOrchestrator()
    
    strategies = [
        ('hierarchical', 'Respects XML structure and semantic boundaries'),
        ('sliding_window', 'Overlapping chunks for context preservation'),
        ('content_aware', 'Groups similar content types together'),
        ('auto', 'Automatically selects best strategy')
    ]
    
    results = {}
    
    for strategy, description in strategies:
        print(f"\n📋 Testing {strategy.upper()} Strategy")
        print("-" * 40)
        print(f"Description: {description}")
        
        try:
            # Create chunking config
            config = ChunkingConfig(
                max_chunk_size=1500,  # Smaller for SCAP/XSD
                min_chunk_size=200,
                overlap_size=100,
                preserve_hierarchy=True
            )
            
            chunks = orchestrator.chunk_document(
                scap_file,
                analysis_dict,
                strategy=strategy,
                config=config
            )
            
            print(f"✅ Generated {len(chunks)} chunks")
            
            if chunks:
                # Analyze chunk characteristics
                total_tokens = sum(chunk.token_estimate for chunk in chunks)
                avg_tokens = total_tokens / len(chunks)
                
                chunk_sizes = [chunk.token_estimate for chunk in chunks]
                min_size = min(chunk_sizes)
                max_size = max(chunk_sizes)
                
                print(f"   Total estimated tokens: {total_tokens:,}")
                print(f"   Average chunk size: {avg_tokens:.0f} tokens")
                print(f"   Size range: {min_size}-{max_size} tokens")
                
                # Show first few chunks details
                print(f"   Sample chunks:")
                for i, chunk in enumerate(chunks[:5]):
                    path = chunk.element_path or "root"
                    content_preview = chunk.content[:80] + "..." if len(chunk.content) > 80 else chunk.content
                    content_preview = content_preview.replace('\n', ' ').replace('\t', ' ')
                    print(f"     {i+1}. {chunk.chunk_id}")
                    print(f"        Path: {path}")
                    print(f"        Tokens: {chunk.token_estimate}")
                    print(f"        Content: {content_preview}")
                    
                    # Show metadata if available
                    if chunk.metadata:
                        key_metadata = {k: v for k, v in chunk.metadata.items() 
                                      if k in ['chunk_type', 'content_type', 'semantic_role', 'elements_count']}
                        if key_metadata:
                            print(f"        Metadata: {key_metadata}")
                    print()
                
                if len(chunks) > 5:
                    print(f"     ... and {len(chunks) - 5} more chunks")
                
                # Store results
                results[strategy] = {
                    'chunk_count': len(chunks),
                    'total_tokens': total_tokens,
                    'avg_tokens': avg_tokens,
                    'min_size': min_size,
                    'max_size': max_size,
                    'chunks': chunks[:5]  # Store first 5 for analysis
                }
            else:
                print("   ⚠️ No chunks generated")
                results[strategy] = {
                    'chunk_count': 0,
                    'total_tokens': 0,
                    'avg_tokens': 0,
                    'min_size': 0,
                    'max_size': 0,
                    'chunks': []
                }
                
        except Exception as e:
            print(f"❌ Error with {strategy} strategy: {e}")
            import traceback
            traceback.print_exc()
    
    # Generate comparison
    print(f"\n📊 SCAP CHUNKING STRATEGY COMPARISON")
    print("=" * 60)
    
    if results:
        print(f"{'Strategy':<15} {'Chunks':<8} {'Total Tokens':<12} {'Avg Tokens':<11} {'Size Range':<15}")
        print("-" * 70)
        
        for strategy, data in results.items():
            if data['chunk_count'] > 0:
                size_range = f"{data['min_size']}-{data['max_size']}"
                print(f"{strategy:<15} {data['chunk_count']:<8} {data['total_tokens']:<12,} {data['avg_tokens']:<11.0f} {size_range:<15}")
            else:
                print(f"{strategy:<15} {'0':<8} {'0':<12} {'0':<11} {'0-0':<15}")
    
    # Detailed hierarchical analysis
    if 'hierarchical' in results and results['hierarchical']['chunk_count'] > 0:
        print(f"\n🔍 DETAILED HIERARCHICAL ANALYSIS")
        print("-" * 40)
        
        h_chunks = results['hierarchical']['chunks']
        print(f"Hierarchical strategy successfully created {results['hierarchical']['chunk_count']} chunks")
        print(f"This demonstrates the hierarchical approach working with structured XML")
        print()
        
        for i, chunk in enumerate(h_chunks, 1):
            print(f"Hierarchical Chunk {i}:")
            print(f"  ID: {chunk.chunk_id}")
            print(f"  Path: {chunk.element_path}")
            print(f"  Tokens: {chunk.token_estimate}")
            print(f"  Elements: {len(chunk.elements_included) if chunk.elements_included else 'N/A'}")
            
            # Show content structure
            if chunk.content:
                lines = chunk.content.split('\n')[:3]
                for line in lines:
                    clean_line = line.strip()
                    if clean_line:
                        print(f"  Content: {clean_line[:60]}{'...' if len(clean_line) > 60 else ''}")
                        break
            print()
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"scap_chunking_analysis_{timestamp}.json"
    
    comparison_data = {
        "test_info": {
            "file_analyzed": scap_file,
            "file_basename": os.path.basename(scap_file),
            "analysis_timestamp": datetime.now().isoformat(),
            "document_type": analysis_dict['document_type']['type_name']
        },
        "document_structure": {
            "root_element": root.tag,
            "total_elements": len(elements),
            "namespace_count": len(namespaces),
            "element_distribution": dict(sorted(element_counts.items(), key=lambda x: x[1], reverse=True)[:20])
        },
        "chunking_results": {
            strategy: {
                "chunk_count": data['chunk_count'],
                "total_tokens": data['total_tokens'],
                "avg_tokens": data['avg_tokens'],
                "size_range": f"{data['min_size']}-{data['max_size']}" if data['chunk_count'] > 0 else "0-0"
            }
            for strategy, data in results.items()
        }
    }
    
    with open(output_file, 'w') as f:
        json.dump(comparison_data, f, indent=2, default=str)
    
    print(f"\n💾 Analysis saved to: {output_file}")
    print(f"📊 File size: {os.path.getsize(output_file):,} bytes")
    
    # Key insights
    print(f"\n💡 KEY INSIGHTS")
    print("-" * 30)
    
    if results.get('hierarchical', {}).get('chunk_count', 0) > 0:
        print("✅ Hierarchical chunking WORKS with SCAP/XSD documents")
        print("   - Respects XML schema structure")
        print("   - Creates logical semantic boundaries")
        print("   - Better suited for structured XML than flat ServiceNow format")
    else:
        print("⚠️ Hierarchical chunking did not generate chunks for this SCAP file")
        print("   - May need strategy customization")
        print("   - File might be too small or have incompatible structure")
    
    working_strategies = [s for s, data in results.items() if data.get('chunk_count', 0) > 0]
    if working_strategies:
        print(f"\n✅ Working strategies for SCAP: {', '.join(working_strategies)}")
    
    return output_file

if __name__ == "__main__":
    test_hierarchical_with_scap()