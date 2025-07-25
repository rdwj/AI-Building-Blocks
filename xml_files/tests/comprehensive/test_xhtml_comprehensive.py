#!/usr/bin/env python3
"""
Comprehensive test of XHTML handler with detailed analysis
"""

import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from core.analyzer import XMLDocumentAnalyzer

def main():
    analyzer = XMLDocumentAnalyzer()
    test_file = "../../sample_data/test_files_synthetic/small/xhtml/form_page.xhtml"
    
    print(f"🌐 Analyzing XHTML file: {test_file}")
    print("=" * 60)
    
    try:
        result = analyzer.analyze_document(test_file)
        
        print(f"Handler Used: {result['handler_used']}")
        print(f"Document Type: {result['document_type'].type_name}")
        print(f"Version: {result['document_type'].version}")
        print(f"Document Subtype: {result['document_type'].metadata.get('document_type')}")
        print(f"Confidence: {result['confidence']:.2f}")
        
        analysis = result['analysis']
        print(f"\nDocument Analysis: {analysis.document_type}")
        print(f"Data Inventory: {analysis.data_inventory}")
        
        findings = analysis.key_findings
        
        # Document structure
        structure = findings['document_structure']
        print(f"\n🏗️ Document Structure:")
        print(f"  - Total Elements: {structure['total_elements']}")
        print(f"  - Max Depth: {structure['max_depth']}")
        print(f"  - Has Head: {structure['has_head']}")
        print(f"  - Has Body: {structure['has_body']}")
        print(f"  - Top Elements: {list(structure['element_counts'].items())[:5]}")
        
        # Content analysis
        content = findings['content_analysis']
        print(f"\n📝 Content Analysis:")
        print(f"  - Language: {content.get('language', 'unknown')}")
        print(f"  - Text Length: {content['text_content_length']} characters")
        print(f"  - Headings: {content['headings']}")
        print(f"  - Paragraphs: {content['paragraphs']}")
        print(f"  - Lists: {content['lists']}")
        print(f"  - Tables: {content['tables']}")
        print(f"  - Sections: {content['sections']}")
        
        # Semantic elements
        semantic = findings['semantic_elements']
        print(f"\n🎯 Semantic Elements:")
        print(f"  - Total Semantic: {semantic['total_semantic']}")
        if semantic['elements']:
            print(f"  - Elements Found: {semantic['elements']}")
        
        # Metadata
        metadata = findings['metadata']
        print(f"\n📋 Metadata:")
        print(f"  - Title: {metadata.get('title')}")
        print(f"  - Description: {metadata.get('description', 'None')[:100]}...")
        print(f"  - Author: {metadata.get('author')}")
        print(f"  - Charset: {metadata.get('charset')}")
        print(f"  - Viewport: {metadata.get('viewport')}")
        print(f"  - Meta Tags: {len(metadata.get('meta_tags', []))}")
        print(f"  - Link Tags: {len(metadata.get('link_tags', []))}")
        
        # Accessibility
        accessibility = findings['accessibility']
        print(f"\n♿ Accessibility:")
        print(f"  - Alt Texts: {accessibility['alt_texts']}")
        print(f"  - Missing Alt Texts: {accessibility['missing_alt_texts']}")
        print(f"  - ARIA Attributes: {accessibility['aria_attributes']}")
        print(f"  - Form Labels: {accessibility['form_labels']}")
        print(f"  - Unlabeled Inputs: {accessibility['unlabeled_inputs']}")
        print(f"  - Landmark Roles: {accessibility['landmark_roles']}")
        print(f"  - Heading Structure: {accessibility['heading_structure'][:10]}...")
        
        # Links and media
        links_media = findings['links_and_media']
        print(f"\n🔗 Links and Media:")
        print(f"  - Total Links: {links_media['total_links']}")
        print(f"  - Internal Links: {links_media['internal_links']}")
        print(f"  - External Links: {links_media['external_links']}")
        print(f"  - Email Links: {links_media['email_links']}")
        print(f"  - Images: {links_media['images']}")
        print(f"  - Videos: {links_media['videos']}")
        print(f"  - Audio: {links_media['audio']}")
        
        # Forms
        forms = findings['forms']
        print(f"\n📝 Forms:")
        print(f"  - Form Count: {forms['form_count']}")
        print(f"  - Total Inputs: {forms['total_inputs']}")
        print(f"  - Input Types: {forms['input_types']}")
        print(f"  - Select Elements: {forms['select_elements']}")
        print(f"  - Textarea Elements: {forms['textarea_elements']}")
        print(f"  - Button Elements: {forms['button_elements']}")
        print(f"  - Form Methods: {forms['form_methods']}")
        
        # Styling and scripts
        styling = findings['styling_and_scripts']
        print(f"\n🎨 Styling and Scripts:")
        print(f"  - Inline Styles: {styling['inline_styles']}")
        print(f"  - External Stylesheets: {styling['external_stylesheets']}")
        print(f"  - Inline Scripts: {styling['inline_scripts']}")
        print(f"  - External Scripts: {styling['external_scripts']}")
        print(f"  - Style Attributes: {styling['style_attributes']}")
        
        # Standards compliance
        compliance = findings['standards_compliance']
        print(f"\n✅ Standards Compliance:")
        print(f"  - Has DOCTYPE: {compliance['has_doctype']}")
        print(f"  - Has XMLNS: {compliance['has_xmlns']}")
        print(f"  - Has Lang: {compliance['has_lang']}")
        print(f"  - Well Formed: {compliance['well_formed']}")
        print(f"  - Semantic Structure: {compliance['semantic_structure']}")
        
        # Quality metrics
        quality = analysis.quality_metrics
        print(f"\n📈 Quality Metrics:")
        for metric, value in quality.items():
            print(f"  - {metric.replace('_', ' ').title()}: {value:.2f}")
        
        # AI use cases (first 5)
        print(f"\n🤖 AI Use Cases ({len(analysis.ai_use_cases)}):")
        for i, use_case in enumerate(analysis.ai_use_cases[:5], 1):
            print(f"  {i}. {use_case}")
        
        # Key structured data preview
        key_data = analysis.structured_data
        print(f"\n🔍 Key Structured Data:")
        print(f"  - Page Metadata Keys: {list(key_data['page_metadata'].keys())}")
        print(f"  - Content Hierarchy Items: {len(key_data['content_hierarchy'])}")
        print(f"  - Navigation Structures: {len(key_data['navigation_structure'])}")
        print(f"  - Form Data Items: {len(key_data['form_data'])}")
        print(f"  - Media Inventory Types: {list(key_data['media_inventory'].keys())}")
        
        print(f"\n✅ Comprehensive analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()