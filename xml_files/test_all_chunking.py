#!/usr/bin/env python3
"""
Comprehensive Chunking Test Suite

Tests all chunking strategies against all XML files in sample_data directory.
Saves detailed results including chunks, metadata, and analysis for review.
"""

import sys
import os
import json
import glob
import traceback
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.chunking import ChunkingOrchestrator, ChunkingConfig
from core.analyzer import XMLDocumentAnalyzer

def create_output_directory():
    """Create timestamped output directory for test results"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = f"chunking_test_results_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def find_all_xml_files(base_dir="sample_data"):
    """Find all XML files in the sample data directory"""
    xml_files = []
    
    # Common XML file patterns
    patterns = [
        "**/*.xml",
        "**/*.xsd", 
        "**/*.xccdf",
        "**/*.rss",
        "**/*.atom",
        "**/*.pom"
    ]
    
    for pattern in patterns:
        files = glob.glob(os.path.join(base_dir, pattern), recursive=True)
        xml_files.extend(files)
    
    # Remove duplicates and sort
    xml_files = sorted(list(set(xml_files)))
    
    return xml_files

def analyze_file_with_handlers(file_path):
    """Analyze file using specialized handlers"""
    try:
        analyzer = XMLDocumentAnalyzer()
        analysis = analyzer.analyze_document(file_path)
        
        # Handle the dict format returned by core.analyzer.XMLDocumentAnalyzer
        if isinstance(analysis, dict):
            # Extract document type info (could be DocumentTypeInfo object or dict)
            doc_type_info = analysis.get('document_type', {})
            if hasattr(doc_type_info, 'type_name'):
                # It's a DocumentTypeInfo object
                doc_type = doc_type_info.type_name
                confidence = doc_type_info.confidence
            else:
                # It's already a dict
                doc_type = doc_type_info.get('type_name', 'Generic XML')
                confidence = doc_type_info.get('confidence', 0.5)
            
            analysis_dict = {
                'document_type': {'type_name': doc_type, 'confidence': confidence},
                'key_findings': analysis.get('key_findings', {}),
                'structured_data': analysis.get('structured_data', {}),
                'handler_used': analysis.get('handler_used', 'unknown')
            }
        else:
            # Legacy: SpecializedAnalysis object format
            analysis_dict = {
                'document_type': {
                    'type_name': analysis.document_type,
                    'confidence': analysis.confidence
                },
                'key_findings': analysis.key_findings,
                'structured_data': analysis.structured_data,
                'handler_used': getattr(analysis, 'handler_used', 'unknown')
            }
        return analysis_dict, None
        
    except Exception as e:
        # Fallback: basic XML analysis
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            element_counts = {}
            for elem in root.iter():
                tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                element_counts[tag] = element_counts.get(tag, 0) + 1
            
            analysis_dict = {
                'document_type': {'type_name': 'Generic XML', 'confidence': 0.5},
                'key_findings': {'total_elements': len(list(root.iter()))},
                'structured_data': {'element_distribution': element_counts},
                'handler_used': 'fallback'
            }
            return analysis_dict, None
            
        except Exception as parse_error:
            return None, str(parse_error)

def test_chunking_strategies(file_path, analysis_dict, output_dir):
    """Test all chunking strategies on a file"""
    
    file_results = {
        'file_info': {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'file_size': os.path.getsize(file_path),
            'analysis_timestamp': datetime.now().isoformat()
        },
        'analysis': analysis_dict,
        'chunking_results': {},
        'errors': {}
    }
    
    # Test configurations
    test_configs = {
        'small': ChunkingConfig(max_chunk_size=1000, min_chunk_size=100, overlap_size=50),
        'medium': ChunkingConfig(max_chunk_size=2000, min_chunk_size=200, overlap_size=100),
        'large': ChunkingConfig(max_chunk_size=4000, min_chunk_size=500, overlap_size=200)
    }
    
    strategies = ['hierarchical', 'sliding_window', 'content_aware', 'auto']
    orchestrator = ChunkingOrchestrator()
    
    for config_name, config in test_configs.items():
        file_results['chunking_results'][config_name] = {}
        
        for strategy in strategies:
            strategy_key = f"{strategy}_{config_name}"
            
            try:
                print(f"      Testing {strategy} with {config_name} config...")
                
                chunks = orchestrator.chunk_document(
                    file_path,
                    analysis_dict,
                    strategy=strategy,
                    config=config
                )
                
                # Calculate statistics
                if chunks:
                    token_counts = [chunk.token_estimate for chunk in chunks]
                    content_lengths = [len(chunk.content) for chunk in chunks]
                    
                    stats = {
                        'chunk_count': len(chunks),
                        'total_tokens': sum(token_counts),
                        'avg_tokens': sum(token_counts) / len(chunks),
                        'min_tokens': min(token_counts),
                        'max_tokens': max(token_counts),
                        'total_content_length': sum(content_lengths),
                        'avg_content_length': sum(content_lengths) / len(chunks),
                        'unique_elements': len(set().union(*[chunk.elements_included for chunk in chunks if chunk.elements_included])),
                        'unique_paths': len(set(chunk.element_path for chunk in chunks if chunk.element_path))
                    }
                    
                    # Save detailed chunks to separate file
                    chunks_file = f"{os.path.basename(file_path)}_{strategy_key}_chunks.json"
                    chunks_path = os.path.join(output_dir, 'chunks', chunks_file)
                    os.makedirs(os.path.dirname(chunks_path), exist_ok=True)
                    
                    chunks_data = {
                        'metadata': {
                            'file_path': file_path,
                            'strategy': strategy,
                            'config': config_name,
                            'chunk_count': len(chunks)
                        },
                        'chunks': []
                    }
                    
                    for i, chunk in enumerate(chunks):
                        chunk_data = {
                            'chunk_number': i + 1,
                            'chunk_id': chunk.chunk_id,
                            'element_path': chunk.element_path,
                            'token_estimate': chunk.token_estimate,
                            'content_length': len(chunk.content),
                            'elements_included': chunk.elements_included,
                            'metadata': chunk.metadata,
                            'full_content': chunk.content
                        }
                        chunks_data['chunks'].append(chunk_data)
                    
                    with open(chunks_path, 'w', encoding='utf-8') as f:
                        json.dump(chunks_data, f, indent=2, ensure_ascii=False)
                    
                    stats['chunks_file'] = chunks_file
                    
                else:
                    stats = {
                        'chunk_count': 0,
                        'total_tokens': 0,
                        'avg_tokens': 0,
                        'min_tokens': 0,
                        'max_tokens': 0,
                        'total_content_length': 0,
                        'avg_content_length': 0,
                        'unique_elements': 0,
                        'unique_paths': 0,
                        'chunks_file': None
                    }
                
                file_results['chunking_results'][config_name][strategy] = stats
                
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                file_results['errors'][strategy_key] = error_msg
                print(f"        ❌ Error: {error_msg}")
                
                # Store failed result
                file_results['chunking_results'][config_name][strategy] = {
                    'chunk_count': 0,
                    'error': error_msg
                }
    
    return file_results

def generate_summary_report(all_results, output_dir):
    """Generate comprehensive summary report"""
    
    summary = {
        'test_info': {
            'timestamp': datetime.now().isoformat(),
            'total_files_tested': len(all_results),
            'output_directory': output_dir
        },
        'file_summary': {},
        'strategy_performance': {},
        'document_type_analysis': {},
        'error_analysis': {},
        'recommendations': []
    }
    
    # Analyze by file
    for file_path, results in all_results.items():
        file_name = os.path.basename(file_path)
        doc_type = results['analysis']['document_type']['type_name']
        
        summary['file_summary'][file_name] = {
            'document_type': doc_type,
            'file_size': results['file_info']['file_size'],
            'handler_used': results['analysis'].get('handler_used', 'unknown'),
            'strategies_tested': len([s for config in results['chunking_results'].values() for s in config.keys()]),
            'errors': len(results['errors'])
        }
        
        # Analyze by document type
        if doc_type not in summary['document_type_analysis']:
            summary['document_type_analysis'][doc_type] = {
                'file_count': 0,
                'total_size': 0,
                'strategy_success_rates': {}
            }
        
        summary['document_type_analysis'][doc_type]['file_count'] += 1
        summary['document_type_analysis'][doc_type]['total_size'] += results['file_info']['file_size']
    
    # Analyze strategy performance
    strategy_stats = {}
    
    for file_path, results in all_results.items():
        for config_name, config_results in results['chunking_results'].items():
            for strategy, stats in config_results.items():
                key = f"{strategy}_{config_name}"
                
                if key not in strategy_stats:
                    strategy_stats[key] = {
                        'files_tested': 0,
                        'successful_runs': 0,
                        'total_chunks': 0,
                        'total_tokens': 0,
                        'zero_chunk_files': 0
                    }
                
                strategy_stats[key]['files_tested'] += 1
                
                if 'error' not in stats:
                    strategy_stats[key]['successful_runs'] += 1
                    strategy_stats[key]['total_chunks'] += stats.get('chunk_count', 0)
                    strategy_stats[key]['total_tokens'] += stats.get('total_tokens', 0)
                    
                    if stats.get('chunk_count', 0) == 0:
                        strategy_stats[key]['zero_chunk_files'] += 1
    
    # Calculate success rates and averages
    for key, stats in strategy_stats.items():
        if stats['files_tested'] > 0:
            stats['success_rate'] = stats['successful_runs'] / stats['files_tested']
            stats['avg_chunks_per_file'] = stats['total_chunks'] / stats['successful_runs'] if stats['successful_runs'] > 0 else 0
            stats['avg_tokens_per_file'] = stats['total_tokens'] / stats['successful_runs'] if stats['successful_runs'] > 0 else 0
            stats['zero_chunk_rate'] = stats['zero_chunk_files'] / stats['successful_runs'] if stats['successful_runs'] > 0 else 0
    
    summary['strategy_performance'] = strategy_stats
    
    # Collect all errors
    all_errors = {}
    for file_path, results in all_results.items():
        for strategy_config, error in results['errors'].items():
            if error not in all_errors:
                all_errors[error] = []
            all_errors[error].append((file_path, strategy_config))
    
    summary['error_analysis'] = {
        error: {
            'occurrence_count': len(files),
            'affected_files': [{'file': os.path.basename(f[0]), 'strategy_config': f[1]} for f in files]
        }
        for error, files in all_errors.items()
    }
    
    # Generate recommendations
    recommendations = []
    
    # Check for strategies with high zero-chunk rates
    for key, stats in strategy_stats.items():
        if stats.get('zero_chunk_rate', 0) > 0.3:  # More than 30% zero chunks
            recommendations.append(f"Strategy '{key}' produces zero chunks for {stats['zero_chunk_rate']:.1%} of files - needs investigation")
    
    # Check for strategies with low success rates
    for key, stats in strategy_stats.items():
        if stats.get('success_rate', 0) < 0.8:  # Less than 80% success
            recommendations.append(f"Strategy '{key}' has low success rate ({stats['success_rate']:.1%}) - check error handling")
    
    # Check for document types without proper handlers
    for doc_type, info in summary['document_type_analysis'].items():
        generic_files = [f for f, data in summary['file_summary'].items() 
                        if data['document_type'] == doc_type and data['handler_used'] in ['fallback', 'unknown']]
        if generic_files and doc_type != 'Generic XML':
            recommendations.append(f"Document type '{doc_type}' using generic handler - consider specialized handler")
    
    summary['recommendations'] = recommendations
    
    return summary

def main():
    """Main test execution"""
    
    print("🧪 COMPREHENSIVE XML CHUNKING TEST SUITE")
    print("=" * 60)
    
    # Create output directory
    output_dir = create_output_directory()
    print(f"📁 Output directory: {output_dir}")
    
    # Find all XML files
    print(f"\n🔍 Discovering XML files...")
    xml_files = find_all_xml_files()
    print(f"   Found {len(xml_files)} XML files")
    
    # Show file distribution
    file_types = {}
    for file_path in xml_files:
        ext = Path(file_path).suffix.lower()
        file_types[ext] = file_types.get(ext, 0) + 1
    
    print(f"   File types: {dict(sorted(file_types.items()))}")
    
    # Test each file
    print(f"\n🧪 Testing chunking strategies...")
    all_results = {}
    
    for i, file_path in enumerate(xml_files, 1):
        print(f"\n📄 [{i}/{len(xml_files)}] {file_path}")
        
        # Analyze file
        print(f"   🔍 Analyzing document...")
        analysis_dict, error = analyze_file_with_handlers(file_path)
        
        if error:
            print(f"   ❌ Analysis failed: {error}")
            all_results[file_path] = {
                'file_info': {
                    'file_path': file_path,
                    'file_name': os.path.basename(file_path),
                    'file_size': os.path.getsize(file_path),
                    'analysis_timestamp': datetime.now().isoformat()
                },
                'analysis': None,
                'chunking_results': {},
                'errors': {'analysis': error}
            }
            continue
        
        doc_type = analysis_dict['document_type']['type_name']
        handler = analysis_dict.get('handler_used', 'unknown')
        print(f"   📋 Document type: {doc_type} (handler: {handler})")
        
        # Test chunking
        print(f"   ⚙️ Testing chunking strategies...")
        try:
            file_results = test_chunking_strategies(file_path, analysis_dict, output_dir)
            all_results[file_path] = file_results
            
            # Quick summary
            total_strategies = sum(len(config) for config in file_results['chunking_results'].values())
            successful_strategies = total_strategies - len(file_results['errors'])
            print(f"   ✅ Completed: {successful_strategies}/{total_strategies} strategies successful")
            
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
            traceback.print_exc()
    
    # Generate summary report
    print(f"\n📊 Generating summary report...")
    summary = generate_summary_report(all_results, output_dir)
    
    # Save all results
    results_file = os.path.join(output_dir, 'chunking_test_results.json')
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
    
    summary_file = os.path.join(output_dir, 'test_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
    
    # Generate human-readable report
    report_file = os.path.join(output_dir, 'README.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# XML Chunking Test Results\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Files Tested:** {len(xml_files)}\n\n")
        
        f.write(f"## Summary Statistics\n\n")
        f.write(f"| Metric | Value |\n")
        f.write(f"|--------|-------|\n")
        f.write(f"| Total Files | {summary['test_info']['total_files_tested']} |\n")
        f.write(f"| Document Types | {len(summary['document_type_analysis'])} |\n")
        f.write(f"| Strategy Configs | {len(summary['strategy_performance'])} |\n")
        f.write(f"| Unique Errors | {len(summary['error_analysis'])} |\n\n")
        
        f.write(f"## Strategy Performance\n\n")
        f.write(f"| Strategy | Success Rate | Avg Chunks/File | Zero Chunk Rate |\n")
        f.write(f"|----------|--------------|-----------------|------------------|\n")
        for strategy, stats in sorted(summary['strategy_performance'].items()):
            success_rate = f"{stats.get('success_rate', 0):.1%}"
            avg_chunks = f"{stats.get('avg_chunks_per_file', 0):.1f}"
            zero_rate = f"{stats.get('zero_chunk_rate', 0):.1%}"
            f.write(f"| {strategy} | {success_rate} | {avg_chunks} | {zero_rate} |\n")
        f.write(f"\n")
        
        f.write(f"## Document Types\n\n")
        f.write(f"| Type | Files | Total Size |\n")
        f.write(f"|------|-------|------------|\n")
        for doc_type, info in sorted(summary['document_type_analysis'].items()):
            size_mb = info['total_size'] / 1024 / 1024
            f.write(f"| {doc_type} | {info['file_count']} | {size_mb:.1f} MB |\n")
        f.write(f"\n")
        
        if summary['recommendations']:
            f.write(f"## Recommendations\n\n")
            for rec in summary['recommendations']:
                f.write(f"- {rec}\n")
            f.write(f"\n")
        
        f.write(f"## Files\n\n")
        f.write(f"- `chunking_test_results.json` - Complete detailed results\n")
        f.write(f"- `test_summary.json` - Summary statistics and analysis\n")
        f.write(f"- `chunks/` - Individual chunk files for each test\n")
    
    print(f"\n✅ TESTING COMPLETE")
    print(f"📁 Results saved in: {output_dir}")
    print(f"📊 Files generated:")
    print(f"   - {results_file}")
    print(f"   - {summary_file}")
    print(f"   - {report_file}")
    print(f"   - chunks/ directory with {len(xml_files)} * 12 chunk files")
    
    if summary['recommendations']:
        print(f"\n💡 Key Recommendations:")
        for rec in summary['recommendations'][:5]:  # Show first 5
            print(f"   - {rec}")
        if len(summary['recommendations']) > 5:
            print(f"   ... and {len(summary['recommendations']) - 5} more (see report)")
    
    print(f"\n🔍 Next steps:")
    print(f"   1. Review {report_file}")
    print(f"   2. Examine failed strategies in test_summary.json")
    print(f"   3. Check specific chunk outputs in chunks/ directory")
    print(f"   4. Address recommendations and retest")

if __name__ == "__main__":
    main()