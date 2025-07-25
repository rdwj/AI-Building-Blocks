#!/usr/bin/env python3
"""
Test WADL handler integration with main analyzer
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def test_wadl_integration():
    """Test WADL handler integration with main analyzer"""
    
    try:
        from core.analyzer import XMLDocumentAnalyzer
        print("✅ XMLDocumentAnalyzer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import XMLDocumentAnalyzer: {e}")
        return False
    
    # Test registry import
    try:
        from handlers import ALL_HANDLERS, WADLHandler
        print(f"✅ Handler registry imported successfully ({len(ALL_HANDLERS)} handlers)")
        
        # Check if WADLHandler is in the registry
        wadl_handler_in_registry = any(h.__name__ == 'WADLHandler' for h in ALL_HANDLERS)
        print(f"✅ WADLHandler in registry: {wadl_handler_in_registry}")
        
    except ImportError as e:
        print(f"❌ Failed to import handler registry: {e}")
        return False
    
    # Test with sample WADL files
    analyzer = XMLDocumentAnalyzer()
    test_files = [
        "../../sample_data/test_files_synthetic/small/wadl/simple_api.wadl",
        "../../sample_data/test_files_synthetic/small/wadl/complex_api.wadl"
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
            print(f"  - API Type: {result['document_type'].metadata.get('api_type')}")
            print(f"  - Confidence: {result['confidence']:.1f}")
            print(f"  - Analysis type: {result['analysis'].document_type}")
            
            # Verify it's using the WADL handler
            if result['handler_used'] != 'WADLHandler':
                print(f"❌ Wrong handler used! Expected WADLHandler, got {result['handler_used']}")
                return False
            
            # Check analysis details
            findings = result['analysis'].key_findings
            inventory = result['analysis'].data_inventory
            
            print(f"  - Total resources: {inventory['total_resources']}")
            print(f"  - Total methods: {inventory['total_methods']}")
            print(f"  - Total parameters: {inventory['total_parameters']}")
            print(f"  - Representation formats: {inventory['representation_formats']}")
            
            # Application info
            app_info = findings['application_info']
            print(f"  - Base URI: {app_info['base_uri']}")
            print(f"  - Title: {app_info['title']}")
            
            # Method distribution
            methods = findings['methods']
            print(f"  - Method distribution: {methods['method_distribution']}")
            
            # Security
            security = findings['security']
            print(f"  - Has authentication: {security['has_authentication']}")
            print(f"  - HTTPS required: {security['https_required']}")
            
            # Quality
            quality = result['analysis'].quality_metrics
            print(f"  - Overall quality: {quality['overall']:.2f}")
            print(f"  - Design quality: {quality['design_quality']:.2f}")
            
            print("  ✅ Integration test passed")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == "__main__":
    print("🧪 WADL Handler Integration Test")
    print("=" * 50)
    
    success = test_wadl_integration()
    
    if success:
        print("\n🎉 WADL handler integration test passed!")
        sys.exit(0)
    else:
        print("\n❌ WADL handler integration test failed!")
        sys.exit(1)