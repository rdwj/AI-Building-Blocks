#!/usr/bin/env python3
"""
Demo script showing how to use the XML Agent Framework with STIG files

This script demonstrates:
1. Basic document analysis
2. Schema extraction and summarization
3. Chunking strategies
4. LLM prompt generation
5. Integration patterns for agentic systems

Run with: python demo.py /path/to/your/stig/file.xml
"""

import sys
import json
from pathlib import Path
import time

# Import our framework (assumes the framework code is in xml_framework.py)
try:
    from xml_framework import XMLAgentFramework, DocumentTypeDetector
except ImportError:
    print("Error: xml_framework.py not found. Please ensure the framework file is in the same directory.")
    sys.exit(1)

def analyze_stig_file(file_path: str):
    """Demonstrate STIG file analysis"""
    print(f"🔍 Analyzing STIG file: {file_path}")
    print("=" * 60)
    
    # Initialize framework
    framework = XMLAgentFramework(max_chunk_size=8000, max_samples=3)
    
    start_time = time.time()
    
    # Step 1: Quick file info
    file_size = Path(file_path).stat().st_size
    print(f"📁 File size: {file_size / (1024*1024):.2f} MB")
    
    # Step 2: Analyze document schema
    print("\n📋 Extracting document schema...")
    schema = framework.analyze_document(file_path)
    
    print(f"✅ Schema analysis complete!")
    print(f"   Document Type: {schema.document_type}")
    print(f"   Root Element: {schema.root_element}")
    print(f"   Total Elements: {schema.statistics['total_elements']:,}")
    print(f"   Unique Elements: {schema.statistics['unique_elements']}")
    print(f"   Max Depth: {schema.statistics['max_depth']}")
    print(f"   Namespaces: {schema.statistics['namespace_count']}")
    
    # Step 3: Show key elements
    print(f"\n🔑 Top 10 Most Frequent Elements:")
    sorted_elements = sorted(schema.elements.items(), 
                           key=lambda x: x[1].count, reverse=True)[:10]
    
    for i, (tag, element) in enumerate(sorted_elements, 1):
        ns_info = f" ({element.namespace}:)" if element.namespace else ""
        attr_count = len(element.attributes)
        child_count = len(element.child_elements)
        
        print(f"   {i:2d}. {tag}{ns_info}: {element.count:,} occurrences")
        print(f"       Attributes: {attr_count}, Children: {child_count}")
        
        if element.text_samples:
            sample = element.text_samples[0][:60].replace('\n', ' ')
            print(f"       Sample text: \"{sample}...\"")
    
    # Step 4: Namespace analysis
    print(f"\n🌐 Namespace Analysis:")
    for prefix, uri in schema.namespaces.items():
        print(f"   {prefix:12s}: {uri}")
    
    # Step 5: Create chunks
    print(f"\n📦 Creating document chunks...")
    chunks = framework.chunk_document(file_path, schema)
    
    total_chunk_size = sum(chunk.size_bytes for chunk in chunks)
    print(f"✅ Created {len(chunks)} chunks")
    print(f"   Total chunk size: {total_chunk_size / (1024*1024):.2f} MB")
    print(f"   Average chunk size: {total_chunk_size / len(chunks) / 1024:.1f} KB")
    
    # Show chunk details
    print(f"\n📊 Chunk Breakdown:")
    for i, chunk in enumerate(chunks[:5]):  # Show first 5
        print(f"   Chunk {i+1}: {chunk.chunk_id}")
        print(f"     Size: {chunk.size_bytes / 1024:.1f} KB")
        print(f"     Lines: {chunk.line_range[0]}-{chunk.line_range[1]}")
        print(f"     Path: {chunk.element_path}")
        print(f"     Elements: {', '.join(chunk.elements_contained[:3])}...")
    
    if len(chunks) > 5:
        print(f"   ... and {len(chunks) - 5} more chunks")
    
    # Step 6: Generate LLM prompts
    print(f"\n🤖 Generating LLM prompts...")
    prompts = framework.generate_llm_prompts(schema, chunks, file_path)
    
    print(f"✅ Generated {len(prompts)} prompts:")
    for prompt_name in prompts.keys():
        prompt_size = len(prompts[prompt_name])
        print(f"   - {prompt_name}: {prompt_size:,} characters")
    
    # Step 7: Processing strategy
    strategy = framework._suggest_processing_strategy(schema)
    print(f"\n🎯 Suggested Processing Strategy:")
    print(f"   Approach: {strategy['approach']}")
    print(f"   Key Elements: {', '.join(strategy['key_elements'])}")
    print(f"   Pattern: {strategy['extraction_pattern']}")
    
    analysis_time = time.time() - start_time
    print(f"\n⏱️  Analysis completed in {analysis_time:.2f} seconds")
    
    return schema, chunks, prompts, strategy

