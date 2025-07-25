#!/usr/bin/env python3
"""
Test script for SAML Handler
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handlers.saml_handler import SAMLHandler
import xml.etree.ElementTree as ET

def test_saml_handler():
    """Test SAML handler with synthetic test files"""
    handler = SAMLHandler()
    
    # Test files
    test_files = [
        '../../sample_data/test_files_synthetic/small/saml/saml_assertion.xml',
        '../../sample_data/test_files_synthetic/small/saml/saml_response.xml',
        '../../sample_data/test_files_synthetic/small/saml/saml_authn_request.xml',
        '../../sample_data/test_files_synthetic/small/saml/saml_logout_request.xml'
    ]
    
    print("🧪 Testing SAML Handler")
    print("=" * 50)
    
    results = []
    
    for file_path in test_files:
        print(f"\n📄 Testing: {file_path}")
        
        try:
            # Parse XML
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract namespaces
            namespaces = {}
            for key, value in root.attrib.items():
                if key.startswith('xmlns'):
                    prefix = key.split(':', 1)[1] if ':' in key else 'default'
                    namespaces[prefix] = value
            
            # Test detection
            can_handle, confidence = handler.can_handle(root, namespaces)
            print(f"   Can handle: {can_handle} (confidence: {confidence:.2f})")
            
            if can_handle:
                # Test type detection
                doc_type = handler.detect_type(root, namespaces)
                print(f"   Type: {doc_type.type_name} (v{doc_type.version})")
                print(f"   Message type: {doc_type.metadata.get('message_type')}")
                print(f"   Issuer: {doc_type.metadata.get('issuer')}")
                print(f"   Has signature: {doc_type.metadata.get('has_signature')}")
                print(f"   Has encryption: {doc_type.metadata.get('has_encryption')}")
                
                # Test analysis
                analysis = handler.analyze(root, file_path)
                print(f"   Analysis complete - {len(analysis.key_findings)} findings")
                
                # Show key findings
                saml_info = analysis.key_findings['saml_info']
                print(f"   SAML version: {saml_info['version']}")
                print(f"   Message type: {saml_info['message_type']}")
                print(f"   ID: {saml_info['id']}")
                
                # Security info
                security_info = analysis.key_findings['security']
                if security_info['security_risks']:
                    print(f"   ⚠️  Security risks: {security_info['security_risks']}")
                
                # Subject info
                subject_info = analysis.key_findings['subject_info']
                if subject_info['has_subject']:
                    print(f"   Subject: {subject_info['name_id']} ({subject_info['name_id_format']})")
                
                # Assertion info  
                assertion_info = analysis.key_findings['assertions']
                if assertion_info['assertion_count'] > 0:
                    print(f"   Assertions: {assertion_info['assertion_count']} (encrypted: {assertion_info['encrypted_assertions']})")
                
                # Attribute info
                attr_info = analysis.key_findings['attributes']
                if attr_info['total_attributes'] > 0:
                    print(f"   Attributes: {attr_info['total_attributes']} total")
                
                # Quality metrics
                quality = analysis.quality_metrics
                print(f"   Quality - Overall: {quality['overall']:.2f}, Security: {quality['security']:.2f}")
                
                results.append((file_path, True, doc_type.type_name))
            else:
                results.append((file_path, False, "Not handled"))
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append((file_path, False, f"Error: {e}"))
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 SAML Handler Test Results:")
    success_count = sum(1 for _, success, _ in results if success)
    print(f"Success rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    
    for file_path, success, type_name in results:
        status = "✅" if success else "❌"
        print(f"{status} {os.path.basename(file_path)}: {type_name}")
    
    return success_count == len(results)

if __name__ == "__main__":
    success = test_saml_handler()
    sys.exit(0 if success else 1)