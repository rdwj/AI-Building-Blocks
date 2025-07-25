#!/usr/bin/env python3
"""
Debug SOAP namespace detection
"""

import xml.etree.ElementTree as ET
import sys
import os

def debug_soap_file(file_path):
    print(f"\n🔍 Debugging: {file_path}")
    
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    print(f"Root tag: {root.tag}")
    print(f"Root attributes: {dict(root.attrib)}")
    
    # Extract namespaces manually
    namespaces = {}
    for key, value in root.attrib.items():
        if key.startswith('xmlns'):
            prefix = key.split(':', 1)[1] if ':' in key else 'default'
            namespaces[prefix] = value
            print(f"Namespace {prefix}: {value}")
    
    # Check root tag name
    root_tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag
    print(f"Local root tag: {root_tag}")
    
    # Check for SOAP namespaces
    SOAP_11_NS = "http://schemas.xmlsoap.org/soap/envelope/"
    SOAP_12_NS = "http://www.w3.org/2003/05/soap-envelope"
    
    has_soap_11 = any(SOAP_11_NS in uri for uri in namespaces.values())
    has_soap_12 = any(SOAP_12_NS in uri for uri in namespaces.values())
    
    print(f"Has SOAP 1.1: {has_soap_11}")
    print(f"Has SOAP 1.2: {has_soap_12}")
    
    # Check for Body element
    body_found = root.find('.//Body') is not None or any('Body' in elem.tag for elem in root)
    print(f"Body found: {body_found}")

if __name__ == "__main__":
    test_files = [
        'sample_data/test_files_synthetic/small/soap/soap_request.xml',
        'sample_data/test_files_synthetic/small/soap/soap_response.xml', 
        'sample_data/test_files_synthetic/small/soap/soap_fault.xml',
        'sample_data/test_files_synthetic/small/soap/soap12_envelope.xml'
    ]
    
    for file_path in test_files:
        debug_soap_file(file_path)