#!/usr/bin/env python3
"""
Simple viewer for chunk content
"""

import json
import sys
import os
from datetime import datetime

def view_chunk_content(file_path, chunk_number=None, preview_length=500):
    """View content of specific chunks"""
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    metadata = data.get('metadata', {})
    chunks = data.get('chunks', [])
    
    print(f"📄 CHUNK CONTENT VIEWER")
    print("=" * 50)
    print(f"File: {file_path}")
    print(f"Strategy: {metadata.get('strategy', 'unknown')}")
    print(f"Document Type: {metadata.get('document_type', 'unknown')}")
    print(f"Total Chunks: {len(chunks)}")
    print()
    
    if chunk_number is None:
        # Show summary of all chunks
        print("📋 CHUNK SUMMARY")
        print("-" * 30)
        for i, chunk in enumerate(chunks, 1):
            print(f"Chunk {i}: {chunk['chunk_id']}")
            print(f"  Path: {chunk['element_path']}")
            print(f"  Tokens: {chunk['token_estimate']}")
            print(f"  Content Length: {chunk['content_length']:,} chars")
            
            # Show first line of content
            content = chunk['full_content']
            first_line = content.split('\n')[0][:80]
            if len(content.split('\n')[0]) > 80:
                first_line += "..."
            print(f"  Preview: {first_line}")
            print()
            
        print(f"💡 To view full content of a specific chunk, run:")
        print(f"   python view_chunk_content.py {file_path} <chunk_number>")
        
    else:
        # Show specific chunk content
        if chunk_number < 1 or chunk_number > len(chunks):
            print(f"❌ Invalid chunk number. Must be 1-{len(chunks)}")
            return
            
        chunk = chunks[chunk_number - 1]
        print(f"📄 CHUNK {chunk_number} CONTENT")
        print("=" * 50)
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"Element Path: {chunk['element_path']}")
        print(f"Token Estimate: {chunk['token_estimate']}")
        print(f"Content Length: {chunk['content_length']:,} characters")
        print(f"Elements Included: {len(chunk['elements_included'])} unique elements")
        print()
        
        if chunk['metadata']:
            print("📋 Metadata:")
            for key, value in chunk['metadata'].items():
                if key not in ['document_type', 'chunk_index', 'total_chunks']:
                    print(f"  {key}: {value}")
            print()
        
        print("📄 FULL CONTENT:")
        print("-" * 30)
        
        content = chunk['full_content']
        if len(content) <= preview_length:
            print(content)
        else:
            print(content[:preview_length])
            print(f"\n... (content truncated at {preview_length} chars)")
            print(f"💡 Full content is {len(content):,} characters")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python view_chunk_content.py <chunk_file.json> [chunk_number]")
        print()
        print("Available chunk files:")
        import glob
        chunk_files = glob.glob("scap_chunks_*.json")
        for file in sorted(chunk_files):
            size = os.path.getsize(file)
            print(f"  {file} ({size:,} bytes)")
        sys.exit(1)
    
    file_path = sys.argv[1]
    chunk_number = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    view_chunk_content(file_path, chunk_number)