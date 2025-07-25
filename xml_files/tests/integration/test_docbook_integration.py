#!/usr/bin/env python3
"""
Test DocBook handler integration with main analyzer
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def test_docbook_integration():
    """Test DocBook handler integration with main analyzer"""
    
    try:
        from core.analyzer import XMLDocumentAnalyzer
        print("✅ XMLDocumentAnalyzer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import XMLDocumentAnalyzer: {e}")
        return False
    
    # Test registry import
    try:
        from handlers import ALL_HANDLERS, DocBookHandler
        print(f"✅ Handler registry imported successfully ({len(ALL_HANDLERS)} handlers)")
        
        # Check if DocBookHandler is in the registry
        docbook_handler_in_registry = any(h.__name__ == 'DocBookHandler' for h in ALL_HANDLERS)
        print(f"✅ DocBookHandler in registry: {docbook_handler_in_registry}")
        
    except ImportError as e:
        print(f"❌ Failed to import handler registry: {e}")
        return False
    
    # Test with sample DocBook file
    analyzer = XMLDocumentAnalyzer()
    test_file = "../../sample_data/test_files_synthetic/small/docbook/book.xml"
    
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
        
        # Verify it's using the DocBook handler
        if result['handler_used'] != 'DocBookHandler':
            print(f"❌ Wrong handler used! Expected DocBookHandler, got {result['handler_used']}")
            return False
        
        # Check analysis details
        findings = result['analysis'].key_findings
        print(f"  - Chapters found: {len(findings['structure']['chapters'])}")
        print(f"  - Sections found: {findings['structure']['total_sections']}")
        print(f"  - Paragraphs found: {findings['content_stats']['paragraphs']}")
        
        print("✅ DocBook handler integration successful!")
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 DocBook Handler Integration Test")
    print("=" * 50)
    
    success = test_docbook_integration()
    
    if success:
        print("\n🎉 DocBook handler integration test passed!")
        sys.exit(0)
    else:
        print("\n❌ DocBook handler integration test failed!")
        sys.exit(1)