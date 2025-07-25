#!/usr/bin/env python3
"""
Comprehensive test of all XML handlers against all sample data files
"""
import sys
import os
from pathlib import Path
import time
from collections import defaultdict

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def is_xml_file(file_path):
    """Check if file is an XML file by extension"""
    xml_extensions = {'.xml', '.xlf', '.xliff', '.xsd', '.wsdl', '.svg', '.kml', 
                     '.gpx', '.rss', '.atom', '.xhtml', '.html', '.pom', '.wadl'}
    return Path(file_path).suffix.lower() in xml_extensions

def get_file_size_category(size_bytes):
    """Categorize file by size"""
    if size_bytes < 1024:
        return "tiny"
    elif size_bytes < 10 * 1024:
        return "small"
    elif size_bytes < 100 * 1024:
        return "medium" 
    elif size_bytes < 1024 * 1024:
        return "large"
    else:
        return "huge"

def test_all_sample_data():
    """Test all XML files in sample_data directory"""
    
    try:
        from core.analyzer import XMLDocumentAnalyzer
        print("✅ XMLDocumentAnalyzer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import XMLDocumentAnalyzer: {e}")
        return False
    
    # Find all XML files
    sample_data_dir = Path("sample_data")
    if not sample_data_dir.exists():
        print("❌ sample_data directory not found")
        return False
    
    xml_files = []
    for file_path in sample_data_dir.rglob("*"):
        if file_path.is_file() and is_xml_file(file_path):
            xml_files.append(file_path)
    
    if not xml_files:
        print("❌ No XML files found in sample_data directory")
        return False
    
    print(f"🔍 Found {len(xml_files)} XML files to test")
    
    # Initialize analyzer
    analyzer = XMLDocumentAnalyzer()
    
    # Test results tracking
    results = {
        'total_files': len(xml_files),
        'successful': 0,
        'failed': 0,
        'errors': [],
        'handler_usage': defaultdict(int),
        'document_types': defaultdict(int),
        'size_categories': defaultdict(int),
        'processing_times': [],
        'file_results': []
    }
    
    print(f"\n🧪 Testing {len(xml_files)} XML files...")
    print("=" * 80)
    
    for i, file_path in enumerate(xml_files, 1):
        try:
            relative_path = file_path.relative_to(Path.cwd())
        except ValueError:
            relative_path = file_path
        file_size = file_path.stat().st_size
        size_category = get_file_size_category(file_size)
        results['size_categories'][size_category] += 1
        
        print(f"[{i:3d}/{len(xml_files)}] {relative_path} ({file_size:,} bytes)")
        
        start_time = time.time()
        
        try:
            # Analyze the file
            result = analyzer.analyze_document(str(file_path))
            processing_time = time.time() - start_time
            results['processing_times'].append(processing_time)
            
            if 'error' in result:
                print(f"    ❌ Error: {result['error']}")
                results['failed'] += 1
                results['errors'].append({
                    'file': str(relative_path),
                    'error': result['error']
                })
            else:
                handler_used = result.get('handler_used', 'Unknown')
                confidence = result.get('confidence', 0.0)
                analysis = result.get('analysis')
                
                if analysis:
                    doc_type = analysis.document_type
                    ai_use_cases = len(analysis.ai_use_cases) if hasattr(analysis, 'ai_use_cases') else 0
                    quality_score = analysis.quality_metrics.get('overall', 0.0) if hasattr(analysis, 'quality_metrics') else 0.0
                    
                    print(f"    ✅ {handler_used} (conf: {confidence:.2f}) → {doc_type}")
                    print(f"        Quality: {quality_score:.2f}, AI use cases: {ai_use_cases}, Time: {processing_time:.3f}s")
                    
                    results['successful'] += 1
                    results['handler_usage'][handler_used] += 1
                    results['document_types'][doc_type] += 1
                    
                    results['file_results'].append({
                        'file': str(relative_path),
                        'handler': handler_used,
                        'document_type': doc_type,
                        'confidence': confidence,
                        'quality_score': quality_score,
                        'ai_use_cases': ai_use_cases,
                        'processing_time': processing_time,
                        'file_size': file_size,
                        'size_category': size_category
                    })
                else:
                    print(f"    ❌ No analysis result from {handler_used}")
                    results['failed'] += 1
                    results['errors'].append({
                        'file': str(relative_path),
                        'error': 'No analysis result returned'
                    })
                    
        except Exception as e:
            processing_time = time.time() - start_time
            print(f"    ❌ Exception: {e}")
            results['failed'] += 1
            results['errors'].append({
                'file': str(relative_path),
                'error': str(e)
            })
    
    # Print comprehensive results
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 80)
    
    success_rate = (results['successful'] / results['total_files']) * 100
    print(f"Overall Success Rate: {success_rate:.1f}% ({results['successful']}/{results['total_files']})")
    print(f"Total Processing Time: {sum(results['processing_times']):.2f}s")
    if results['processing_times']:
        avg_time = sum(results['processing_times']) / len(results['processing_times'])
        print(f"Average Processing Time: {avg_time:.3f}s per file")
    
    # Handler usage statistics
    print(f"\n🔧 Handler Usage Statistics:")
    sorted_handlers = sorted(results['handler_usage'].items(), key=lambda x: x[1], reverse=True)
    for handler, count in sorted_handlers:
        percentage = (count / results['successful']) * 100 if results['successful'] > 0 else 0
        print(f"  {handler}: {count} files ({percentage:.1f}%)")
    
    # Document type distribution
    print(f"\n📋 Document Type Distribution:")
    sorted_types = sorted(results['document_types'].items(), key=lambda x: x[1], reverse=True)
    for doc_type, count in sorted_types:
        percentage = (count / results['successful']) * 100 if results['successful'] > 0 else 0
        print(f"  {doc_type}: {count} files ({percentage:.1f}%)")
    
    # File size distribution
    print(f"\n📏 File Size Distribution:")
    size_order = ['tiny', 'small', 'medium', 'large', 'huge']
    for size_cat in size_order:
        count = results['size_categories'].get(size_cat, 0)
        if count > 0:
            percentage = (count / results['total_files']) * 100
            print(f"  {size_cat.capitalize()}: {count} files ({percentage:.1f}%)")
    
    # Performance analysis
    if results['file_results']:
        print(f"\n⚡ Performance Analysis:")
        # Best performing handlers (by average processing time)
        handler_times = defaultdict(list)
        for result in results['file_results']:
            handler_times[result['handler']].append(result['processing_time'])
        
        handler_avg_times = {
            handler: sum(times) / len(times) 
            for handler, times in handler_times.items()
        }
        sorted_performance = sorted(handler_avg_times.items(), key=lambda x: x[1])
        
        print("  Fastest Handlers (avg time):")
        for handler, avg_time in sorted_performance[:5]:
            count = len(handler_times[handler])
            print(f"    {handler}: {avg_time:.3f}s avg ({count} files)")
    
    # Quality analysis
    if results['file_results']:
        print(f"\n🏆 Quality Analysis:")
        quality_scores = [r['quality_score'] for r in results['file_results'] if r['quality_score'] > 0]
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
            max_quality = max(quality_scores)
            min_quality = min(quality_scores)
            print(f"  Average Quality Score: {avg_quality:.2f}")
            print(f"  Quality Range: {min_quality:.2f} - {max_quality:.2f}")
            
            # Best quality files
            best_files = sorted(results['file_results'], key=lambda x: x['quality_score'], reverse=True)[:5]
            print("  Highest Quality Files:")
            for result in best_files:
                if result['quality_score'] > 0:
                    print(f"    {result['file']}: {result['quality_score']:.2f} ({result['document_type']})")
    
    # Error analysis
    if results['errors']:
        print(f"\n❌ Error Analysis ({len(results['errors'])} errors):")
        error_types = defaultdict(int)
        for error in results['errors']:
            error_msg = error['error']
            # Categorize common errors
            if 'parse' in error_msg.lower():
                error_types['Parse Errors'] += 1
            elif 'not found' in error_msg.lower():
                error_types['File Not Found'] += 1
            elif 'permission' in error_msg.lower():
                error_types['Permission Errors'] += 1
            else:
                error_types['Other Errors'] += 1
        
        for error_type, count in error_types.items():
            print(f"  {error_type}: {count}")
        
        # Show first few errors for debugging
        print("  Sample Errors:")
        for error in results['errors'][:3]:
            print(f"    {error['file']}: {error['error']}")
    
    print(f"\n{'='*80}")
    if success_rate >= 90:
        print("🎉 EXCELLENT! Very high success rate")
    elif success_rate >= 75:
        print("✅ GOOD! High success rate")
    elif success_rate >= 50:
        print("⚠️  MODERATE success rate - room for improvement")
    else:
        print("❌ LOW success rate - needs attention")
    
    return success_rate >= 75

if __name__ == "__main__":
    print("🧪 COMPREHENSIVE XML HANDLER TEST")
    print("Testing all handlers against all sample data files")
    print("=" * 80)
    
    success = test_all_sample_data()
    
    if success:
        print("\n🎉 Overall test PASSED!")
        sys.exit(0)
    else:
        print("\n❌ Overall test had issues - check results above")
        sys.exit(1)