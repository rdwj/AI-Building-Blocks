#!/usr/bin/env python3
"""
Test script for SOAP Envelope Handler
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handlers.soap_envelope_handler import SOAPEnvelopeHandler
import xml.etree.ElementTree as ET

def test_soap_handler():
    """Test SOAP handler with synthetic test files"""
    handler = SOAPEnvelopeHandler()
    
    # Test files
    test_files = [
        '../../sample_data/test_files_synthetic/small/soap/soap_request.xml',
        '../../sample_data/test_files_synthetic/small/soap/soap_response.xml', 
        '../../sample_data/test_files_synthetic/small/soap/soap_fault.xml',
        '../../sample_data/test_files_synthetic/small/soap/soap12_envelope.xml'
    ]
    
    print("🧪 Testing SOAP Envelope Handler")
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
                print(f"   Has security: {doc_type.metadata.get('has_security')}")
                print(f"   Has addressing: {doc_type.metadata.get('has_addressing')}")
                
                # Test analysis
                analysis = handler.analyze(root, file_path)
                print(f"   Analysis complete - {len(analysis.key_findings)} findings")
                
                # Show key findings
                envelope_info = analysis.key_findings['envelope_info']
                print(f"   SOAP version: {envelope_info['version']}")
                print(f"   Message type: {envelope_info['message_type']}")
                
                security_info = analysis.key_findings['security']
                if security_info['has_security']:
                    print(f"   Security tokens: {len(security_info['security_tokens'])}")
                    if security_info['security_risks']:
                        print(f"   ⚠️  Security risks: {security_info['security_risks']}")
                
                addressing_info = analysis.key_findings['addressing']
                if addressing_info['has_addressing']:
                    print(f"   WS-Addressing: {addressing_info.get('action', 'N/A')}")
                
                fault_info = analysis.key_findings['faults']
                if fault_info['is_fault']:
                    fault_summary = fault_info['fault_summary']
                    print(f"   Fault: {fault_summary.get('code')} - {fault_summary.get('string')}")
                
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
    print("📊 SOAP Handler Test Results:")
    success_count = sum(1 for _, success, _ in results if success)
    print(f"Success rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    
    for file_path, success, type_name in results:
        status = "✅" if success else "❌"
        print(f"{status} {os.path.basename(file_path)}: {type_name}")
    
    return success_count == len(results)

if __name__ == "__main__":
    success = test_soap_handler()
    sys.exit(0 if success else 1)