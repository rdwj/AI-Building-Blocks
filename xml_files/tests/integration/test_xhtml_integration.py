#!/usr/bin/env python3
"""
Test XHTML handler integration with main analyzer
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def test_xhtml_integration():
    """Test XHTML handler integration with main analyzer"""
    
    try:
        from core.analyzer import XMLDocumentAnalyzer
        print("✅ XMLDocumentAnalyzer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import XMLDocumentAnalyzer: {e}")
        return False
    
    # Test registry import
    try:
        from handlers import ALL_HANDLERS, XHTMLHandler
        print(f"✅ Handler registry imported successfully ({len(ALL_HANDLERS)} handlers)")
        
        # Check if XHTMLHandler is in the registry
        xhtml_handler_in_registry = any(h.__name__ == 'XHTMLHandler' for h in ALL_HANDLERS)
        print(f"✅ XHTMLHandler in registry: {xhtml_handler_in_registry}")
        
    except ImportError as e:
        print(f"❌ Failed to import handler registry: {e}")
        return False
    
    # Test with sample XHTML files
    analyzer = XMLDocumentAnalyzer()
    test_files = [
        "../../sample_data/test_files_synthetic/small/xhtml/simple_page.xhtml",
        "../../sample_data/test_files_synthetic/small/xhtml/semantic_article.xhtml"
    ]
    
    for test_file in test_files:
        if not Path(test_file).exists():
            print(f"❌ Test file not found: {test_file}")
            continue
        
        print(f"\n🔍 Testing integration with {test_file}")
        
        try:
            result = analyzer.analyze_document(test_file)
            
            print(f"✅ Analysis completed successfully")
            print(f"  - Handler used: {result['handler_used']}")
            print(f"  - Document type: {result['document_type'].type_name}")
            print(f"  - Version: {result['document_type'].version}")
            print(f"  - Document subtype: {result['document_type'].metadata.get('document_type')}")
            print(f"  - Confidence: {result['confidence']:.1f}")
            print(f"  - Analysis type: {result['analysis'].document_type}")
            
            # Verify it's using the XHTML handler
            if result['handler_used'] != 'XHTMLHandler':
                print(f"❌ Wrong handler used! Expected XHTMLHandler, got {result['handler_used']}")
                return False
            
            # Check analysis details
            findings = result['analysis'].key_findings
            inventory = result['analysis'].data_inventory
            
            print(f"  - Total elements: {inventory['total_elements']}")
            print(f"  - Semantic elements: {inventory['semantic_elements']}")
            print(f"  - Links: {inventory['links']}")
            print(f"  - Forms: {inventory['forms']}")
            print(f"  - Images: {inventory['images']}")
            
            # Content analysis
            content = findings['content_analysis']
            print(f"  - Language: {content.get('language', 'unknown')}")
            print(f"  - Headings: {sum(content['headings'].values()) if content['headings'] else 0}")
            print(f"  - Paragraphs: {content['paragraphs']}")
            
            # Metadata
            metadata = findings['metadata']
            if metadata['title']:
                print(f"  - Title: {metadata['title'][:50]}...")
            
            # Quality
            quality = result['analysis'].quality_metrics
            print(f"  - Overall quality: {quality['overall']:.2f}")
            
            print("  ✅ Integration test passed")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == "__main__":
    print("🧪 XHTML Handler Integration Test")
    print("=" * 50)
    
    success = test_xhtml_integration()
    
    if success:
        print("\n🎉 XHTML handler integration test passed!")
        sys.exit(0)
    else:
        print("\n❌ XHTML handler integration test failed!")
        sys.exit(1)