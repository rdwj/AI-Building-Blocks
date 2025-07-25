#!/usr/bin/env python3
"""
Test script for SVG Handler
Tests the SVG handler against synthetic test files.
"""

import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

# Test individual handler
try:
    from handlers.svg_handler import SVGHandler
    print("✅ SVGHandler imported successfully")
except ImportError as e:
    print(f"❌ Failed to import SVGHandler: {e}")
    sys.exit(1)

def test_handler():
    """Test the SVG handler with synthetic files"""
    
    handler = SVGHandler()
    test_files_dir = Path("../../sample_data/test_files_synthetic/small/svg")
    
    if not test_files_dir.exists():
        print(f"❌ Test files directory not found: {test_files_dir}")
        return False
    
    svg_files = list(test_files_dir.glob("*.svg"))
    if not svg_files:
        print(f"❌ No SVG files found in {test_files_dir}")
        return False
    
    print(f"\n🔍 Testing SVG handler with {len(svg_files)} files...")
    
    success_count = 0
    total_count = len(svg_files)
    
    for svg_file in svg_files:
        print(f"\n📄 Testing: {svg_file.name}")
        
        try:
            # Parse the XML file
            tree = ET.parse(svg_file)
            root = tree.getroot()
            
            # Extract namespaces
            namespaces = {}
            for key, value in root.attrib.items():
                if key.startswith('xmlns'):
                    prefix = key.split(':')[1] if ':' in key else 'default'
                    namespaces[prefix] = value
            
            # Test can_handle
            can_handle, confidence = handler.can_handle(root, namespaces)
            print(f"  ✓ can_handle: {can_handle} (confidence: {confidence:.1f})")
            
            if not can_handle:
                print(f"  ❌ Handler cannot handle this file")
                continue
            
            # Test detect_type
            doc_type = handler.detect_type(root, namespaces)
            print(f"  ✓ detect_type: {doc_type.type_name} (v{doc_type.version})")
            
            # Test extract_key_data
            key_data = handler.extract_key_data(root)
            print(f"  ✓ extract_key_data: {len(key_data)} sections")
            
            # Test full analysis
            analysis = handler.analyze(root, str(svg_file))
            print(f"  ✓ analyze: {analysis.document_type}")
            print(f"    - Key findings: {len(analysis.key_findings)} sections")
            print(f"    - Recommendations: {len(analysis.recommendations)} items")
            print(f"    - AI use cases: {len(analysis.ai_use_cases)} cases")
            print(f"    - Data inventory: {sum(analysis.data_inventory.values())} items")
            print(f"    - Quality score: {analysis.quality_metrics.get('overall', 0):.2f}")
            
            # Test specific SVG analysis
            svg_info = analysis.key_findings.get('svg_info', {})
            print(f"    - SVG type: {svg_info.get('svg_type', 'Unknown')}")
            
            dimensions = analysis.key_findings.get('dimensions', {})
            print(f"    - Dimensions: {dimensions.get('width', 'auto')} x {dimensions.get('height', 'auto')}")
            
            accessibility = analysis.key_findings.get('accessibility', {})
            print(f"    - Accessibility score: {accessibility.get('accessibility_score', 0):.2f}")
            
            success_count += 1
            print(f"  ✅ {svg_file.name} - SUCCESS")
            
        except Exception as e:
            print(f"  ❌ {svg_file.name} - ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n📊 SVG Handler Test Results:")
    print(f"✅ Success: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    return success_count == total_count

if __name__ == "__main__":
    print("🧪 SVG Handler Test Suite")
    print("=" * 50)
    
    success = test_handler()
    
    if success:
        print("\n🎉 All tests passed! SVG handler is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the handler implementation.")
        sys.exit(1)