#!/usr/bin/env python3
"""
Test handler registration and recognition
"""

import sys
import os
import xml.etree.ElementTree as ET

# Add src to path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.analyzer import XMLDocumentAnalyzer

def test_handler_registration():
    """Test if handlers are properly registered and working"""
    
    print("🧪 TESTING HANDLER REGISTRATION")
    print("=" * 50)
    
    # Create analyzer
    try:
        analyzer = XMLDocumentAnalyzer()
        print(f"✅ XMLDocumentAnalyzer created successfully")
        print(f"📋 Registered handlers: {len(analyzer.handlers)}")
        
        # List all handlers
        print(f"\n📝 Handler List:")
        for i, handler in enumerate(analyzer.handlers, 1):
            handler_name = handler.__class__.__name__
            print(f"   {i:2d}. {handler_name}")
        
    except Exception as e:
        print(f"❌ Failed to create analyzer: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test with specific files that should be recognized
    test_files = [
        ("sample_data/test_files/small/scap/ios-sample-1.1.xccdf.xml", "SCAPHandler"),
        ("incident_1217.xml", "ServiceNowHandler"),
        ("sample_data/test_files/small/ant/apache-ant-build.xml", "AntBuildHandler"),
        ("sample_data/test_files_synthetic/small/log4j/log4j.xml", "Log4jConfigHandler"),
        ("sample_data/test_files_synthetic/small/docbook/article.xml", "DocBookHandler"),
    ]
    
    print(f"\n🔍 TESTING HANDLER RECOGNITION")
    print("-" * 40)
    
    for file_path, expected_handler in test_files:
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            continue
            
        print(f"\n📄 Testing: {os.path.basename(file_path)}")
        
        try:
            # Analyze the file
            result = analyzer.analyze_document(file_path)
            
            if 'error' in result:
                print(f"   ❌ Analysis error: {result['error']}")
                continue
            
            # Check what handler was used
            handler_used = result.get('handler_used', 'unknown')
            doc_type = result.get('document_type', 'unknown')
            confidence = result.get('confidence', 0)
            
            print(f"   📋 Document Type: {doc_type}")
            print(f"   🔧 Handler Used: {handler_used}")
            print(f"   📊 Confidence: {confidence:.2%}")
            
            # Check if expected handler was used
            if expected_handler in handler_used:
                print(f"   ✅ Expected handler used")
            else:
                print(f"   ❌ Expected {expected_handler}, got {handler_used}")
                
                # Debug: check which handlers could handle this
                tree = ET.parse(file_path)
                root = tree.getroot()
                namespaces = dict(root.attrib)
                
                print(f"   🔍 Debug - handlers that can handle this:")
                for handler in analyzer.handlers[:10]:  # Check first 10
                    try:
                        can_handle, conf = handler.can_handle(root, namespaces)
                        if can_handle or conf > 0.1:
                            print(f"      {handler.__class__.__name__}: {can_handle} ({conf:.2%})")
                    except Exception as e:
                        print(f"      {handler.__class__.__name__}: ERROR - {e}")
            
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_handler_registration()