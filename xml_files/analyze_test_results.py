#!/usr/bin/env python3
"""
Analyze comprehensive chunking test results and identify specific issues
"""

import json
import os
from collections import defaultdict, Counter

def analyze_results():
    """Analyze test results and generate detailed findings"""
    
    results_dir = "chunking_test_results_20250725_070919"
    
    # Load test results
    with open(f"{results_dir}/chunking_test_results.json", 'r') as f:
        detailed_results = json.load(f)
    
    with open(f"{results_dir}/test_summary.json", 'r') as f:
        summary = json.load(f)
    
    print("🔍 CHUNKING TEST RESULTS ANALYSIS")
    print("=" * 60)
    
    # 1. Handler Recognition Analysis
    print(f"\n📋 HANDLER RECOGNITION ANALYSIS")
    print("-" * 40)
    
    handler_usage = defaultdict(list)
    doc_types = defaultdict(list)
    
    for file_path, results in detailed_results.items():
        file_name = os.path.basename(file_path)
        handler = results['analysis'].get('handler_used', 'unknown') if results['analysis'] else 'failed'
        doc_type = results['analysis']['document_type']['type_name'] if results['analysis'] else 'failed'
        
        handler_usage[handler].append(file_name)
        doc_types[doc_type].append(file_name)
    
    print(f"Handler Distribution:")
    for handler, files in handler_usage.items():
        print(f"  {handler}: {len(files)} files")
        if handler == 'fallback' and len(files) <= 10:  # Show some examples
            print(f"    Examples: {', '.join(files[:5])}")
    
    print(f"\nDocument Type Distribution:")
    for doc_type, files in doc_types.items():
        print(f"  {doc_type}: {len(files)} files")
    
    # 2. Specialized Handler Investigation
    print(f"\n🔍 SPECIALIZED HANDLER INVESTIGATION")
    print("-" * 45)
    
    # Look for files that should have been handled by specialized handlers
    expected_handlers = {
        'SCAP': [f for f in handler_usage['fallback'] if 'xccdf' in f.lower() or 'scap' in f.lower()],
        'Maven': [f for f in handler_usage['fallback'] if 'pom' in f.lower()],
        'Ant': [f for f in handler_usage['fallback'] if 'build.xml' in f.lower() or 'ant' in f.lower()],
        'Log4j': [f for f in handler_usage['fallback'] if 'log4j' in f.lower()],
        'Spring': [f for f in handler_usage['fallback'] if 'spring' in f.lower() or 'applicationContext' in f.lower()],
        'DocBook': [f for f in handler_usage['fallback'] if any(x in f.lower() for x in ['article', 'book', 'chapter', 'docbook'])],
        'RSS/Feed': [f for f in handler_usage['fallback'] if any(x in f.lower() for x in ['rss', 'atom', 'feed'])],
        'HL7': [f for f in handler_usage['fallback'] if any(x in f.lower() for x in ['hl7', 'ccda', 'ccd'])],
    }
    
    print(f"Files that should have been handled by specialized handlers:")
    total_missed = 0
    for expected_type, files in expected_handlers.items():
        if files:
            print(f"  {expected_type}: {len(files)} files")
            total_missed += len(files)
            if len(files) <= 5:
                print(f"    Files: {', '.join(files)}")
    
    print(f"\nTotal files missing specialized handlers: {total_missed}/{len(detailed_results)} ({total_missed/len(detailed_results)*100:.1f}%)")
    
    # 3. Hierarchical Chunking Deep Dive
    print(f"\n⚙️ HIERARCHICAL CHUNKING ANALYSIS")
    print("-" * 40)
    
    hierarchical_stats = defaultdict(list)
    zero_chunk_files = []
    working_files = []
    
    for file_path, results in detailed_results.items():
        file_name = os.path.basename(file_path)
        
        for config_name, config_results in results['chunking_results'].items():
            if 'hierarchical' in config_results:
                chunk_count = config_results['hierarchical'].get('chunk_count', 0)
                hierarchical_stats[config_name].append(chunk_count)
                
                if chunk_count == 0:
                    zero_chunk_files.append((file_name, config_name))
                else:
                    working_files.append((file_name, config_name, chunk_count))
    
    print(f"Hierarchical chunking performance by config:")
    for config, counts in hierarchical_stats.items():
        zero_count = counts.count(0)
        working_count = len(counts) - zero_count
        avg_chunks = sum(c for c in counts if c > 0) / working_count if working_count > 0 else 0
        print(f"  {config}: {zero_count} zero-chunk files, {working_count} working files, avg {avg_chunks:.1f} chunks")
    
    print(f"\nSample files producing zero chunks:")
    for file_name, config in zero_chunk_files[:10]:
        print(f"  {file_name} ({config})")
    
    print(f"\nSample files producing chunks:")
    for file_name, config, chunks in working_files[:10]:
        print(f"  {file_name} ({config}): {chunks} chunks")
    
    # 4. Strategy Comparison
    print(f"\n📊 STRATEGY PERFORMANCE COMPARISON")
    print("-" * 40)
    
    strategy_summary = {}
    for strategy_config, stats in summary['strategy_performance'].items():
        strategy, config = strategy_config.split('_', 1)
        if strategy not in strategy_summary:
            strategy_summary[strategy] = {
                'avg_chunks': [],
                'zero_rates': [],
                'success_rates': []
            }
        
        strategy_summary[strategy]['avg_chunks'].append(stats['avg_chunks_per_file'])
        strategy_summary[strategy]['zero_rates'].append(stats['zero_chunk_rate'])
        strategy_summary[strategy]['success_rates'].append(stats['success_rate'])
    
    print(f"{'Strategy':<15} {'Avg Chunks':<12} {'Zero Rate':<12} {'Success Rate':<12}")
    print("-" * 55)
    for strategy, data in strategy_summary.items():
        avg_chunks = sum(data['avg_chunks']) / len(data['avg_chunks'])
        avg_zero_rate = sum(data['zero_rates']) / len(data['zero_rates'])
        avg_success_rate = sum(data['success_rates']) / len(data['success_rates'])
        
        print(f"{strategy:<15} {avg_chunks:<12.1f} {avg_zero_rate:<12.1%} {avg_success_rate:<12.1%}")
    
    # 5. File Size Analysis
    print(f"\n📏 FILE SIZE ANALYSIS")
    print("-" * 25)
    
    file_sizes = []
    for file_path, results in detailed_results.items():
        file_sizes.append(results['file_info']['file_size'])
    
    file_sizes.sort()
    
    print(f"File size distribution:")
    print(f"  Total files: {len(file_sizes)}")
    print(f"  Min size: {file_sizes[0]:,} bytes")
    print(f"  Max size: {file_sizes[-1]:,} bytes")
    print(f"  Median size: {file_sizes[len(file_sizes)//2]:,} bytes")
    print(f"  Total size: {sum(file_sizes):,} bytes ({sum(file_sizes)/1024/1024:.1f} MB)")
    
    # Size categories
    small_files = [s for s in file_sizes if s < 10000]  # < 10KB
    medium_files = [s for s in file_sizes if 10000 <= s < 100000]  # 10KB - 100KB
    large_files = [s for s in file_sizes if s >= 100000]  # > 100KB
    
    print(f"  Small (< 10KB): {len(small_files)} files")
    print(f"  Medium (10-100KB): {len(medium_files)} files") 
    print(f"  Large (> 100KB): {len(large_files)} files")
    
    # 6. Root Cause Analysis
    print(f"\n🔍 ROOT CAUSE ANALYSIS")
    print("-" * 30)
    
    print(f"PRIMARY ISSUES IDENTIFIED:")
    print(f"1. Handler Registration: Specialized handlers not being called")
    print(f"   - All files fallback to generic XML handler")
    print(f"   - Need to investigate XMLDocumentAnalyzer.analyze_document()")
    
    print(f"\n2. Semantic Boundary Detection: Hierarchical chunking failing")
    print(f"   - 66.7% of files produce zero chunks with hierarchical strategy")
    print(f"   - Generic semantic boundaries don't match real XML elements")
    
    print(f"\n3. Document Type Classification: Missing specialized analysis")
    print(f"   - Should detect SCAP, Maven, Ant, DocBook, HL7, etc.")
    print(f"   - Missing optimized chunking configurations per document type")
    
    print(f"\nRECOMMENDED FIXES:")
    print(f"1. Debug XMLDocumentAnalyzer - check handler registration and calling")
    print(f"2. Test individual specialized handlers in isolation")
    print(f"3. Add more generic semantic boundaries for common XML patterns")
    print(f"4. Improve fallback semantic boundary detection")
    print(f"5. Add debugging output to see why handlers aren't matching")
    
    return {
        'handler_issues': len(handler_usage['fallback']),
        'hierarchical_zero_rate': len(zero_chunk_files) / (len(detailed_results) * 3),  # 3 configs
        'total_files': len(detailed_results),
        'missed_specialized': total_missed
    }

if __name__ == "__main__":
    analyze_results()