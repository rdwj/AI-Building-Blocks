#!/usr/bin/env python3
"""
Test script for DocBook Handler
Tests the DocBook handler against synthetic test files.
"""

import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

# Test individual handler
try:
    from handlers.docbook_handler import DocBookHandler
    print("✅ DocBookHandler imported successfully")
except ImportError as e:
    print(f"❌ Failed to import DocBookHandler: {e}")
    sys.exit(1)

def test_handler():
    """Test the DocBook handler with synthetic files"""
    
    handler = DocBookHandler()
    test_files_dir = Path("../../sample_data/test_files_synthetic/small/docbook")
    
    if not test_files_dir.exists():
        print(f"❌ Test files directory not found: {test_files_dir}")
        return False
    
    docbook_files = list(test_files_dir.glob("*.xml"))
    if not docbook_files:
        print(f"❌ No DocBook files found in {test_files_dir}")
        return False
    
    print(f"\n🔍 Testing DocBook handler with {len(docbook_files)} files...")
    
    success_count = 0
    total_count = len(docbook_files)
    
    for docbook_file in docbook_files:
        print(f"\n📄 Testing: {docbook_file.name}")
        
        try:
            # Parse the XML file
            tree = ET.parse(docbook_file)
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
            print(f"    - Document type: {doc_type.metadata.get('document_type', 'unknown')}")
            
            # Test extract_key_data
            key_data = handler.extract_key_data(root)
            print(f"  ✓ extract_key_data: {len(key_data)} sections")
            print(f"    - Title: {key_data['document_metadata']['title']}")
            
            # Test full analysis
            analysis = handler.analyze(root, str(docbook_file))
            print(f"  ✓ analyze: {analysis.document_type}")
            print(f"    - Key findings: {len(analysis.key_findings)} sections")
            print(f"    - Recommendations: {len(analysis.recommendations)} items")
            print(f"    - AI use cases: {len(analysis.ai_use_cases)} cases")
            print(f"    - Data inventory: {sum(analysis.data_inventory.values())} items")
            print(f"    - Quality score: {analysis.quality_metrics.get('overall', 0):.2f}")
            
            # Test specific DocBook analysis
            docbook_info = analysis.key_findings.get('docbook_info', {})
            print(f"    - DocBook version: {docbook_info.get('version', 'Unknown')}")
            
            structure = analysis.key_findings.get('structure', {})
            print(f"    - Chapters: {len(structure.get('chapters', []))}")
            print(f"    - Sections: {structure.get('total_sections', 0)}")
            
            content = analysis.key_findings.get('content_stats', {})
            print(f"    - Paragraphs: {content.get('paragraphs', 0)}")
            print(f"    - Examples: {len(content.get('code_examples', []))}")
            
            quality = analysis.key_findings.get('quality_indicators', {})
            if quality:
                print(f"    - Quality score: {quality.get('quality_score', 0):.2f}")
            
            success_count += 1
            print(f"  ✅ {docbook_file.name} - SUCCESS")
            
        except Exception as e:
            print(f"  ❌ {docbook_file.name} - ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n📊 DocBook Handler Test Results:")
    print(f"✅ Success: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    return success_count == total_count

if __name__ == "__main__":
    print("🧪 DocBook Handler Test Suite")
    print("=" * 50)
    
    success = test_handler()
    
    if success:
        print("\n🎉 All tests passed! DocBook handler is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the handler implementation.")
        sys.exit(1)