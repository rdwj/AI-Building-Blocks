#!/usr/bin/env python3
"""
Comprehensive test of GPX handler with detailed analysis
"""

import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from core.analyzer import XMLDocumentAnalyzer

def main():
    analyzer = XMLDocumentAnalyzer()
    test_file = "../../sample_data/test_files_synthetic/small/gpx/hiking_track.gpx"
    
    print(f"🏃 Analyzing GPX file: {test_file}")
    print("=" * 60)
    
    try:
        result = analyzer.analyze_document(test_file)
        
        print(f"Handler Used: {result['handler_used']}")
        print(f"Document Type: {result['document_type'].type_name}")
        print(f"Version: {result['document_type'].version}")
        print(f"Content Type: {result['document_type'].metadata.get('content_type')}")
        print(f"Confidence: {result['confidence']:.2f}")
        
        analysis = result['analysis']
        print(f"\nDocument Analysis: {analysis.document_type}")
        print(f"Data Inventory: {analysis.data_inventory}")
        
        findings = analysis.key_findings
        
        # Metadata
        metadata = findings['metadata']
        print(f"\n📋 Metadata:")
        print(f"  - Name: {metadata.get('name')}")
        print(f"  - Description: {metadata.get('description')}")
        print(f"  - Creator: {metadata.get('creator')}")
        print(f"  - Version: {metadata.get('version')}")
        
        # Statistics
        stats = findings['statistics']
        print(f"\n📊 Statistics:")
        print(f"  - Total Points: {stats['total_points']}")
        print(f"  - Distance: {stats['total_distance_km']:.2f} km")
        print(f"  - Duration: {stats['total_duration_hours']:.2f} hours")
        print(f"  - Avg Speed: {stats['avg_speed_kmh']:.2f} km/h")
        print(f"  - Max Speed: {stats['max_speed_kmh']:.2f} km/h") 
        print(f"  - Elevation Gain: {stats['elevation_gain_m']:.0f} m")
        print(f"  - Elevation Loss: {stats['elevation_loss_m']:.0f} m")
        print(f"  - Max Elevation: {stats['max_elevation_m']:.0f} m")
        print(f"  - Min Elevation: {stats['min_elevation_m']:.0f} m")
        
        # Tracks
        tracks = findings['tracks']
        print(f"\n🛤️ Tracks ({tracks['count']}):")
        for i, track in enumerate(tracks['tracks'][:2], 1):
            print(f"  Track {i}: {track.get('name', 'Unnamed')}")
            print(f"    - Points: {track['total_points']}")
            print(f"    - Distance: {track['total_distance_km']:.2f} km")
            print(f"    - Duration: {track['total_duration_minutes']:.1f} minutes")
            print(f"    - Segments: {len(track['segments'])}")
        
        # Elevation Profile
        elevation = findings['elevation_profile']
        if elevation['has_elevation']:
            print(f"\n⛰️ Elevation Profile:")
            elev_stats = elevation['statistics']
            print(f"  - Range: {elev_stats['min']:.0f}m - {elev_stats['max']:.0f}m")
            print(f"  - Total Range: {elev_stats['range']:.0f}m")
            print(f"  - Mean Elevation: {elev_stats['mean']:.0f}m")
            print(f"  - Elevation Gain: {elev_stats['gain']:.0f}m")
            print(f"  - Elevation Loss: {elev_stats['loss']:.0f}m")
            
            if 'gradient_analysis' in elevation:
                grad = elevation['gradient_analysis']
                print(f"  - Max Gradient: {grad['max_gradient']:.1f}%")
                print(f"  - Min Gradient: {grad['min_gradient']:.1f}%")
                print(f"  - Avg Gradient: {grad['avg_gradient']:.1f}%")
                print(f"  - Steep Sections: {grad['steep_sections']}")
        
        # Temporal Analysis
        temporal = findings['temporal_analysis']
        if temporal['has_timestamps']:
            print(f"\n⏰ Temporal Analysis:")
            print(f"  - Start: {temporal['start_time']}")
            print(f"  - End: {temporal['end_time']}")  
            print(f"  - Duration: {temporal['duration_hours']:.2f} hours")
            print(f"  - Time Gaps: {len(temporal['time_gaps'])}")
        
        # Geographic Bounds
        bounds = findings['geographic_bounds']
        print(f"\n🗺️ Geographic Bounds:")
        print(f"  - North: {bounds['north']:.4f}°")
        print(f"  - South: {bounds['south']:.4f}°")
        print(f"  - East: {bounds['east']:.4f}°")
        print(f"  - West: {bounds['west']:.4f}°")
        
        # Quality metrics
        quality = analysis.quality_metrics
        print(f"\n📈 Quality Metrics:")
        for metric, value in quality.items():
            print(f"  - {metric.replace('_', ' ').title()}: {value:.2f}")
        
        # AI use cases (first 5)
        print(f"\n🤖 AI Use Cases ({len(analysis.ai_use_cases)}):")
        for i, use_case in enumerate(analysis.ai_use_cases[:5], 1):
            print(f"  {i}. {use_case}")
        
        print(f"\n✅ Comprehensive analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()