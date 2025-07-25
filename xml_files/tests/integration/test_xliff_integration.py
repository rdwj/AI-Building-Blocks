#!/usr/bin/env python3
"""
Test XLIFF handler integration with the main framework
"""
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def test_xliff_integration():
    """Test XLIFF handler integration"""
    
    try:
        from xml_schema_analyzer_fixed import XMLSchemaAnalyzer
        from core.analyzer import XMLDocumentAnalyzer
        print("✅ Core modules imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import core modules: {e}")
        return False
    
    # Test files
    test_files = [
        "../../sample_data/test_files_synthetic/small/xliff/simple_translation.xlf",
        "../../sample_data/test_files_synthetic/small/xliff/multilingual_project.xlf",
        "../../sample_data/test_files_synthetic/small/xliff/software_ui_translation.xlf"
    ]
    
    analyzer = XMLDocumentAnalyzer()
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
            
            # Test full analysis
            result = analyzer.analyze_document(test_file)
            analysis = result.get('analysis')
            handler_used = result.get('handler_used', 'Unknown')
            
            if analysis:
                print(f"  - Document type: {analysis.document_type}")
                print(f"  - Translation units: {analysis.data_inventory.get('translation_units', 'N/A')}")
                print(f"  - Source language: {analysis.data_inventory.get('source_language', 'N/A')}")
                print(f"  - Target languages: {analysis.data_inventory.get('target_languages', 'N/A')}")
                print(f"  - Quality score: {analysis.quality_metrics.get('overall', 0.0):.2f}")
                
                # Verify it's using XLIFF handler
                if 'XLIFF' in handler_used:
                    print("✅ XLIFF handler correctly detected and used")
                    success_count += 1
                else:
                    print(f"❌ Wrong handler detected: {handler_used}")
            else:
                print(f"❌ No specialized analysis found. Handler used: {handler_used}")
            
        except Exception as e:
            print(f"❌ Error processing {test_file}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n📊 Integration Test Results: {success_count}/{len(test_files)} files processed successfully")
    return success_count == len(test_files)

if __name__ == "__main__":
    print("🧪 XLIFF Handler Integration Test")
    print("=" * 50)
    
    success = test_xliff_integration()
    
    if success:
        print("\n🎉 XLIFF handler integration test passed!")
        sys.exit(0)
    else:
        print("\n❌ XLIFF handler integration test failed!")
        sys.exit(1)