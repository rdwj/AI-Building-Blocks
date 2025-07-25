#!/usr/bin/env python3
"""
Test Struts Configuration handler implementation
"""
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def test_struts_handler():
    """Test Struts Configuration handler with sample files"""
    
    try:
        from handlers.struts_config_handler import StrutsConfigHandler
        print("✅ StrutsConfigHandler imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import StrutsConfigHandler: {e}")
        return False
    
    # Test files
    test_files = [
        "../../sample_data/test_files_synthetic/small/struts/simple_struts_config.xml",
        "../../sample_data/test_files_synthetic/small/struts/enterprise_struts_config.xml",
        "../../sample_data/test_files_synthetic/small/struts/legacy_struts_config.xml"
    ]
    
    handler = StrutsConfigHandler()
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
            print(f"  - Config type: {doc_type.metadata.get('config_type')}")
            print(f"  - Complexity: {doc_type.metadata.get('complexity')}")
            print(f"  - Action count: {doc_type.metadata.get('action_count')}")
            
            # Test analyze
            analysis = handler.analyze(root, test_file)
            print(f"  - Analysis type: {analysis.document_type}")
            
            # Check key findings
            findings = analysis.key_findings
            
            # Configuration info
            config_info = findings['configuration_info']
            print(f"  - Root element: {config_info['root_element']}")
            print(f"  - Main sections: {config_info['main_sections']}")
            
            # Action mappings
            actions = findings['action_mappings']
            print(f"  - Action count: {actions['action_count']}")
            print(f"  - Action types: {len(actions['action_types'])}")
            print(f"  - Scope usage: {actions['scope_usage']}")
            
            # Form beans
            forms = findings['form_beans']
            print(f"  - Form beans: {forms['bean_count']}")
            print(f"  - Dynamic forms: {forms['dynamic_forms']}")
            print(f"  - Form types: {len(forms['form_types'])}")
            
            # Global forwards
            forwards = findings['global_forwards']
            print(f"  - Global forwards: {forwards['forward_count']}")
            print(f"  - Redirects: {forwards['redirect_count']}")
            
            # Data sources
            data_sources = findings['data_sources']
            print(f"  - Data sources: {data_sources['source_count']}")
            print(f"  - Driver types: {list(data_sources['driver_types'].keys())}")
            
            # Plugins
            plugins = findings['plugins']
            print(f"  - Plugin count: {plugins['plugin_count']}")
            print(f"  - Tiles integration: {plugins['tiles_integration']}")
            print(f"  - Validator integration: {plugins['validator_integration']}")
            
            # Security analysis
            security = findings['security_analysis']
            print(f"  - Validation enabled: {security['validation_enabled']}")
            print(f"  - Potential vulnerabilities: {len(security['potential_vulnerabilities'])}")
            if security['potential_vulnerabilities']:
                print(f"    * {security['potential_vulnerabilities'][0]}")
            
            # Architecture metrics
            arch_metrics = findings['architecture_metrics']
            print(f"  - Complexity score: {arch_metrics['complexity_score']:.2f}")
            print(f"  - Maintainability score: {arch_metrics['maintainability_score']:.2f}")
            print(f"  - Action to form ratio: {arch_metrics['action_to_form_ratio']:.2f}")
            
            # Data inventory
            inventory = analysis.data_inventory
            print(f"  - Total actions: {inventory['total_actions']}")
            print(f"  - Form beans: {inventory['form_beans']}")
            print(f"  - Global forwards: {inventory['global_forwards']}")
            print(f"  - Data sources: {inventory['data_sources']}")
            print(f"  - Plugins: {inventory['plugins']}")
            
            # Quality metrics
            quality = analysis.quality_metrics
            print(f"  - Overall quality: {quality['overall']:.2f}")
            print(f"  - Design quality: {quality['design_quality']:.2f}")
            print(f"  - Security quality: {quality['security_quality']:.2f}")
            print(f"  - Maintainability: {quality['maintainability']:.2f}")
            
            # Structured data
            structured_data = analysis.structured_data
            print(f"  - App structure keys: {list(structured_data['application_structure'].keys())}")
            print(f"  - Action catalog count: {len(structured_data['action_catalog'])}")
            print(f"  - Form definitions: {len(structured_data['form_definitions'])}")
            
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
    print("🧪 Struts Configuration Handler Test")
    print("=" * 50)
    
    success = test_struts_handler()
    
    if success:
        print("\n🎉 All Struts handler tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some Struts handler tests failed!")
        sys.exit(1)