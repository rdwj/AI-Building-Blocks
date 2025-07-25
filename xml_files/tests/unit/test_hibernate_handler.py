#!/usr/bin/env python3
"""
Test script for Hibernate Handler
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handlers.hibernate_handler import HibernateHandler
import xml.etree.ElementTree as ET

def test_hibernate_handler():
    """Test Hibernate handler with synthetic test files"""
    handler = HibernateHandler()
    
    # Test files
    test_files = [
        '../../sample_data/test_files_synthetic/small/hibernate/hibernate.cfg.xml',
        '../../sample_data/test_files_synthetic/small/hibernate/User.hbm.xml',
        '../../sample_data/test_files_synthetic/small/hibernate/Order.hbm.xml',
        '../../sample_data/test_files_synthetic/small/hibernate/Product.hbm.xml'
    ]
    
    print("🧪 Testing Hibernate Handler")
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
                print(f"   Database driver: {doc_type.metadata.get('database_driver')}")
                print(f"   Entity count: {doc_type.metadata.get('entity_count')}")
                
                # Test analysis
                analysis = handler.analyze(root, file_path)
                print(f"   Analysis complete - {len(analysis.key_findings)} findings")
                
                # Show key findings based on file type
                hibernate_info = analysis.key_findings.get('hibernate_info', {})
                print(f"   Hibernate version: {hibernate_info.get('version')}")
                print(f"   File type: {hibernate_info.get('file_type')}")
                
                # Configuration-specific info
                if 'session_factory' in analysis.key_findings:
                    sf_info = analysis.key_findings['session_factory']
                    print(f"   Session factory: {sf_info['present']} (props: {sf_info['property_count']})")
                
                if 'database_info' in analysis.key_findings:
                    db_info = analysis.key_findings['database_info']
                    if db_info.get('driver'):
                        print(f"   Database: {db_info.get('driver', 'Unknown')}")
                
                # Mapping-specific info
                if 'entities' in analysis.key_findings:
                    entity_info = analysis.key_findings['entities']
                    print(f"   Entities: {entity_info['entity_count']}")
                    if entity_info['table_names']:
                        print(f"   Tables: {', '.join(entity_info['table_names'][:3])}")
                
                if 'relationships' in analysis.key_findings:
                    rel_info = analysis.key_findings['relationships']
                    print(f"   Relationships: {rel_info['relationship_count']}")
                
                # Security info
                if 'security' in analysis.key_findings:
                    security_info = analysis.key_findings['security']
                    if security_info.get('security_risks'):
                        print(f"   ⚠️  Security risks: {len(security_info['security_risks'])}")
                
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
    print("📊 Hibernate Handler Test Results:")
    success_count = sum(1 for _, success, _ in results if success)
    print(f"Success rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    
    for file_path, success, type_name in results:
        status = "✅" if success else "❌"
        print(f"{status} {os.path.basename(file_path)}: {type_name}")
    
    return success_count == len(results)

if __name__ == "__main__":
    success = test_hibernate_handler()
    sys.exit(0 if success else 1)