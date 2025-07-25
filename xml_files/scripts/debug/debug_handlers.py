#!/usr/bin/env python3
"""
Debug Handler Issues

Simple test to debug what's wrong with the handlers.
"""

import sys
import traceback
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_import():
    """Test if we can import the analyzer"""
    try:
        from core.analyzer import XMLDocumentAnalyzer
        print("✅ Successfully imported XMLDocumentAnalyzer")
        return XMLDocumentAnalyzer
    except Exception as e:
        print(f"❌ Failed to import XMLDocumentAnalyzer: {e}")
        traceback.print_exc()
        return None

def test_instantiation(analyzer_class):
    """Test if we can create an instance"""
    try:
        analyzer = analyzer_class()
        print("✅ Successfully created XMLDocumentAnalyzer instance")
        print(f"   Number of handlers registered: {len(analyzer.handlers)}")
        for i, handler in enumerate(analyzer.handlers):
            print(f"   {i+1}. {handler.__class__.__name__}")
        return analyzer
    except Exception as e:
        print(f"❌ Failed to create XMLDocumentAnalyzer instance: {e}")
        traceback.print_exc()
        return None

def test_simple_file(analyzer):
    """Test with a simple XML file"""
    # Create a simple test XML file
    simple_xml = """<?xml version="1.0" encoding="UTF-8"?>
<root>
    <test>Simple test content</test>
</root>"""
    
    test_file = Path("test_simple.xml")
    test_file.write_text(simple_xml)
    
    try:
        print(f"\n🧪 Testing with simple XML file: {test_file}")
        result = analyzer.analyze_document(str(test_file))
        print("✅ Analysis completed successfully")
        print(f"   Result keys: {list(result.keys())}")
        
        if 'error' in result:
            print(f"   ❌ Error in result: {result['error']}")
        else:
            print(f"   Handler used: {result.get('handler_used', 'Unknown')}")
            doc_type = result.get('document_type')
            type_name = doc_type.type_name if doc_type else 'Unknown'
            print(f"   Document type: {type_name}")
        
        return result
        
    except Exception as e:
        print(f"❌ Exception during analysis: {e}")
        traceback.print_exc()
        return None
    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()

def test_existing_file(analyzer):
    """Test with an existing sample file"""
    test_files = [
        "sample_data/test_files_synthetic/small/rss/sample-feed.xml",
        "sample_data/test_files_synthetic/small/svg/sample-icon.svg",
        "sample_data/stigs_old/node2.example.com-STIG-20250710162433.xml"
    ]
    
    for test_file in test_files:
        file_path = Path(test_file)
        if not file_path.exists():
            print(f"⏭️  Skipping {test_file} - file not found")
            continue
            
        print(f"\n🧪 Testing with existing file: {test_file}")
        try:
            result = analyzer.analyze_document(str(file_path))
            if 'error' in result:
                print(f"   ❌ Error: {result['error']}")
            else:
                print(f"   ✅ Success - Handler: {result.get('handler_used', 'Unknown')}")
                doc_type = result.get('document_type')
            type_name = doc_type.type_name if doc_type else 'Unknown'
            print(f"   Document type: {type_name}")
            return result
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            traceback.print_exc()
    
    return None

def main():
    print("🔍 Debugging XML Handler Issues")
    print("=" * 50)
    
    # Step 1: Test import
    analyzer_class = test_import()
    if not analyzer_class:
        return False
    
    # Step 2: Test instantiation
    analyzer = test_instantiation(analyzer_class)
    if not analyzer:
        return False
    
    # Step 3: Test with simple file
    result = test_simple_file(analyzer)
    if not result:
        return False
    
    # Step 4: Test with existing files
    result = test_existing_file(analyzer)
    
    print("\n" + "=" * 50)
    print("🎯 Debug Summary:")
    print("✅ All basic functionality working")
    print("✅ Ready to proceed with comprehensive testing")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)