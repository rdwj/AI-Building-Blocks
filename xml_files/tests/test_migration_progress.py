#!/usr/bin/env python3
"""
Test Migration Progress

Test if the individual handler files work correctly.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_individual_handlers():
    """Test if we can import individual handlers"""
    print("🧪 Testing Individual Handler Imports")
    print("-" * 40)
    
    handlers_to_test = [
        ('SCAPHandler', 'handlers.scap_handler'),
        ('RSSHandler', 'handlers.rss_handler'),
        ('MavenPOMHandler', 'handlers.maven_pom_handler'),
        ('SpringConfigHandler', 'handlers.spring_config_handler'),
        ('GenericXMLHandler', 'handlers.generic_xml_handler'),
    ]
    
    success_count = 0
    
    for handler_name, module_path in handlers_to_test:
        try:
            module = __import__(module_path, fromlist=[handler_name])
            handler_class = getattr(module, handler_name)
            
            # Test instantiation
            handler_instance = handler_class()
            print(f"  ✅ {handler_name} - Import and instantiation successful")
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ {handler_name} - Failed: {e}")
    
    print(f"\n📊 Results: {success_count}/{len(handlers_to_test)} handlers working")
    return success_count == len(handlers_to_test)

def test_registry_import():
    """Test if we can import from the registry"""
    print("\n🧪 Testing Handler Registry Import")
    print("-" * 40)
    
    try:
        from handlers import ALL_HANDLERS, HANDLER_CATEGORIES
        print(f"  ✅ Registry imported successfully")
        print(f"  📊 {len(ALL_HANDLERS)} handlers in registry")
        print(f"  📂 {len(HANDLER_CATEGORIES)} categories defined")
        
        # Test instantiation of a few handlers from registry
        test_handlers = ALL_HANDLERS[:3]  # Test first 3
        for handler_class in test_handlers:
            try:
                instance = handler_class()
                print(f"    ✅ {handler_class.__name__} instantiated from registry")
            except Exception as e:
                print(f"    ❌ {handler_class.__name__} failed: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Registry import failed: {e}")
        return False

def test_sample_analysis():
    """Test analysis with a sample file using migrated handlers"""
    print("\n🧪 Testing Sample Analysis with Migrated Handlers")
    print("-" * 40)
    
    try:
        # Import a specific handler directly
        from handlers.rss_handler import RSSHandler
        
        # Test with RSS file
        rss_file = "../sample_data/test_files_synthetic/small/rss/sample-feed.xml"
        if not Path(rss_file).exists():
            print("  ⏭️  RSS sample file not found, skipping")
            return True
        
        # Parse the file
        import xml.etree.ElementTree as ET
        tree = ET.parse(rss_file)
        root = tree.getroot()
        
        # Extract namespaces
        namespaces = {child[0]: child[1] for _, child in ET.iterparse(rss_file, events=['start-ns'])}
        
        # Test handler
        handler = RSSHandler()
        can_handle, confidence = handler.can_handle(root, namespaces)
        
        if can_handle:
            doc_type = handler.detect_type(root, namespaces)
            analysis = handler.analyze(root, rss_file)
            
            print(f"  ✅ RSS Handler Analysis Successful")
            print(f"    📄 Document Type: {doc_type.type_name}")
            print(f"    🎯 Confidence: {confidence}")
            print(f"    📊 Findings: {len(analysis.key_findings) if analysis.key_findings else 0}")
            return True
        else:
            print(f"  ❌ RSS Handler cannot handle the file")
            return False
            
    except Exception as e:
        print(f"  ❌ Sample analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    print("🚀 Testing Handler Migration Progress")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test 1: Individual handler imports
    if not test_individual_handlers():
        all_tests_passed = False
    
    # Test 2: Registry import
    if not test_registry_import():
        all_tests_passed = False
    
    # Test 3: Sample analysis
    if not test_sample_analysis():
        all_tests_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 All migration tests PASSED!")
        print("✅ Handler migration is working correctly")
    else:
        print("❌ Some migration tests FAILED!")
        print("🛑 Need to fix issues before proceeding")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)