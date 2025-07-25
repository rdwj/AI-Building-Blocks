#!/usr/bin/env python3
"""
Test and demonstrate different XML chunking strategies on ServiceNow data
"""

import sys
import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime

# Add src to path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.chunking import ChunkingOrchestrator, ChunkingConfig
from handlers.servicenow_handler import ServiceNowHandler

def test_chunking_strategies():
    """Test all available chunking strategies on ServiceNow data"""
    
    # ServiceNow file to test with
    ticket_file = "/Users/wjackson/Developer/LLNL/data/rhoai-sanitized-main/servicenow/incident_1217.xml"
    
    print("📦 XML CHUNKING STRATEGIES DEMONSTRATION")
    print("=" * 60)
    print(f"File: {os.path.basename(ticket_file)}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # First, analyze the file with ServiceNow handler
    print(f"\n🎫 Pre-analysis with ServiceNow Handler")
    print("-" * 40)
    
    handler = ServiceNowHandler()
    tree = ET.parse(ticket_file)
    root = tree.getroot()
    
    analysis_result = handler.analyze(root, ticket_file)
    print(f"Document Type: {analysis_result.document_type}")
    print(f"Journal Entries: {analysis_result.key_findings.get('journal_analysis', {}).get('total_entries', 'N/A')}")
    print(f"Attachments: {analysis_result.key_findings.get('attachment_analysis', {}).get('total_attachments', 'N/A')}")
    print(f"Total Fields: {analysis_result.data_inventory.get('total_fields', 'N/A')}")
    
    # Initialize chunking orchestrator
    orchestrator = ChunkingOrchestrator()
    
    # Test different chunking strategies (only those implemented)
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
            # Create chunking config for this strategy
            config = ChunkingConfig(
                max_chunk_size=2048,  # Reasonable size for testing
                min_chunk_size=200,
                overlap_size=100,
                preserve_hierarchy=True
            )
            
            # Apply chunking - pass analysis_result as dict
            analysis_dict = {
                'document_type': {'type_name': analysis_result.document_type},
                'key_findings': analysis_result.key_findings,
                'structured_data': analysis_result.structured_data
            }
            
            chunks = orchestrator.chunk_document(
                ticket_file,
                analysis_dict,
                strategy=strategy,
                config=config
            )
            
            print(f"✅ Generated {len(chunks)} chunks")
            
            # Analyze chunk characteristics
            total_tokens = sum(chunk.token_estimate for chunk in chunks)
            avg_tokens = total_tokens / len(chunks) if chunks else 0
            
            chunk_sizes = [chunk.token_estimate for chunk in chunks]
            min_size = min(chunk_sizes) if chunk_sizes else 0
            max_size = max(chunk_sizes) if chunk_sizes else 0
            
            print(f"   Total estimated tokens: {total_tokens:,}")
            print(f"   Average chunk size: {avg_tokens:.0f} tokens")
            print(f"   Size range: {min_size}-{max_size} tokens")
            
            # Show first few chunks details
            print(f"   Sample chunks:")
            for i, chunk in enumerate(chunks[:3]):
                path = chunk.element_path or "root"
                content_preview = chunk.content[:60] + "..." if len(chunk.content) > 60 else chunk.content
                print(f"     {i+1}. {chunk.chunk_id}")
                print(f"        Path: {path}")
                print(f"        Tokens: {chunk.token_estimate}")
                print(f"        Content: {content_preview}")
                
                # Show metadata if available
                if chunk.metadata:
                    key_metadata = {k: v for k, v in chunk.metadata.items() if k in ['chunk_type', 'content_type', 'semantic_role']}
                    if key_metadata:
                        print(f"        Metadata: {key_metadata}")
                print()
            
            if len(chunks) > 3:
                print(f"     ... and {len(chunks) - 3} more chunks")
            
            # Store results for comparison
            results[strategy] = {
                'chunk_count': len(chunks),
                'total_tokens': total_tokens,
                'avg_tokens': avg_tokens,
                'min_size': min_size,
                'max_size': max_size,
                'chunks': chunks
            }
            
        except Exception as e:
            print(f"❌ Error with {strategy} strategy: {e}")
            import traceback
            traceback.print_exc()
    
    # Generate comparison analysis
    print(f"\n📊 CHUNKING STRATEGY COMPARISON")
    print("=" * 60)
    
    comparison_data = {
        "test_info": {
            "file_analyzed": ticket_file,
            "file_basename": os.path.basename(ticket_file),
            "analysis_timestamp": datetime.now().isoformat(),
            "document_type": analysis_result.document_type
        },
        "strategies_tested": len(results),
        "comparison_results": {}
    }
    
    # Create comparison table
    print(f"{'Strategy':<15} {'Chunks':<8} {'Total Tokens':<12} {'Avg Tokens':<11} {'Size Range':<15}")
    print("-" * 70)
    
    for strategy, data in results.items():
        size_range = f"{data['min_size']}-{data['max_size']}"
        print(f"{strategy:<15} {data['chunk_count']:<8} {data['total_tokens']:<12,} {data['avg_tokens']:<11.0f} {size_range:<15}")
        
        # Add to comparison data
        comparison_data["comparison_results"][strategy] = {
            "chunk_count": data['chunk_count'],
            "total_tokens": data['total_tokens'],
            "avg_tokens": data['avg_tokens'],
            "size_range": size_range,
            "chunk_details": [
                {
                    "chunk_id": chunk.chunk_id,
                    "token_estimate": chunk.token_estimate,
                    "element_path": chunk.element_path,
                    "content_preview": chunk.content[:100] + "..." if len(chunk.content) > 100 else chunk.content,
                    "metadata": chunk.metadata
                }
                for chunk in data['chunks'][:5]  # First 5 chunks for each strategy
            ]
        }
    
    # Analysis insights
    print(f"\n🔍 CHUNKING INSIGHTS")
    print("-" * 30)
    
    if results:
        # Find most efficient strategy
        min_chunks = min(data['chunk_count'] for data in results.values())
        max_chunks = max(data['chunk_count'] for data in results.values())
        
        most_efficient = [strategy for strategy, data in results.items() if data['chunk_count'] == min_chunks]
        most_granular = [strategy for strategy, data in results.items() if data['chunk_count'] == max_chunks]
        
        print(f"Most efficient (fewest chunks): {', '.join(most_efficient)} ({min_chunks} chunks)")
        print(f"Most granular (most chunks): {', '.join(most_granular)} ({max_chunks} chunks)")
        
        # Token distribution analysis
        print(f"\nToken Distribution:")
        for strategy, data in results.items():
            efficiency = data['total_tokens'] / data['chunk_count'] if data['chunk_count'] > 0 else 0
            print(f"  {strategy}: {efficiency:.0f} tokens/chunk efficiency")
    
    # Save detailed results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"chunking_analysis_{os.path.splitext(os.path.basename(ticket_file))[0]}_{timestamp}.json"
    
    print(f"\n💾 Saving detailed analysis to: {output_file}")
    
    with open(output_file, 'w') as f:
        json.dump(comparison_data, f, indent=2, default=str)
    
    print(f"📊 File size: {os.path.getsize(output_file):,} bytes")
    
    # Recommendations
    print(f"\n💡 CHUNKING RECOMMENDATIONS")
    print("-" * 30)
    
    if 'hierarchical' in results and 'content_aware' in results:
        print("For ServiceNow Data:")
        print("  • Use 'hierarchical' for preserving ticket structure")
        print("  • Use 'content_aware' for separating conversations from metadata")
        print("  • Use 'sliding_window' for conversation analysis with context")
        print("  • Use 'token_aware' for LLM processing with strict size limits")
        print("  • Use 'auto' for general-purpose applications")
    
    print(f"\n🔍 To examine detailed chunk analysis:")
    print(f"   python -m json.tool {output_file}")
    
    return output_file

def analyze_chunk_content():
    """Detailed analysis of what each chunk contains"""
    
    print(f"\n📖 DETAILED CHUNK CONTENT ANALYSIS")
    print("=" * 50)
    
    # Test with hierarchical strategy for detailed analysis
    ticket_file = "/Users/wjackson/Developer/LLNL/data/rhoai-sanitized-main/servicenow/incident_1217.xml"
    
    handler = ServiceNowHandler()
    tree = ET.parse(ticket_file)
    root = tree.getroot()
    analysis_result = handler.analyze(root, ticket_file)
    
    orchestrator = ChunkingOrchestrator()
    config = ChunkingConfig(max_chunk_size=1024)
    
    # Convert analysis_result to dict format
    analysis_dict = {
        'document_type': {'type_name': analysis_result.document_type},
        'key_findings': analysis_result.key_findings,
        'structured_data': analysis_result.structured_data
    }
    
    chunks = orchestrator.chunk_document(ticket_file, analysis_dict, strategy='hierarchical', config=config)
    
    print(f"Analyzing {len(chunks)} hierarchical chunks in detail:")
    print()
    
    for i, chunk in enumerate(chunks, 1):
        print(f"📄 CHUNK {i}: {chunk.chunk_id}")
        print("-" * 30)
        print(f"Element Path: {chunk.element_path}")
        print(f"Token Estimate: {chunk.token_estimate}")
        print(f"Content Length: {len(chunk.content)} characters")
        
        if chunk.metadata:
            print(f"Metadata: {chunk.metadata}")
        
        # Show content with intelligent truncation
        content = chunk.content.strip()
        if len(content) > 200:
            lines = content.split('\n')
            if len(lines) > 5:
                preview_lines = lines[:3] + [f"... ({len(lines)-5} more lines) ..."] + lines[-2:]
                preview = '\n'.join(preview_lines)
            else:
                preview = content[:200] + f"... ({len(content)-200} more chars)"
        else:
            preview = content
        
        print(f"Content Preview:")
        print(f"  {preview}")
        print()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--detailed":
        analyze_chunk_content()
    else:
        output_file = test_chunking_strategies()
        
        # Also run detailed analysis
        if output_file:
            print(f"\n" + "=" * 60)
            analyze_chunk_content()