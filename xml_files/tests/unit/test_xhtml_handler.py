#!/usr/bin/env python3
"""
Test XHTML handler implementation
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def test_xhtml_handler_import():
    """Test importing the XHTML handler"""
    try:
        from handlers.xhtml_handler import XHTMLHandler
        print("✅ XHTMLHandler imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import XHTMLHandler: {e}")
        return False

def test_xhtml_handler_instantiation():
    """Test creating XHTML handler instance"""
    try:
        from handlers.xhtml_handler import XHTMLHandler
        handler = XHTMLHandler()
        print("✅ XHTMLHandler instantiated successfully")
        return handler
    except Exception as e:
        print(f"❌ Failed to instantiate XHTMLHandler: {e}")
        return None

def test_xhtml_files():
    """Test XHTML handler with sample files"""
    from handlers.xhtml_handler import XHTMLHandler
    import xml.etree.ElementTree as ET
    
    handler = XHTMLHandler()
    test_files = [
        "../../sample_data/test_files_synthetic/small/xhtml/simple_page.xhtml",
        "../../sample_data/test_files_synthetic/small/xhtml/form_page.xhtml", 
        "../../sample_data/test_files_synthetic/small/xhtml/semantic_article.xhtml",
        "../../sample_data/test_files_synthetic/small/xhtml/basic_webpage.xhtml"
    ]
    
    results = []
    
    for test_file in test_files:
        if not Path(test_file).exists():
            print(f"❌ Test file not found: {test_file}")
            continue
            
        print(f"\n🔍 Testing {test_file}")
        
        try:
            # Parse XML
            tree = ET.parse(test_file)
            root = tree.getroot()
            
            # Extract namespaces
            namespaces = {}
            for event, elem in ET.iterparse(test_file, events=['start-ns']):
                if event == 'start-ns':
                    prefix, uri = elem
                    namespaces[prefix or 'default'] = uri
            
            # Test can_handle
            can_handle, confidence = handler.can_handle(root, namespaces)
            print(f"  - can_handle: {can_handle} (confidence: {confidence:.2f})")
            
            if can_handle:
                # Test detect_type
                doc_type = handler.detect_type(root, namespaces)
                print(f"  - Document type: {doc_type.type_name}")
                print(f"  - Version: {doc_type.version}")
                print(f"  - Document subtype: {doc_type.metadata.get('document_type', 'unknown')}")
                print(f"  - Confidence: {doc_type.confidence:.2f}")
                
                # Test analyze
                analysis = handler.analyze(root, test_file)
                print(f"  - Analysis type: {analysis.document_type}")
                print(f"  - Key findings keys: {list(analysis.key_findings.keys())}")
                print(f"  - Data inventory: {analysis.data_inventory}")
                print(f"  - AI use cases: {len(analysis.ai_use_cases)}")
                
                # Show specific findings
                findings = analysis.key_findings
                
                # Structure
                structure = findings['document_structure']
                print(f"  - Total elements: {structure['total_elements']}")
                print(f"  - Max depth: {structure['max_depth']}")
                
                # Content
                content = findings['content_analysis']
                print(f"  - Headings: {sum(content['headings'].values()) if content['headings'] else 0}")
                print(f"  - Paragraphs: {content['paragraphs']}")
                print(f"  - Language: {content.get('language', 'unknown')}")
                
                # Semantic elements
                semantic = findings['semantic_elements']
                print(f"  - Semantic elements: {semantic['total_semantic']}")
                
                # Metadata
                metadata = findings['metadata']
                if metadata['title']:
                    print(f"  - Title: {metadata['title'][:50]}...")
                
                # Accessibility
                accessibility = findings['accessibility']
                if accessibility['alt_texts'] + accessibility['missing_alt_texts'] > 0:
                    total_images = accessibility['alt_texts'] + accessibility['missing_alt_texts']
                    alt_ratio = accessibility['alt_texts'] / total_images * 100
                    print(f"  - Image accessibility: {alt_ratio:.0f}% have alt text")
                
                # Forms
                forms = findings['forms']
                if forms['form_count'] > 0:
                    print(f"  - Forms: {forms['form_count']} with {forms['total_inputs']} inputs")
                
                # Links and media
                links_media = findings['links_and_media']
                print(f"  - Links: {links_media['total_links']} ({links_media['external_links']} external)")
                print(f"  - Images: {links_media['images']}")
                
                print(f"  - Quality metrics: {analysis.quality_metrics}")
                
                # Test extract_key_data
                key_data = handler.extract_key_data(root)
                print(f"  - Key data keys: {list(key_data.keys())}")
                
                results.append({
                    'file': test_file,
                    'success': True,
                    'confidence': confidence,
                    'total_elements': structure['total_elements'],
                    'semantic_elements': semantic['total_semantic'],
                    'forms': forms['form_count'],
                    'links': links_media['total_links'],
                    'document_subtype': doc_type.metadata.get('document_type'),
                    'language': content.get('language')
                })
                print("  ✅ Test passed")
            else:
                results.append({
                    'file': test_file,
                    'success': False,
                    'reason': 'Handler rejected file'
                })
                print("  ❌ Handler cannot handle this file")
                
        except Exception as e:
            print(f"  ❌ Test failed: {e}")
            results.append({
                'file': test_file,
                'success': False,
                'reason': str(e)
            })
            import traceback
            traceback.print_exc()
    
    return results

def main():
    print("🧪 XHTML Handler Test Suite")
    print("=" * 50)
    
    # Test import
    if not test_xhtml_handler_import():
        return False
    
    # Test instantiation
    handler = test_xhtml_handler_instantiation()
    if not handler:
        return False
    
    # Test with files
    results = test_xhtml_files()
    
    # Summary
    print(f"\n📊 Test Results Summary")
    print("=" * 30)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    
    if successful:
        avg_confidence = sum(r['confidence'] for r in successful) / len(successful)
        print(f"📈 Average confidence: {avg_confidence:.2f}")
        
        total_elements = sum(r.get('total_elements', 0) for r in successful)
        total_semantic = sum(r.get('semantic_elements', 0) for r in successful)
        total_forms = sum(r.get('forms', 0) for r in successful)
        total_links = sum(r.get('links', 0) for r in successful)
        
        print(f"🔖 Total elements analyzed: {total_elements}")
        print(f"🎯 Total semantic elements: {total_semantic}")
        print(f"📝 Total forms detected: {total_forms}")
        print(f"🔗 Total links detected: {total_links}")
        
        print(f"\n📋 Document Types Detected:")
        doc_types = {}
        for result in successful:
            dt = result.get('document_subtype', 'unknown')
            doc_types[dt] = doc_types.get(dt, 0) + 1
        for dt, count in doc_types.items():
            print(f"  - {dt}: {count}")
        
        print(f"\n🌍 Languages Detected:")
        languages = {}
        for result in successful:
            lang = result.get('language', 'unknown')
            languages[lang] = languages.get(lang, 0) + 1
        for lang, count in languages.items():
            print(f"  - {lang or 'unknown'}: {count}")
    
    if failed:
        print("\n❌ Failed tests:")
        for result in failed:
            print(f"  - {Path(result['file']).name}: {result['reason']}")
    
    success_rate = len(successful) / len(results) * 100 if results else 0
    print(f"\n🎯 Success rate: {success_rate:.1f}%")
    
    return success_rate == 100.0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)