#!/usr/bin/env python3
"""
Test GraphML handler integration with main analyzer
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def test_graphml_integration():
    """Test GraphML handler integration with main analyzer"""
    
    try:
        from core.analyzer import XMLDocumentAnalyzer
        print("✅ XMLDocumentAnalyzer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import XMLDocumentAnalyzer: {e}")
        return False
    
    # Test registry import
    try:
        from handlers import ALL_HANDLERS, GraphMLHandler
        print(f"✅ Handler registry imported successfully ({len(ALL_HANDLERS)} handlers)")
        
        # Check if GraphMLHandler is in the registry
        graphml_handler_in_registry = any(h.__name__ == 'GraphMLHandler' for h in ALL_HANDLERS)
        print(f"✅ GraphMLHandler in registry: {graphml_handler_in_registry}")
        
    except ImportError as e:
        print(f"❌ Failed to import handler registry: {e}")
        return False
    
    # Test with sample GraphML files
    analyzer = XMLDocumentAnalyzer()
    test_files = [
        "../../sample_data/test_files_synthetic/small/graphml/simple_network.graphml",
        "../../sample_data/test_files_synthetic/small/graphml/neural_network.graphml"
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
            print(f"  - Graph Type: {result['document_type'].metadata.get('graph_type')}")
            print(f"  - Complexity: {result['document_type'].metadata.get('complexity')}")
            print(f"  - Confidence: {result['confidence']:.1f}")
            print(f"  - Analysis type: {result['analysis'].document_type}")
            
            # Verify it's using the GraphML handler
            if result['handler_used'] != 'GraphMLHandler':
                print(f"❌ Wrong handler used! Expected GraphMLHandler, got {result['handler_used']}")
                return False
            
            # Check analysis details
            findings = result['analysis'].key_findings
            inventory = result['analysis'].data_inventory
            
            print(f"  - Total graphs: {inventory['total_graphs']}")
            print(f"  - Total nodes: {inventory['total_nodes']}")
            print(f"  - Total edges: {inventory['total_edges']}")
            print(f"  - Attribute keys: {inventory['attribute_keys']}")
            print(f"  - Data elements: {inventory['data_elements']}")
            
            # Graph structure
            structure = findings['graph_structure']
            print(f"  - Graph count: {structure['graph_count']}")
            print(f"  - Directed/Undirected: {structure['directed_graphs']}/{structure['undirected_graphs']}")
            
            # Network metrics
            metrics = findings['network_metrics']
            print(f"  - Density: {metrics['density']:.3f}")
            print(f"  - Diameter estimate: {metrics['diameter_estimate']}")
            
            # Connectivity
            connectivity = findings['connectivity']
            print(f"  - Average degree: {connectivity['average_degree']:.2f}")
            print(f"  - Connectivity ratio: {connectivity['connectivity_ratio']:.3f}")
            
            # Quality
            quality = result['analysis'].quality_metrics
            print(f"  - Overall quality: {quality['overall']:.2f}")
            print(f"  - Completeness: {quality['completeness']:.2f}")
            
            print("  ✅ Integration test passed")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == "__main__":
    print("🧪 GraphML Handler Integration Test")
    print("=" * 50)
    
    success = test_graphml_integration()
    
    if success:
        print("\n🎉 GraphML handler integration test passed!")
        sys.exit(0)
    else:
        print("\n❌ GraphML handler integration test failed!")
        sys.exit(1)