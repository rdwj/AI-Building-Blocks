#!/usr/bin/env python3
"""
Test WADL handler implementation
"""
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def test_wadl_handler():
    """Test WADL handler with sample files"""
    
    try:
        from handlers.wadl_handler import WADLHandler
        print("✅ WADLHandler imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import WADLHandler: {e}")
        return False
    
    # Test files
    test_files = [
        "../../sample_data/test_files_synthetic/small/wadl/simple_api.wadl",
        "../../sample_data/test_files_synthetic/small/wadl/complex_api.wadl"
    ]
    
    handler = WADLHandler()
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
            print(f"  - API type: {doc_type.metadata.get('api_type')}")
            print(f"  - Methods: {doc_type.metadata.get('methods')}")
            
            # Test analyze
            analysis = handler.analyze(root, test_file)
            print(f"  - Analysis type: {analysis.document_type}")
            
            # Check key findings
            findings = analysis.key_findings
            
            # Application info
            app_info = findings['application_info']
            print(f"  - Base URI: {app_info['base_uri']}")
            print(f"  - Title: {app_info['title']}")
            
            # Resources
            resources = findings['resources']
            print(f"  - Resource count: {resources['resource_count']}")
            print(f"  - Base paths: {resources['base_paths'][:3]}")
            
            # Methods
            methods = findings['methods']
            print(f"  - Method count: {methods['method_count']}")
            print(f"  - Method distribution: {methods['method_distribution']}")
            
            # Parameters
            parameters = findings['parameters']
            print(f"  - Parameter count: {parameters['parameter_count']}")
            print(f"  - Required params: {parameters['required_params']}")
            print(f"  - Parameter styles: {list(parameters['parameter_styles'].keys())}")
            
            # Representations
            representations = findings['representations']
            print(f"  - Representation count: {representations['representation_count']}")
            print(f"  - Media types: {representations['media_types']}")
            
            # Grammars
            grammars = findings['grammars']
            print(f"  - Has grammars: {grammars['has_grammars']}")
            print(f"  - Schema count: {grammars['schemas']}")
            
            # Documentation
            documentation = findings['documentation']
            print(f"  - Documentation coverage: {documentation['coverage_score']:.2f}")
            
            # Security
            security = findings['security']
            print(f"  - Has authentication: {security['has_authentication']}")
            print(f"  - HTTPS required: {security['https_required']}")
            print(f"  - Auth methods: {security['auth_methods'][:3]}")
            
            # API metrics
            api_metrics = findings['api_metrics']
            print(f"  - Complexity score: {api_metrics['complexity_score']:.2f}")
            print(f"  - CRUD completeness: {api_metrics['crud_completeness']:.2f}")
            
            # Data inventory
            inventory = analysis.data_inventory
            print(f"  - Total resources: {inventory['total_resources']}")
            print(f"  - Total methods: {inventory['total_methods']}")
            print(f"  - Total parameters: {inventory['total_parameters']}")
            
            # Quality metrics
            quality = analysis.quality_metrics
            print(f"  - Overall quality: {quality['overall']:.2f}")
            print(f"  - Design quality: {quality['design_quality']:.2f}")
            print(f"  - Documentation quality: {quality['documentation_quality']:.2f}")
            
            # Structured data
            structured_data = analysis.structured_data
            print(f"  - API spec keys: {list(structured_data['api_specification'].keys())}")
            print(f"  - Endpoint count: {len(structured_data['endpoint_catalog'])}")
            
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
    print("🧪 WADL Handler Test")
    print("=" * 50)
    
    success = test_wadl_handler()
    
    if success:
        print("\n🎉 All WADL handler tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some WADL handler tests failed!")
        sys.exit(1)