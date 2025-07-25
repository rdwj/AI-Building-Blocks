#!/usr/bin/env python3
"""
Test KML handler implementation
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def test_kml_handler_import():
    """Test importing the KML handler"""
    try:
        from handlers.kml_handler import KMLHandler
        print("✅ KMLHandler imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import KMLHandler: {e}")
        return False

def test_kml_handler_instantiation():
    """Test creating KML handler instance"""
    try:
        from handlers.kml_handler import KMLHandler
        handler = KMLHandler()
        print("✅ KMLHandler instantiated successfully")
        return handler
    except Exception as e:
        print(f"❌ Failed to instantiate KMLHandler: {e}")
        return None

def test_kml_files():
    """Test KML handler with sample files"""
    from handlers.kml_handler import KMLHandler
    import xml.etree.ElementTree as ET
    
    handler = KMLHandler()
    test_files = [
        "../../sample_data/test_files_synthetic/small/kml/simple_placemark.kml",
        "../../sample_data/test_files_synthetic/small/kml/route_linestring.kml", 
        "../../sample_data/test_files_synthetic/small/kml/area_polygon.kml",
        "../../sample_data/test_files_synthetic/small/kml/complex_document.kml"
    ]
    
    results = []
    
    for test_file in test_files:
        if not Path(test_file).exists():
            print(f"❌ Test file not found: {test_file}")
            continue
            
        print(f"\n🔍 Testing {test_file}")
        
        try:
            # Parse XML
            tree = ET.parse(test_file)
            root = tree.getroot()
            
            # Extract namespaces
            namespaces = {}
            for event, elem in ET.iterparse(test_file, events=['start-ns']):
                if event == 'start-ns':
                    prefix, uri = elem
                    namespaces[prefix or 'default'] = uri
            
            # Test can_handle
            can_handle, confidence = handler.can_handle(root, namespaces)
            print(f"  - can_handle: {can_handle} (confidence: {confidence:.2f})")
            
            if can_handle:
                # Test detect_type
                doc_type = handler.detect_type(root, namespaces)
                print(f"  - Document type: {doc_type.type_name}")
                print(f"  - Version: {doc_type.version}")
                print(f"  - Confidence: {doc_type.confidence:.2f}")
                
                # Test analyze
                analysis = handler.analyze(root, test_file)
                print(f"  - Analysis type: {analysis.document_type}")
                print(f"  - Key findings keys: {list(analysis.key_findings.keys())}")
                print(f"  - Data inventory: {analysis.data_inventory}")
                print(f"  - AI use cases: {len(analysis.ai_use_cases)}")
                print(f"  - Quality metrics: {analysis.quality_metrics}")
                
                # Test extract_key_data
                key_data = handler.extract_key_data(root)
                print(f"  - Key data keys: {list(key_data.keys())}")
                
                results.append({
                    'file': test_file,
                    'success': True,
                    'confidence': confidence,
                    'features': analysis.data_inventory.get('total_features', 0)
                })
                print("  ✅ Test passed")
            else:
                results.append({
                    'file': test_file,
                    'success': False,
                    'reason': 'Handler rejected file'
                })
                print("  ❌ Handler cannot handle this file")
                
        except Exception as e:
            print(f"  ❌ Test failed: {e}")
            results.append({
                'file': test_file,
                'success': False,
                'reason': str(e)
            })
            import traceback
            traceback.print_exc()
    
    return results

def main():
    print("🧪 KML Handler Test Suite")
    print("=" * 50)
    
    # Test import
    if not test_kml_handler_import():
        return False
    
    # Test instantiation
    handler = test_kml_handler_instantiation()
    if not handler:
        return False
    
    # Test with files
    results = test_kml_files()
    
    # Summary
    print(f"\n📊 Test Results Summary")
    print("=" * 30)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    
    if successful:
        avg_confidence = sum(r['confidence'] for r in successful) / len(successful)
        print(f"📈 Average confidence: {avg_confidence:.2f}")
        
        total_features = sum(r.get('features', 0) for r in successful)
        print(f"🗺️ Total features detected: {total_features}")
    
    if failed:
        print("\n❌ Failed tests:")
        for result in failed:
            print(f"  - {Path(result['file']).name}: {result['reason']}")
    
    success_rate = len(successful) / len(results) * 100 if results else 0
    print(f"\n🎯 Success rate: {success_rate:.1f}%")
    
    return success_rate == 100.0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)