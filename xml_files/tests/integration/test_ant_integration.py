#!/usr/bin/env python3
"""
Test Ant Handler Integration

Test that the Ant handler works properly with the main XML analyzer.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_integration():
    """Test Ant handler integration with main analyzer"""
    print("🔗 Testing Ant Handler Integration")
    print("=" * 50)
    
    try:
        # Import main analyzer
        from core.analyzer import XMLDocumentAnalyzer
        
        # Create analyzer (should load Ant handler from registry)
        analyzer = XMLDocumentAnalyzer()
        print(f"✅ Analyzer created with {len(analyzer.handlers)} handlers")
        
        # Check if Ant handler is loaded
        ant_handler_loaded = any(handler.__class__.__name__ == 'AntBuildHandler' for handler in analyzer.handlers)
        print(f"✅ Ant handler loaded: {ant_handler_loaded}")
        
        # Test with an Ant build file
        test_file = "../../sample_data/test_files_synthetic/small/ant/build.xml"
        if not Path(test_file).exists():
            print("❌ Test file not found, skipping integration test")
            return False
        
        print(f"\n🧪 Testing integration with: {Path(test_file).name}")
        
        # Analyze the file
        result = analyzer.analyze_document(test_file)
        
        # Check results
        if 'error' in result:
            print(f"❌ Analysis failed: {result['error']}")
            return False
        
        print("✅ Analysis completed successfully")
        print(f"  📄 Document Type: {result['document_type'].type_name}")
        print(f"  🎯 Handler Used: {result['handler_used']}")
        print(f"  📊 Confidence: {result['confidence']:.2f}")
        
        # Verify it's using the Ant handler
        if result['handler_used'] != 'AntBuildHandler':
            print(f"❌ Expected AntBuildHandler, got {result['handler_used']}")
            return False
        
        if result['document_type'].type_name != 'Apache Ant Build':
            print(f"❌ Expected 'Apache Ant Build', got {result['document_type'].type_name}")
            return False
        
        # Check analysis details
        analysis = result.get('analysis')
        if analysis:
            print(f"  🔍 Key Findings:")
            print(f"    - Targets: {len(analysis.key_findings.get('targets', []))}")
            print(f"    - Properties: {len(analysis.key_findings.get('properties', {}).get('inline_properties', {}))}")
            print(f"    - Quality Score: {analysis.quality_metrics.get('overall', 0):.2f}")
        
        print("\n🎉 Integration test PASSED!")
        print("✅ Ant handler is properly integrated with the main analyzer")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    success = test_integration()
    
    if success:
        print(f"\n✅ Ant Build Handler successfully implemented and integrated!")
        print(f"📊 Ready to update checklist and move to next handler")
    else:
        print(f"\n❌ Integration issues found - fix before proceeding")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)