#!/usr/bin/env python3
"""
Test GraphML handler implementation
"""
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def test_graphml_handler():
    """Test GraphML handler with sample files"""
    
    try:
        from handlers.graphml_handler import GraphMLHandler
        print("✅ GraphMLHandler imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import GraphMLHandler: {e}")
        return False
    
    # Test files
    test_files = [
        "../../sample_data/test_files_synthetic/small/graphml/simple_network.graphml",
        "../../sample_data/test_files_synthetic/small/graphml/neural_network.graphml",
        "../../sample_data/test_files_synthetic/small/graphml/dependency_graph.graphml"
    ]
    
    handler = GraphMLHandler()
    success_count = 0
    
    for test_file in test_files:
        if not Path(test_file).exists():
            print(f"❌ Test file not found: {test_file}")
            continue
        
        print(f"\n🔍 Testing {test_file}")
        
        try:
            import xml.etree.ElementTree as ET
            
            # Parse the XML
            tree = ET.parse(test_file)
            root = tree.getroot()
            
            # Extract namespaces
            namespaces = {}
            for prefix, uri in ET.iterparse(test_file, events=('start-ns',)):
                namespaces[prefix] = uri
            
            # Test can_handle
            can_handle, confidence = handler.can_handle(root, namespaces)
            print(f"  - Can handle: {can_handle} (confidence: {confidence:.2f})")
            
            if not can_handle:
                print(f"❌ Handler cannot handle this file")
                continue
            
            # Test detect_type
            doc_type = handler.detect_type(root, namespaces)
            print(f"  - Document type: {doc_type.type_name}")
            print(f"  - Version: {doc_type.version}")
            print(f"  - Graph type: {doc_type.metadata.get('graph_type')}")
            print(f"  - Complexity: {doc_type.metadata.get('complexity')}")
            print(f"  - Node count: {doc_type.metadata.get('node_count')}")
            print(f"  - Edge count: {doc_type.metadata.get('edge_count')}")
            
            # Test analyze
            analysis = handler.analyze(root, test_file)
            print(f"  - Analysis type: {analysis.document_type}")
            
            # Check key findings
            findings = analysis.key_findings
            
            # File info
            file_info = findings['file_info']
            print(f"  - Root element: {file_info['root_element']}")
            print(f"  - Version: {file_info['version']}")
            
            # Graph structure
            structure = findings['graph_structure']
            print(f"  - Graph count: {structure['graph_count']}")
            print(f"  - Directed graphs: {structure['directed_graphs']}")
            print(f"  - Undirected graphs: {structure['undirected_graphs']}")
            
            # Nodes
            nodes = findings['nodes']
            print(f"  - Node count: {nodes['node_count']}")
            print(f"  - Isolated nodes: {nodes['isolated_nodes']}")
            print(f"  - Max degree: {nodes['max_degree']}")
            print(f"  - Node attributes: {len(nodes['node_attributes'])}")
            
            # Edges
            edges = findings['edges']
            print(f"  - Edge count: {edges['edge_count']}")
            print(f"  - Self loops: {edges['self_loops']}")
            print(f"  - Parallel edges: {edges['parallel_edges']}")
            print(f"  - Edge attributes: {len(edges['edge_attributes'])}")
            
            # Attributes
            attributes = findings['attributes']
            print(f"  - Attribute keys: {attributes['key_count']}")
            print(f"  - Attribute types: {list(attributes['attribute_types'].keys())}")
            
            # Network metrics
            metrics = findings['network_metrics']
            print(f"  - Density: {metrics['density']:.3f}")
            print(f"  - Avg clustering: {metrics['avg_clustering']:.3f}")
            print(f"  - Diameter estimate: {metrics['diameter_estimate']}")
            
            # Data properties
            data_props = findings['data_properties']
            print(f"  - Data elements: {data_props['data_count']}")
            print(f"  - Empty data: {data_props['empty_data']}")
            print(f"  - Value types: {list(data_props['value_types'].keys())}")
            
            # Layout info
            layout = findings['layout_info']
            print(f"  - Has coordinates: {layout['has_coordinates']}")
            print(f"  - Coordinate keys: {layout['coordinate_keys']}")
            print(f"  - Visual attributes: {len(layout['visual_attributes'])}")
            print(f"  - Geometric data: {layout['geometric_data']}")
            
            # Connectivity
            connectivity = findings['connectivity']
            print(f"  - Average degree: {connectivity['average_degree']:.2f}")
            print(f"  - Connectivity ratio: {connectivity['connectivity_ratio']:.3f}")
            
            # Data inventory
            inventory = analysis.data_inventory
            print(f"  - Total graphs: {inventory['total_graphs']}")
            print(f"  - Total nodes: {inventory['total_nodes']}")
            print(f"  - Total edges: {inventory['total_edges']}")
            print(f"  - Attribute keys: {inventory['attribute_keys']}")
            print(f"  - Data elements: {inventory['data_elements']}")
            
            # Quality metrics
            quality = analysis.quality_metrics
            print(f"  - Overall quality: {quality['overall']:.2f}")
            print(f"  - Completeness: {quality['completeness']:.2f}")
            print(f"  - Consistency: {quality['consistency']:.2f}")
            print(f"  - Connectivity: {quality['connectivity']:.2f}")
            print(f"  - Attribute coverage: {quality['attribute_coverage']:.2f}")
            
            # Structured data
            structured_data = analysis.structured_data
            print(f"  - Graph metadata keys: {list(structured_data['graph_metadata'].keys())}")
            print(f"  - Node catalog count: {len(structured_data['node_catalog'])}")
            print(f"  - Edge catalog count: {len(structured_data['edge_catalog'])}")
            print(f"  - Attribute schema keys: {list(structured_data['attribute_schema'].keys())}")
            
            # AI use cases (first 3)
            print(f"  - AI use cases ({len(analysis.ai_use_cases)}): {analysis.ai_use_cases[:3]}")
            
            print(f"✅ {test_file} processed successfully")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Error processing {test_file}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n📊 Test Results: {success_count}/{len(test_files)} files processed successfully")
    return success_count == len(test_files)

if __name__ == "__main__":
    print("🧪 GraphML Handler Test")
    print("=" * 50)
    
    success = test_graphml_handler()
    
    if success:
        print("\n🎉 All GraphML handler tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some GraphML handler tests failed!")
        sys.exit(1)