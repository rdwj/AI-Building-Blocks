#!/usr/bin/env python3
"""
Test KML handler integration with main analyzer
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def test_kml_integration():
    """Test KML handler integration with main analyzer"""
    
    try:
        from core.analyzer import XMLDocumentAnalyzer
        print("✅ XMLDocumentAnalyzer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import XMLDocumentAnalyzer: {e}")
        return False
    
    # Test registry import
    try:
        from handlers import ALL_HANDLERS, KMLHandler
        print(f"✅ Handler registry imported successfully ({len(ALL_HANDLERS)} handlers)")
        
        # Check if KMLHandler is in the registry
        kml_handler_in_registry = any(h.__name__ == 'KMLHandler' for h in ALL_HANDLERS)
        print(f"✅ KMLHandler in registry: {kml_handler_in_registry}")
        
    except ImportError as e:
        print(f"❌ Failed to import handler registry: {e}")
        return False
    
    # Test with sample KML file
    analyzer = XMLDocumentAnalyzer()
    test_file = "../../sample_data/test_files_synthetic/small/kml/simple_placemark.kml"
    
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
        
        # Verify it's using the KML handler
        if result['handler_used'] != 'KMLHandler':
            print(f"❌ Wrong handler used! Expected KMLHandler, got {result['handler_used']}")
            return False
        
        # Check analysis details
        findings = result['analysis'].key_findings
        structure = findings['structure']
        print(f"  - Total features: {structure['total_features']}")
        print(f"  - Placemarks: {len(findings['placemarks'])}")
        print(f"  - Geometries: {findings['geometries']['total']}")
        
        if findings['placemarks']:
            placemark = findings['placemarks'][0]
            print(f"  - First placemark: {placemark.get('name', 'Unnamed')}")
            print(f"  - Geometry type: {placemark.get('geometry_type', 'None')}")
        
        print("✅ KML handler integration successful!")
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 KML Handler Integration Test")
    print("=" * 50)
    
    success = test_kml_integration()
    
    if success:
        print("\n🎉 KML handler integration test passed!")
        sys.exit(0)
    else:
        print("\n❌ KML handler integration test failed!")
        sys.exit(1)