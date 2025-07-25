#!/usr/bin/env python3
"""
Test Struts Configuration handler integration with main analyzer
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def test_struts_integration():
    """Test Struts Configuration handler integration with main analyzer"""
    
    try:
        from core.analyzer import XMLDocumentAnalyzer
        print("✅ XMLDocumentAnalyzer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import XMLDocumentAnalyzer: {e}")
        return False
    
    # Test registry import
    try:
        from handlers import ALL_HANDLERS, StrutsConfigHandler
        print(f"✅ Handler registry imported successfully ({len(ALL_HANDLERS)} handlers)")
        
        # Check if StrutsConfigHandler is in the registry
        struts_handler_in_registry = any(h.__name__ == 'StrutsConfigHandler' for h in ALL_HANDLERS)
        print(f"✅ StrutsConfigHandler in registry: {struts_handler_in_registry}")
        
    except ImportError as e:
        print(f"❌ Failed to import handler registry: {e}")
        return False
    
    # Test with sample Struts files
    analyzer = XMLDocumentAnalyzer()
    test_files = [
        "../../sample_data/test_files_synthetic/small/struts/simple_struts_config.xml",
        "../../sample_data/test_files_synthetic/small/struts/enterprise_struts_config.xml"
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
            print(f"  - Config Type: {result['document_type'].metadata.get('config_type')}")
            print(f"  - Complexity: {result['document_type'].metadata.get('complexity')}")
            print(f"  - Confidence: {result['confidence']:.1f}")
            print(f"  - Analysis type: {result['analysis'].document_type}")
            
            # Verify it's using the Struts handler
            if result['handler_used'] != 'StrutsConfigHandler':
                print(f"❌ Wrong handler used! Expected StrutsConfigHandler, got {result['handler_used']}")
                return False
            
            # Check analysis details
            findings = result['analysis'].key_findings
            inventory = result['analysis'].data_inventory
            
            print(f"  - Total actions: {inventory['total_actions']}")
            print(f"  - Form beans: {inventory['form_beans']}")
            print(f"  - Global forwards: {inventory['global_forwards']}")
            print(f"  - Data sources: {inventory['data_sources']}")
            print(f"  - Plugins: {inventory['plugins']}")
            
            # Action mappings
            actions = findings['action_mappings']
            print(f"  - Action count: {actions['action_count']}")
            print(f"  - Action types: {len(actions['action_types'])}")
            
            # Security analysis
            security = findings['security_analysis']
            print(f"  - Validation enabled: {security['validation_enabled']}")
            print(f"  - Potential vulnerabilities: {len(security['potential_vulnerabilities'])}")
            
            # Architecture metrics
            arch_metrics = findings['architecture_metrics']
            print(f"  - Complexity score: {arch_metrics['complexity_score']:.2f}")
            print(f"  - Maintainability: {arch_metrics['maintainability_score']:.2f}")
            
            # Quality
            quality = result['analysis'].quality_metrics
            print(f"  - Overall quality: {quality['overall']:.2f}")
            print(f"  - Security quality: {quality['security_quality']:.2f}")
            
            print("  ✅ Integration test passed")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == "__main__":
    print("🧪 Struts Configuration Handler Integration Test")
    print("=" * 60)
    
    success = test_struts_integration()
    
    if success:
        print("\n🎉 Struts handler integration test passed!")
        sys.exit(0)
    else:
        print("\n❌ Struts handler integration test failed!")
        sys.exit(1)