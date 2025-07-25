#!/usr/bin/env python3
"""
Test XLIFF handler implementation
"""
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def test_xliff_handler():
    """Test XLIFF handler with sample files"""
    
    try:
        from handlers.xliff_handler import XLIFFHandler
        print("✅ XLIFFHandler imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import XLIFFHandler: {e}")
        return False
    
    # Test files
    test_files = [
        "../../sample_data/test_files_synthetic/small/xliff/simple_translation.xlf",
        "../../sample_data/test_files_synthetic/small/xliff/multilingual_project.xlf",
        "../../sample_data/test_files_synthetic/small/xliff/software_ui_translation.xlf"
    ]
    
    handler = XLIFFHandler()
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
            print(f"  - Document subtype: {doc_type.metadata.get('document_type')}")
            print(f"  - Complexity: {doc_type.metadata.get('complexity')}")
            print(f"  - Workflow state: {doc_type.metadata.get('workflow_state')}")
            print(f"  - Translation units: {doc_type.metadata.get('translation_units')}")
            print(f"  - File count: {doc_type.metadata.get('file_count')}")
            
            # Test analyze
            analysis = handler.analyze(root, test_file)
            print(f"  - Analysis type: {analysis.document_type}")
            
            # Check key findings
            findings = analysis.key_findings
            
            # File info
            file_info = findings['file_info']
            print(f"  - XLIFF version: {file_info['version']}")
            print(f"  - Tool name: {file_info['tool_name']}")
            
            # Translation files
            files = findings['translation_files']
            print(f"  - File count: {files['file_count']}")
            print(f"  - Source languages: {files['source_languages']}")
            print(f"  - Target languages: {files['target_languages']}")
            
            # Translation units
            units = findings['translation_units']
            print(f"  - Translation units: {units['unit_count']}")
            print(f"  - Approved: {units['approved_count']}")
            print(f"  - Locked: {units['locked_count']}")
            print(f"  - Empty targets: {units['empty_targets']}")
            print(f"  - States: {list(units['states'].keys())}")
            
            # Languages
            languages = findings['languages']
            print(f"  - Source language: {languages['source_language']}")
            print(f"  - Target languages: {languages['target_languages']}")
            print(f"  - Language pairs: {languages['language_pairs']}")
            print(f"  - Multilingual: {languages['multilingual']}")
            
            # Workflow state
            workflow = findings['workflow_state']
            print(f"  - Completion: {workflow['completion_percentage']:.1f}%")
            print(f"  - Translated: {workflow['translated_count']}")
            print(f"  - Needs work: {workflow['needs_work_count']}")
            
            # Translation memory
            tm = findings['translation_memory']
            print(f"  - Has TM matches: {tm['has_tm_matches']}")
            print(f"  - Exact matches: {tm['exact_matches']}")
            print(f"  - Fuzzy matches: {tm['fuzzy_matches']}")
            
            # Notes and comments
            notes = findings['notes_comments']
            print(f"  - Note count: {notes['note_count']}")
            print(f"  - Translator notes: {notes['translator_notes']}")
            print(f"  - Reviewer notes: {notes['reviewer_notes']}")
            
            # Quality metrics
            quality_metrics = findings['quality_metrics']
            print(f"  - Completion rate: {quality_metrics['completion_rate']:.1f}%")
            print(f"  - Approval rate: {quality_metrics['approval_rate']:.1f}%")
            print(f"  - Empty target rate: {quality_metrics['empty_target_rate']:.1f}%")
            
            # Localization metadata
            l10n = findings['localization_metadata']
            print(f"  - Data types: {l10n['datatypes']}")
            print(f"  - Original formats: {l10n['original_formats']}")
            print(f"  - Phase count: {len(l10n['phase_info'])}")
            
            # Translation tools
            tools = findings['translation_tools']
            print(f"  - Primary tool: {tools['primary_tool']}")
            print(f"  - Tool count: {tools['tool_count']}")
            
            # Data inventory
            inventory = analysis.data_inventory
            print(f"  - Total files: {inventory['total_files']}")
            print(f"  - Translation units: {inventory['translation_units']}")
            print(f"  - Source language: {inventory['source_language']}")
            print(f"  - Target languages: {inventory['target_languages']}")
            print(f"  - Translated units: {inventory['translated_units']}")
            print(f"  - Completion rate: {inventory['completion_rate']:.1f}%")
            
            # Quality assessment
            quality = analysis.quality_metrics
            print(f"  - Overall quality: {quality['overall']:.2f}")
            print(f"  - Completeness: {quality['completeness']:.2f}")
            print(f"  - Consistency: {quality['consistency']:.2f}")
            print(f"  - Workflow health: {quality['workflow_health']:.2f}")
            print(f"  - Localization readiness: {quality['localization_readiness']:.2f}")
            
            # Structured data
            structured_data = analysis.structured_data
            print(f"  - Project metadata keys: {list(structured_data['translation_project'].keys())}")
            print(f"  - Translation catalog count: {len(structured_data['translation_catalog'])}")
            print(f"  - Language pairs: {len(structured_data['language_pairs'])}")
            
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
    print("🧪 XLIFF Handler Test")
    print("=" * 50)
    
    success = test_xliff_handler()
    
    if success:
        print("\n🎉 All XLIFF handler tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some XLIFF handler tests failed!")
        sys.exit(1)