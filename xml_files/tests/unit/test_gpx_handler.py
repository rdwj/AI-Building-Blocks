#!/usr/bin/env python3
"""
Test GPX handler implementation
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def test_gpx_handler_import():
    """Test importing the GPX handler"""
    try:
        from handlers.gpx_handler import GPXHandler
        print("✅ GPXHandler imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import GPXHandler: {e}")
        return False

def test_gpx_handler_instantiation():
    """Test creating GPX handler instance"""
    try:
        from handlers.gpx_handler import GPXHandler
        handler = GPXHandler()
        print("✅ GPXHandler instantiated successfully")
        return handler
    except Exception as e:
        print(f"❌ Failed to instantiate GPXHandler: {e}")
        return None

def test_gpx_files():
    """Test GPX handler with sample files"""
    from handlers.gpx_handler import GPXHandler
    import xml.etree.ElementTree as ET
    
    handler = GPXHandler()
    test_files = [
        "../../sample_data/test_files_synthetic/small/gpx/simple_waypoints.gpx",
        "../../sample_data/test_files_synthetic/small/gpx/hiking_track.gpx", 
        "../../sample_data/test_files_synthetic/small/gpx/cycling_route.gpx",
        "../../sample_data/test_files_synthetic/small/gpx/running_activity.gpx"
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
                print(f"  - Content type: {doc_type.metadata.get('content_type', 'unknown')}")
                print(f"  - Confidence: {doc_type.confidence:.2f}")
                
                # Test analyze
                analysis = handler.analyze(root, test_file)
                print(f"  - Analysis type: {analysis.document_type}")
                print(f"  - Key findings keys: {list(analysis.key_findings.keys())}")
                print(f"  - Data inventory: {analysis.data_inventory}")
                print(f"  - AI use cases: {len(analysis.ai_use_cases)}")
                
                # Show specific findings
                findings = analysis.key_findings
                if findings['waypoints']['count'] > 0:
                    print(f"  - Waypoints: {findings['waypoints']['count']}")
                if findings['tracks']['count'] > 0:
                    print(f"  - Tracks: {findings['tracks']['count']}")
                    total_points = sum(track['total_points'] for track in findings['tracks']['tracks'])
                    print(f"  - Total track points: {total_points}")
                if findings['routes']['count'] > 0:
                    print(f"  - Routes: {findings['routes']['count']}")
                
                stats = findings['statistics']
                if stats['total_distance_km'] > 0:
                    print(f"  - Total distance: {stats['total_distance_km']:.2f} km")
                if stats['total_duration_hours'] > 0:
                    print(f"  - Duration: {stats['total_duration_hours']:.2f} hours")
                if stats['elevation_gain_m'] > 0:
                    print(f"  - Elevation gain: {stats['elevation_gain_m']:.0f} m")
                
                print(f"  - Quality metrics: {analysis.quality_metrics}")
                
                # Test extract_key_data
                key_data = handler.extract_key_data(root)
                print(f"  - Key data keys: {list(key_data.keys())}")
                
                results.append({
                    'file': test_file,
                    'success': True,
                    'confidence': confidence,
                    'waypoints': findings['waypoints']['count'],
                    'tracks': findings['tracks']['count'],
                    'routes': findings['routes']['count'],
                    'distance_km': stats['total_distance_km'],
                    'content_type': doc_type.metadata.get('content_type')
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
    print("🧪 GPX Handler Test Suite")
    print("=" * 50)
    
    # Test import
    if not test_gpx_handler_import():
        return False
    
    # Test instantiation
    handler = test_gpx_handler_instantiation()
    if not handler:
        return False
    
    # Test with files
    results = test_gpx_files()
    
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
        
        total_waypoints = sum(r.get('waypoints', 0) for r in successful)
        total_tracks = sum(r.get('tracks', 0) for r in successful)
        total_routes = sum(r.get('routes', 0) for r in successful)
        total_distance = sum(r.get('distance_km', 0) for r in successful)
        
        print(f"📍 Total waypoints detected: {total_waypoints}")
        print(f"🛤️ Total tracks detected: {total_tracks}")
        print(f"🗺️ Total routes detected: {total_routes}")
        print(f"📏 Total distance: {total_distance:.2f} km")
        
        print(f"\n📋 Content Types Detected:")
        content_types = {}
        for result in successful:
            ct = result.get('content_type', 'unknown')
            content_types[ct] = content_types.get(ct, 0) + 1
        for ct, count in content_types.items():
            print(f"  - {ct}: {count}")
    
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