def demonstrate_llm_integration(prompts: dict, schema, chunks):
    """Show how to integrate with LLM for semantic understanding"""
    
    print(f"\n🧠 LLM Integration Demonstration")
    print("=" * 60)
    
    # Show what you'd send to the LLM for schema analysis
    print(f"\n1️⃣  SCHEMA ANALYSIS PROMPT:")
    print("-" * 40)
    schema_prompt = prompts['schema_analysis']
    print(f"Prompt length: {len(schema_prompt):,} characters")
    print(f"First 500 characters:")
    print(schema_prompt[:500] + "...")
    
    print(f"\n🎯 This prompt would help the LLM understand:")
    print("   • Document purpose and structure")
    print("   • Key data entities and relationships") 
    print("   • Optimal processing strategies")
    print("   • Security/compliance considerations")
    
    # Show chunk analysis approach
    if any(key.startswith('chunk_') for key in prompts.keys()):
        print(f"\n2️⃣  CHUNK ANALYSIS APPROACH:")
        print("-" * 40)
        
        chunk_keys = [k for k in prompts.keys() if k.startswith('chunk_')]
        print(f"Total chunks for LLM processing: {len(chunk_keys)}")
        
        if chunk_keys:
            first_chunk_prompt = prompts[chunk_keys[0]]
            print(f"Sample chunk prompt length: {len(first_chunk_prompt):,} characters")
            print(f"First 300 characters of chunk prompt:")
            print(first_chunk_prompt[:300] + "...")
    
    # Show integration patterns
    print(f"\n3️⃣  INTEGRATION PATTERNS:")
    print("-" * 40)
    print("   Sequential Processing:")
    print("     1. Send schema prompt → Get document understanding")
    print("     2. Send chunk prompts → Extract structured data")
    print("     3. Aggregate results → Build complete picture")
    print()
    print("   Parallel Processing:")
    print("     1. Send schema prompt to one LLM instance")
    print("     2. Send chunk prompts to multiple instances")
    print("     3. Combine results using schema context")
    print()
    print("   Adaptive Processing:")
    print("     1. Use schema analysis to identify key sections")
    print("     2. Prioritize chunks with important elements")
    print("     3. Apply document-specific extraction rules")

def save_analysis_results(file_path: str, schema, chunks, prompts, strategy):
    """Save analysis results for later use"""
    
    output_dir = Path(file_path).parent / "xml_analysis"
    output_dir.mkdir(exist_ok=True)
    
    base_name = Path(file_path).stem
    
    # Save schema summary
    schema_file = output_dir / f"{base_name}_schema.json"
    schema_data = {
        'document_type': schema.document_type,
        'root_element': schema.root_element,
        'statistics': schema.statistics,
        'namespaces': schema.namespaces,
        'top_elements': [
            {
                'tag': tag,
                'count': element.count,
                'namespace': element.namespace,
                'attributes': list(element.attributes.keys()),
                'has_text': len(element.text_samples) > 0
            }
            for tag, element in sorted(schema.elements.items(), 
                                     key=lambda x: x[1].count, reverse=True)[:20]
        ],
        'processing_strategy': strategy
    }
    
    with open(schema_file, 'w') as f:
        json.dump(schema_data, f, indent=2)
    
    # Save chunk metadata
    chunks_file = output_dir / f"{base_name}_chunks.json"
    chunks_data = [
        {
            'chunk_id': chunk.chunk_id,
            'element_path': chunk.element_path,
            'line_range': chunk.line_range,
            'size_bytes': chunk.size_bytes,
            'elements_contained': chunk.elements_contained,
            'summary': chunk.summary
        }
        for chunk in chunks
    ]
    
    with open(chunks_file, 'w') as f:
        json.dump(chunks_data, f, indent=2)
    
    # Save prompts
    prompts_dir = output_dir / f"{base_name}_prompts"
    prompts_dir.mkdir(exist_ok=True)
    
    for prompt_name, prompt_content in prompts.items():
        prompt_file = prompts_dir / f"{prompt_name}.txt"
        with open(prompt_file, 'w') as f:
            f.write(prompt_content)
    
    print(f"\n💾 Analysis results saved to: {output_dir}")
    print(f"   📋 Schema: {schema_file.name}")
    print(f"   📦 Chunks: {chunks_file.name}")
    print(f"   🤖 Prompts: {prompts_dir.name}/ ({len(prompts)} files)")

def main():
    """Main demonstration function"""
    
    if len(sys.argv) < 2:
        print("Usage: python demo.py <xml_file_path>")
        print("\nExample:")
        print("  python demo.py /path/to/stig-file.xml")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not Path(file_path).exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    try:
        # Run the analysis
        schema, chunks, prompts, strategy = analyze_stig_file(file_path)
        
        # Demonstrate LLM integration
        demonstrate_llm_integration(prompts, schema, chunks)
        
        # Save results
        save_analysis_results(file_path, schema, chunks, prompts, strategy)
        
        print(f"\n🎉 Analysis complete! You now have:")
        print("   ✅ Deterministic schema extraction")
        print("   ✅ Intelligent document chunking") 
        print("   ✅ LLM-ready prompts for semantic analysis")
        print("   ✅ Processing strategy recommendations")
        print("\n💡 Next steps for your agentic framework:")
        print("   1. Send the schema prompt to your LLM")
        print("   2. Use the response to refine chunk processing")
        print("   3. Process chunks in parallel for efficiency")
        print("   4. Aggregate results for final analysis")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()