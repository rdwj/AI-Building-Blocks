#!/usr/bin/env python3
"""
Test Sitemap handler integration with main analyzer
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def test_sitemap_integration():
    """Test Sitemap handler integration with main analyzer"""
    
    try:
        from core.analyzer import XMLDocumentAnalyzer
        print("✅ XMLDocumentAnalyzer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import XMLDocumentAnalyzer: {e}")
        return False
    
    # Test registry import
    try:
        from handlers import ALL_HANDLERS, SitemapHandler
        print(f"✅ Handler registry imported successfully ({len(ALL_HANDLERS)} handlers)")
        
        # Check if SitemapHandler is in the registry
        sitemap_handler_in_registry = any(h.__name__ == 'SitemapHandler' for h in ALL_HANDLERS)
        print(f"✅ SitemapHandler in registry: {sitemap_handler_in_registry}")
        
    except ImportError as e:
        print(f"❌ Failed to import handler registry: {e}")
        return False
    
    # Test with sample Sitemap file
    analyzer = XMLDocumentAnalyzer()
    test_file = "../../sample_data/test_files_synthetic/small/sitemap/urlset.xml"
    
    if not Path(test_file).exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    print(f"\n🔍 Testing integration with {test_file}")
    
    try:
        result = analyzer.analyze_document(test_file)
        
        print(f"✅ Analysis completed successfully")
        print(f"  - Handler used: {result['handler_used']}")
        print(f"  - Document type: {result['document_type'].type_name}")
        print(f"  - Confidence: {result['confidence']:.1f}")
        print(f"  - Analysis type: {result['analysis'].document_type}")
        
        # Verify it's using the Sitemap handler
        if result['handler_used'] != 'SitemapHandler':
            print(f"❌ Wrong handler used! Expected SitemapHandler, got {result['handler_used']}")
            return False
        
        # Check analysis details
        findings = result['analysis'].key_findings
        content_analysis = findings['content_analysis']
        print(f"  - URLs found: {content_analysis.get('url_count', 0)}")
        print(f"  - Priority values: {len(content_analysis.get('priorities', {}))}")
        print(f"  - Change frequencies: {len(content_analysis.get('change_frequencies', {}))}")
        
        seo_analysis = findings['seo_analysis']
        if 'priority_distribution' in seo_analysis:
            print(f"  - Average priority: {seo_analysis['priority_distribution'].get('average_priority', 0):.2f}")
        
        print("✅ Sitemap handler integration successful!")
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Sitemap Handler Integration Test")
    print("=" * 50)
    
    success = test_sitemap_integration()
    
    if success:
        print("\n🎉 Sitemap handler integration test passed!")
        sys.exit(0)
    else:
        print("\n❌ Sitemap handler integration test failed!")
        sys.exit(1)