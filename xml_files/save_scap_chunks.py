#!/usr/bin/env python3
"""
Save SCAP document chunks with full content for examination
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

def save_scap_chunks():
    """Save SCAP document chunks with full content"""
    
    # SCAP file to process
    scap_file = "sample_data/test_files/small/scap/ios-sample-1.1.xccdf.xml"
    
    print("💾 SAVING SCAP CHUNKS WITH FULL CONTENT")
    print("=" * 60)
    print(f"File: {scap_file}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not os.path.exists(scap_file):
        print(f"❌ File not found: {scap_file}")
        return
    
    # Analyze with SCAP handler
    handler = SCAPHandler()
    tree = ET.parse(scap_file)
    root = tree.getroot()
    namespaces = {prefix: uri for prefix, uri in root.nsmap.items()} if hasattr(root, 'nsmap') else {}
    
    can_handle, confidence = handler.can_handle(root, namespaces)
    if can_handle:
        analysis_result = handler.analyze(root, scap_file)
        analysis_dict = {
            'document_type': {'type_name': analysis_result.document_type},
            'key_findings': analysis_result.key_findings,
            'structured_data': analysis_result.structured_data
        }
        print(f"✅ SCAP Handler Analysis: {analysis_result.document_type}")
    else:
        print("❌ SCAP Handler failed - using generic analysis")
        return
    
    # Create orchestrator and config
    orchestrator = ChunkingOrchestrator()
    config = ChunkingConfig(
        max_chunk_size=1500,
        min_chunk_size=200,
        overlap_size=100,
        preserve_hierarchy=True
    )
    
    # Test all strategies and save chunks
    strategies = ['hierarchical', 'sliding_window', 'content_aware', 'auto']
    
    for strategy in strategies:
        print(f"\n📋 Processing {strategy.upper()} strategy...")
        
        try:
            chunks = orchestrator.chunk_document(
                scap_file,
                analysis_dict,
                strategy=strategy,
                config=config
            )
            
            print(f"   Generated {len(chunks)} chunks")
            
            if chunks:
                # Save chunks to file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = f"scap_chunks_{strategy}_{timestamp}.json"
                
                # Convert chunks to serializable format
                chunks_data = {
                    "metadata": {
                        "file_analyzed": scap_file,
                        "strategy": strategy,
                        "chunk_count": len(chunks),
                        "analysis_timestamp": datetime.now().isoformat(),
                        "document_type": analysis_dict['document_type']['type_name']
                    },
                    "chunks": []
                }
                
                for i, chunk in enumerate(chunks):
                    chunk_data = {
                        "chunk_number": i + 1,
                        "chunk_id": chunk.chunk_id,
                        "element_path": chunk.element_path,
                        "token_estimate": chunk.token_estimate,
                        "content_length": len(chunk.content),
                        "elements_included": chunk.elements_included,
                        "metadata": chunk.metadata,
                        "start_line": chunk.start_line,
                        "end_line": chunk.end_line,
                        "parent_context": chunk.parent_context,
                        "full_content": chunk.content  # The actual chunk content
                    }
                    chunks_data["chunks"].append(chunk_data)
                
                # Save to file
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(chunks_data, f, indent=2, ensure_ascii=False)
                
                file_size = os.path.getsize(output_file)
                print(f"   💾 Saved to: {output_file}")
                print(f"   📊 File size: {file_size:,} bytes")
                
                # Show first chunk preview
                if len(chunks) > 0:
                    first_chunk = chunks[0]
                    content_preview = first_chunk.content[:200] + "..." if len(first_chunk.content) > 200 else first_chunk.content
                    content_preview = content_preview.replace('\n', ' ').replace('\t', ' ')
                    print(f"   📄 First chunk preview: {content_preview}")
                
        except Exception as e:
            print(f"❌ Error with {strategy}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✅ SCAP chunk files saved!")
    print(f"📁 Look for files matching pattern: scap_chunks_*_{datetime.now().strftime('%Y%m%d')}_*.json")
    
    # Show file listing
    import glob
    chunk_files = glob.glob("scap_chunks_*.json")
    if chunk_files:
        print(f"\n📁 Available SCAP chunk files:")
        for file in sorted(chunk_files):
            size = os.path.getsize(file)
            print(f"   {file} ({size:,} bytes)")

if __name__ == "__main__":
    save_scap_chunks()