#!/usr/bin/env python3
"""
Test script for Sitemap Handler
Tests the Sitemap handler against synthetic test files.
"""

import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

# Test individual handler
try:
    from handlers.sitemap_handler import SitemapHandler
    print("✅ SitemapHandler imported successfully")
except ImportError as e:
    print(f"❌ Failed to import SitemapHandler: {e}")
    sys.exit(1)

def test_handler():
    """Test the Sitemap handler with synthetic files"""
    
    handler = SitemapHandler()
    test_files_dir = Path("../../sample_data/test_files_synthetic/small/sitemap")
    
    if not test_files_dir.exists():
        print(f"❌ Test files directory not found: {test_files_dir}")
        return False
    
    sitemap_files = list(test_files_dir.glob("*.xml"))
    if not sitemap_files:
        print(f"❌ No Sitemap files found in {test_files_dir}")
        return False
    
    print(f"\n🔍 Testing Sitemap handler with {len(sitemap_files)} files...")
    
    success_count = 0
    total_count = len(sitemap_files)
    
    for sitemap_file in sitemap_files:
        print(f"\n📄 Testing: {sitemap_file.name}")
        
        try:
            # Parse the XML file
            tree = ET.parse(sitemap_file)
            root = tree.getroot()
            
            # Extract namespaces
            namespaces = {}
            for key, value in root.attrib.items():
                if key.startswith('xmlns'):
                    prefix = key.split(':')[1] if ':' in key else 'default'
                    namespaces[prefix] = value
            
            # Test can_handle
            can_handle, confidence = handler.can_handle(root, namespaces)
            print(f"  ✓ can_handle: {can_handle} (confidence: {confidence:.1f})")
            
            if not can_handle:
                print(f"  ❌ Handler cannot handle this file")
                continue
            
            # Test detect_type
            doc_type = handler.detect_type(root, namespaces)
            print(f"  ✓ detect_type: {doc_type.type_name} (v{doc_type.version})")
            print(f"    - Sitemap type: {doc_type.metadata.get('sitemap_type', 'unknown')}")
            
            # Test extract_key_data
            key_data = handler.extract_key_data(root)
            print(f"  ✓ extract_key_data: {len(key_data)} sections")
            
            # Test full analysis
            analysis = handler.analyze(root, str(sitemap_file))
            print(f"  ✓ analyze: {analysis.document_type}")
            print(f"    - Key findings: {len(analysis.key_findings)} sections")
            print(f"    - Recommendations: {len(analysis.recommendations)} items")
            print(f"    - AI use cases: {len(analysis.ai_use_cases)} cases")
            print(f"    - Data inventory: {sum(analysis.data_inventory.values())} items")
            print(f"    - Quality score: {analysis.quality_metrics.get('overall', 0):.2f}")
            
            # Test specific Sitemap analysis
            sitemap_info = analysis.key_findings.get('sitemap_info', {})
            print(f"    - Sitemap type: {sitemap_info.get('type', 'Unknown')}")
            
            content_analysis = analysis.key_findings.get('content_analysis', {})
            if 'url_count' in content_analysis:
                print(f"    - URLs found: {content_analysis.get('url_count', 0)}")
                
                priorities = content_analysis.get('priorities', {})
                print(f"    - Priority values: {len(priorities)} different")
                
                changefreqs = content_analysis.get('change_frequencies', {})
                print(f"    - Change frequencies: {len(changefreqs)} different")
                
                lastmod = content_analysis.get('last_modified', {})
                print(f"    - URLs with lastmod: {lastmod.get('count', 0)}")
            
            if 'sitemap_count' in content_analysis:
                print(f"    - Sitemaps in index: {content_analysis.get('sitemap_count', 0)}")
            
            seo_analysis = analysis.key_findings.get('seo_analysis', {})
            if 'priority_distribution' in seo_analysis:
                priority_dist = seo_analysis['priority_distribution']
                print(f"    - Average priority: {priority_dist.get('average_priority', 0):.2f}")
            
            success_count += 1
            print(f"  ✅ {sitemap_file.name} - SUCCESS")
            
        except Exception as e:
            print(f"  ❌ {sitemap_file.name} - ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n📊 Sitemap Handler Test Results:")
    print(f"✅ Success: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    return success_count == total_count

if __name__ == "__main__":
    print("🧪 Sitemap Handler Test Suite")
    print("=" * 50)
    
    success = test_handler()
    
    if success:
        print("\n🎉 All tests passed! Sitemap handler is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the handler implementation.")
        sys.exit(1)