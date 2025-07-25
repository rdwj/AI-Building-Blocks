#!/usr/bin/env python3
"""
Manual test of KML handler with complex document
"""

import sys
import os
import json

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from core.analyzer import XMLDocumentAnalyzer

def main():
    analyzer = XMLDocumentAnalyzer()
    test_file = "../../sample_data/test_files_synthetic/small/kml/complex_document.kml"
    
    print(f"🗺️ Analyzing KML file: {test_file}")
    print("=" * 60)
    
    try:
        result = analyzer.analyze_document(test_file)
        
        print(f"Handler Used: {result['handler_used']}")
        print(f"Document Type: {result['document_type'].type_name}")
        print(f"Version: {result['document_type'].version}")
        print(f"Confidence: {result['confidence']:.2f}")
        
        analysis = result['analysis']
        print(f"\nDocument Analysis: {analysis.document_type}")
        print(f"Data Inventory: {analysis.data_inventory}")
        
        findings = analysis.key_findings
        
        # Structure
        structure = findings['structure']
        print(f"\n📊 Structure:")
        print(f"  - Total Features: {structure['total_features']}")
        print(f"  - Documents: {structure['documents']}")
        print(f"  - Folders: {structure['folders']}")
        print(f"  - Max Depth: {structure['max_depth']}")
        print(f"  - Has Schema: {structure['has_schema']}")
        print(f"  - Has Extended Data: {structure['has_extended_data']}")
        
        # Placemarks
        placemarks = findings['placemarks']
        print(f"\n📍 Placemarks ({len(placemarks)}):")
        for pm in placemarks[:3]:
            print(f"  - {pm.get('name', 'Unnamed')}: {pm.get('geometry_type', 'No geometry')}")
            if pm.get('description'):
                desc = pm['description'][:100] + "..." if len(pm['description']) > 100 else pm['description']
                print(f"    Description: {desc}")
        
        # Geometries
        geometries = findings['geometries']
        print(f"\n🗺️ Geometries:")
        print(f"  - Total: {geometries['total']}")
        print(f"  - Points: {geometries['points']}")
        print(f"  - Lines: {geometries['lines']}")
        print(f"  - Polygons: {geometries['polygons']}")
        print(f"  - Coordinates: {geometries['coordinate_count']}")
        
        # Quality metrics
        quality = analysis.quality_metrics
        print(f"\n📈 Quality Metrics:")
        for metric, value in quality.items():
            print(f"  - {metric.title()}: {value:.2f}")
        
        # AI use cases
        print(f"\n🤖 AI Use Cases ({len(analysis.ai_use_cases)}):")
        for i, use_case in enumerate(analysis.ai_use_cases[:5], 1):
            print(f"  {i}. {use_case}")
        
        print(f"\n✅ Analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()