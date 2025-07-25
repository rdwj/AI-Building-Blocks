#!/usr/bin/env python3
"""
Test a small sample to verify handler fixes
"""

import sys
import os
import json
from datetime import datetime

# Add src to path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.analyzer import XMLDocumentAnalyzer
from core.chunking import ChunkingOrchestrator, ChunkingConfig

def test_small_sample():
    """Test a few files to verify the fixes"""
    
    print("🧪 TESTING HANDLER FIXES - SMALL SAMPLE")
    print("=" * 60)
    
    test_files = [
        "sample_data/test_files/small/scap/ios-sample-1.1.xccdf.xml",
        "sample_data/test_files/small/ant/apache-ant-build.xml", 
        "sample_data/test_files_synthetic/small/log4j/log4j.xml",
        "sample_data/test_files_synthetic/small/docbook/article.xml"
    ]
    
    analyzer = XMLDocumentAnalyzer()
    orchestrator = ChunkingOrchestrator()
    
    results = {}
    
    for file_path in test_files:
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            continue
            
        file_name = os.path.basename(file_path)
        print(f"\n📄 Testing: {file_name}")
        
        # Analyze document
        analysis = analyzer.analyze_document(file_path)
        
        # Extract information from analysis result
        if hasattr(analysis, 'document_type'):
            # It's a SpecializedAnalysis object
            doc_type = analysis.document_type
            handler = getattr(analysis, 'handler_used', 'SpecializedAnalysis')
            analysis_dict = {
                'document_type': {'type_name': analysis.document_type},
                'key_findings': analysis.key_findings,
                'structured_data': analysis.structured_data
            }
        elif 'document_type' in analysis and hasattr(analysis['document_type'], 'type_name'):
            # It's a dict with DocumentTypeInfo object
            doc_type = analysis['document_type'].type_name
            handler = analysis.get('handler_used', 'unknown')
            analysis_dict = {
                'document_type': {'type_name': doc_type},
                'key_findings': analysis.get('key_findings', {}),
                'structured_data': analysis.get('structured_data', {})
            }
        else:
            # It's a plain dict
            doc_type = analysis.get('document_type', {}).get('type_name', 'unknown')
            handler = analysis.get('handler_used', 'unknown')
            analysis_dict = analysis
        
        print(f"   📋 Document Type: {doc_type}")
        print(f"   🔧 Handler: {handler}")
        
        # Test hierarchical chunking
        config = ChunkingConfig(max_chunk_size=2000, min_chunk_size=200, overlap_size=100)
        
        try:
            chunks = orchestrator.chunk_document(
                file_path,
                analysis_dict,
                strategy='hierarchical',
                config=config
            )
            
            print(f"   📦 Hierarchical chunks: {len(chunks)}")
            if chunks:
                tokens = [c.token_estimate for c in chunks]
                print(f"      Token range: {min(tokens)}-{max(tokens)}")
                print(f"      Avg tokens: {sum(tokens)/len(tokens):.0f}")
            
        except Exception as e:
            print(f"   ❌ Chunking error: {e}")
            
        # Test auto strategy
        try:
            auto_chunks = orchestrator.chunk_document(
                file_path,
                analysis_dict,
                strategy='auto',
                config=config
            )
            
            print(f"   🤖 Auto chunks: {len(auto_chunks)}")
            
        except Exception as e:
            print(f"   ❌ Auto chunking error: {e}")
        
        results[file_name] = {
            'document_type': doc_type,
            'handler': handler,
            'hierarchical_chunks': len(chunks) if 'chunks' in locals() else 0,
            'auto_chunks': len(auto_chunks) if 'auto_chunks' in locals() else 0
        }
    
    print(f"\n📊 SUMMARY")
    print("-" * 30)
    print(f"{'File':<25} {'Doc Type':<20} {'Handler':<15} {'Hier':<6} {'Auto':<6}")
    print("-" * 80)
    
    for file_name, data in results.items():
        doc_type = data['document_type'][:18] + '..' if len(data['document_type']) > 20 else data['document_type']
        handler = data['handler'][:13] + '..' if len(data['handler']) > 15 else data['handler']
        print(f"{file_name[:23]:<25} {doc_type:<20} {handler:<15} {data['hierarchical_chunks']:<6} {data['auto_chunks']:<6}")
    
    print(f"\n💡 Results:")
    working_handlers = sum(1 for d in results.values() if d['handler'] != 'GenericXMLHandler')
    working_hierarchical = sum(1 for d in results.values() if d['hierarchical_chunks'] > 0)
    
    print(f"   Specialized handlers working: {working_handlers}/{len(results)}")
    print(f"   Hierarchical chunking working: {working_hierarchical}/{len(results)}")

if __name__ == "__main__":
    test_small_sample()