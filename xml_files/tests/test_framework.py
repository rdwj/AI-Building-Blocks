#!/usr/bin/env python3
"""
Test script to verify the XML analysis framework is working correctly
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from xml_schema_analyzer_fixed import XMLSchemaAnalyzer
        print("✅ xml_schema_analyzer_fixed imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import xml_schema_analyzer_fixed: {e}")
        return False
    
    try:
        from core.analyzer import XMLDocumentAnalyzer
        print("✅ xml_specialized_handlers imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import xml_specialized_handlers: {e}")
        return False
    
    try:
        from xml_chunking_strategy import ChunkingOrchestrator
        print("✅ xml_chunking_strategy imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import xml_chunking_strategy: {e}")
        return False
    
    try:
        from additional_xml_handlers import MavenPOMHandler, Log4jConfigHandler
        print("✅ additional_xml_handlers imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import additional_xml_handlers: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality"""
    print("\nTesting basic functionality...")
    
    # Create a test XML
    test_xml = """<?xml version="1.0" encoding="UTF-8"?>
<test>
    <element attr="value">Content</element>
</test>"""
    
    test_path = Path("test_temp.xml")
    test_path.write_text(test_xml)
    
    try:
        from core.analyzer import XMLDocumentAnalyzer
        
        analyzer = XMLDocumentAnalyzer()
        result = analyzer.analyze_document(str(test_path))
        
        if "error" not in result:
            print("✅ Basic analysis completed successfully")
            print(f"   Document type: {result['document_type'].type_name}")
            print(f"   Handler: {result['handler_used']}")
            return True
        else:
            print(f"❌ Analysis failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    finally:
        # Clean up
        if test_path.exists():
            test_path.unlink()

def test_handler_detection():
    """Test that handlers detect correct document types"""
    print("\nTesting handler detection...")
    
    test_cases = [
        {
            "name": "Maven POM",
            "xml": """<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <groupId>test</groupId>
    <artifactId>test</artifactId>
</project>""",
            "expected": "Maven POM"
        },
        {
            "name": "RSS Feed",
            "xml": """<?xml version="1.0"?>
<rss version="2.0">
    <channel><title>Test</title></channel>
</rss>""",
            "expected": "RSS Feed"
        }
    ]
    
    from core.analyzer import XMLDocumentAnalyzer
    analyzer = XMLDocumentAnalyzer()
    
    all_passed = True
    
    for test_case in test_cases:
        test_path = Path("test_handler.xml")
        test_path.write_text(test_case["xml"])
        
        try:
            result = analyzer.analyze_document(str(test_path))
            detected = result['document_type'].type_name
            
            if test_case["expected"] in detected:
                print(f"✅ {test_case['name']}: Correctly detected as {detected}")
            else:
                print(f"❌ {test_case['name']}: Expected {test_case['expected']}, got {detected}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ {test_case['name']}: Error - {e}")
            all_passed = False
        finally:
            if test_path.exists():
                test_path.unlink()
    
    return all_passed

def main():
    """Run all tests"""
    print("🧪 XML Analysis Framework Test Suite")
    print("="*40)
    
    tests_passed = 0
    tests_total = 3
    
    # Test 1: Imports
    if test_imports():
        tests_passed += 1
    
    # Test 2: Basic functionality
    if test_basic_functionality():
        tests_passed += 1
    
    # Test 3: Handler detection
    if test_handler_detection():
        tests_passed += 1
    
    print("\n" + "="*40)
    print(f"Tests passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("✅ All tests passed! The framework is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
