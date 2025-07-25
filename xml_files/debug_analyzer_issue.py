#!/usr/bin/env python3
"""
Debug why the analyzer isn't using specialized handlers in the comprehensive test
"""

import sys
import os
import traceback

# Add src to path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_analyzer_issue():
    """Debug the analyzer import and handler loading issue"""
    
    print("🔍 DEBUGGING ANALYZER ISSUE")
    print("=" * 50)
    
    # Test 1: Direct import
    print("1. Testing direct import...")
    try:
        from core.analyzer import XMLDocumentAnalyzer
        analyzer = XMLDocumentAnalyzer()
        print(f"   ✅ Direct import successful: {len(analyzer.handlers)} handlers")
    except Exception as e:
        print(f"   ❌ Direct import failed: {e}")
        traceback.print_exc()
        return
    
    # Test 2: Check handlers registry
    print("\n2. Testing handlers registry...")
    try:
        from handlers import ALL_HANDLERS
        print(f"   ✅ Registry import successful: {len(ALL_HANDLERS)} handlers in registry")
        print(f"   First 5: {[h.__name__ for h in ALL_HANDLERS[:5]]}")
    except Exception as e:
        print(f"   ❌ Registry import failed: {e}")
        traceback.print_exc()
    
    # Test 3: Test with a specific file
    print("\n3. Testing analysis with specific file...")
    test_file = "sample_data/test_files/small/ant/apache-ant-build.xml"
    if os.path.exists(test_file):
        try:
            result = analyzer.analyze_document(test_file)
            
            if hasattr(result, 'document_type'):
                doc_type = result.document_type
                handler_used = getattr(result, 'handler_used', 'unknown')
            else:
                doc_type = result.get('document_type', 'unknown')
                handler_used = result.get('handler_used', 'unknown')
            
            print(f"   📋 Document Type: {doc_type}")
            print(f"   🔧 Handler Used: {handler_used}")
            
            if 'Generic XML' in str(doc_type):
                print(f"   ⚠️ Using generic handler - let's debug why...")
                
                # Debug: Test individual handlers
                import xml.etree.ElementTree as ET
                tree = ET.parse(test_file)
                root = tree.getroot()
                namespaces = dict(root.attrib)
                
                print(f"   🔍 Testing individual handlers:")
                for i, handler in enumerate(analyzer.handlers[:5]):
                    try:
                        can_handle, confidence = handler.can_handle(root, namespaces)
                        print(f"      {handler.__class__.__name__}: {can_handle} ({confidence:.2%})")
                        if can_handle:
                            print(f"         ✅ This handler should be used!")
                    except Exception as he:
                        print(f"      {handler.__class__.__name__}: ERROR - {he}")
                        
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
            traceback.print_exc()
    else:
        print(f"   ⚠️ Test file not found: {test_file}")
    
    # Test 4: Check if there are import cycles or path issues
    print("\n4. Checking for import issues...")
    
    # Test importing individual handlers
    test_handlers = [
        'ant_build_handler.AntBuildHandler',
        'scap_handler.SCAPHandler', 
        'log4j_config_handler.Log4jConfigHandler'
    ]
    
    for handler_path in test_handlers:
        module_name, class_name = handler_path.split('.')
        try:
            module = __import__(f'handlers.{module_name}', fromlist=[class_name])
            handler_class = getattr(module, class_name)
            handler_instance = handler_class()
            print(f"   ✅ {handler_path}: OK")
        except Exception as e:
            print(f"   ❌ {handler_path}: {e}")

if __name__ == "__main__":
    debug_analyzer_issue()