#!/usr/bin/env python3
"""
Test script for Ivy Handler
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handlers.ivy_handler import IvyHandler
import xml.etree.ElementTree as ET

def test_ivy_handler():
    """Test Ivy handler with synthetic test files"""
    handler = IvyHandler()
    
    # Test files
    test_files = [
        '../../sample_data/test_files_synthetic/small/ivy/ivy.xml',
        '../../sample_data/test_files_synthetic/small/ivy/ivysettings.xml', 
        '../../sample_data/test_files_synthetic/small/ivy/library-ivy.xml'
    ]
    
    print("🧪 Testing Ivy Handler")
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
                print(f"   File type: {doc_type.metadata.get('file_type')}")
                print(f"   Module: {doc_type.metadata.get('module_organization')}/{doc_type.metadata.get('module_name')}")
                print(f"   Dependencies: {doc_type.metadata.get('dependency_count')}")
                print(f"   Publications: {doc_type.metadata.get('publication_count')}")
                
                # Test analysis
                analysis = handler.analyze(root, file_path)
                print(f"   Analysis complete - {len(analysis.key_findings)} findings")
                
                # Show key findings based on file type
                ivy_info = analysis.key_findings.get('ivy_info', {})
                print(f"   Ivy version: {ivy_info.get('version')}")
                print(f"   File type: {ivy_info.get('file_type')}")
                
                # Module-specific info
                if 'module_info' in analysis.key_findings:
                    module_info = analysis.key_findings['module_info']
                    if module_info.get('organisation'):
                        print(f"   Organization: {module_info['organisation']}")
                    if module_info.get('status'):
                        print(f"   Status: {module_info['status']}")
                
                if 'dependencies' in analysis.key_findings:
                    dep_info = analysis.key_findings['dependencies']
                    print(f"   Dependencies: {dep_info['dependency_count']}")
                    if dep_info['organizations']:
                        print(f"   Organizations: {', '.join(dep_info['organizations'][:3])}")
                
                if 'publications' in analysis.key_findings:
                    pub_info = analysis.key_findings['publications']
                    print(f"   Publications: {pub_info['publication_count']}")
                    if pub_info['artifact_types']:
                        print(f"   Artifact types: {', '.join(pub_info['artifact_types'].keys())}")
                
                if 'configurations' in analysis.key_findings:
                    config_info = analysis.key_findings['configurations']
                    print(f"   Configurations: {config_info['configuration_count']}")
                
                # Settings-specific info
                if 'resolvers' in analysis.key_findings:
                    resolver_info = analysis.key_findings['resolvers']
                    print(f"   Resolvers: {resolver_info['resolver_count']}")
                    if resolver_info['resolver_types']:
                        print(f"   Resolver types: {', '.join(resolver_info['resolver_types'].keys())}")
                
                # Security info
                if 'security' in analysis.key_findings:
                    security_info = analysis.key_findings['security']
                    if security_info.get('security_risks'):
                        print(f"   ⚠️  Security risks: {len(security_info['security_risks'])}")
                        for risk in security_info['security_risks'][:2]:  # Show first 2
                            print(f"      - {risk}")
                
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
    print("📊 Ivy Handler Test Results:")
    success_count = sum(1 for _, success, _ in results if success)
    print(f"Success rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    
    for file_path, success, type_name in results:
        status = "✅" if success else "❌"
        print(f"{status} {os.path.basename(file_path)}: {type_name}")
    
    return success_count == len(results)

if __name__ == "__main__":
    success = test_ivy_handler()
    sys.exit(0 if success else 1)