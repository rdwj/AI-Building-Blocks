#!/usr/bin/env python3
"""
Test GPX handler integration with main analyzer
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def test_gpx_integration():
    """Test GPX handler integration with main analyzer"""
    
    try:
        from core.analyzer import XMLDocumentAnalyzer
        print("✅ XMLDocumentAnalyzer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import XMLDocumentAnalyzer: {e}")
        return False
    
    # Test registry import
    try:
        from handlers import ALL_HANDLERS, GPXHandler
        print(f"✅ Handler registry imported successfully ({len(ALL_HANDLERS)} handlers)")
        
        # Check if GPXHandler is in the registry
        gpx_handler_in_registry = any(h.__name__ == 'GPXHandler' for h in ALL_HANDLERS)
        print(f"✅ GPXHandler in registry: {gpx_handler_in_registry}")
        
    except ImportError as e:
        print(f"❌ Failed to import handler registry: {e}")
        return False
    
    # Test with sample GPX files
    analyzer = XMLDocumentAnalyzer()
    test_files = [
        "../../sample_data/test_files_synthetic/small/gpx/simple_waypoints.gpx",
        "../../sample_data/test_files_synthetic/small/gpx/hiking_track.gpx"
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
            print(f"  - Content type: {result['document_type'].metadata.get('content_type')}")
            print(f"  - Confidence: {result['confidence']:.1f}")
            print(f"  - Analysis type: {result['analysis'].document_type}")
            
            # Verify it's using the GPX handler
            if result['handler_used'] != 'GPXHandler':
                print(f"❌ Wrong handler used! Expected GPXHandler, got {result['handler_used']}")
                return False
            
            # Check analysis details
            findings = result['analysis'].key_findings
            inventory = result['analysis'].data_inventory
            
            print(f"  - Waypoints: {inventory['waypoints']}")
            print(f"  - Routes: {inventory['routes']}")
            print(f"  - Tracks: {inventory['tracks']}")
            print(f"  - Track points: {inventory['track_points']}")
            
            if inventory['time_span_hours'] > 0:
                print(f"  - Duration: {inventory['time_span_hours']:.2f} hours")
            
            stats = findings['statistics']
            if stats['total_distance_km'] > 0:
                print(f"  - Distance: {stats['total_distance_km']:.2f} km")
            if stats['elevation_gain_m'] > 0:
                print(f"  - Elevation gain: {stats['elevation_gain_m']:.0f} m")
            
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
    print("🧪 GPX Handler Integration Test")
    print("=" * 50)
    
    success = test_gpx_integration()
    
    if success:
        print("\n🎉 GPX handler integration test passed!")
        sys.exit(0)
    else:
        print("\n❌ GPX handler integration test failed!")
        sys.exit(1)