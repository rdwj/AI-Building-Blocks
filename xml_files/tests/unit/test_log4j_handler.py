#!/usr/bin/env python3
"""
Test script for Log4j Configuration Handler
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handlers.log4j_config_handler import Log4jConfigHandler
import xml.etree.ElementTree as ET

def test_log4j_handler():
    """Test Log4j handler with synthetic test files"""
    handler = Log4jConfigHandler()
    
    # Test files
    test_files = [
        '../../sample_data/test_files_synthetic/small/log4j/log4j2.xml',
        '../../sample_data/test_files_synthetic/small/log4j/log4j.xml',
        '../../sample_data/test_files_synthetic/small/log4j/log4j2-vulnerable.xml'
    ]
    
    print("🧪 Testing Log4j Configuration Handler")
    print("=" * 55)
    
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
                print(f"   Framework: {doc_type.metadata.get('framework')}")
                print(f"   Appenders: {doc_type.metadata.get('appender_count')}")
                print(f"   Loggers: {doc_type.metadata.get('logger_count')}")
                print(f"   Security issues: {doc_type.metadata.get('has_security_issues')}")
                
                # Test analysis
                analysis = handler.analyze(root, file_path)
                print(f"   Analysis complete - {len(analysis.key_findings)} findings")
                
                # Show key findings
                log4j_info = analysis.key_findings.get('log4j_info', {})
                print(f"   Log4j version: {log4j_info.get('version')}")
                
                appender_info = analysis.key_findings.get('appenders', {})
                print(f"   Appenders: {appender_info.get('appender_count')} total")
                if appender_info.get('appender_types'):
                    print(f"   Appender types: {', '.join(appender_info['appender_types'].keys())}")
                
                logger_info = analysis.key_findings.get('loggers', {})
                print(f"   Loggers: {logger_info.get('logger_count')} total")
                if logger_info.get('level_distribution'):
                    levels = ', '.join(f"{k}:{v}" for k,v in logger_info['level_distribution'].items())
                    print(f"   Log levels: {levels}")
                
                # Security analysis
                security_info = analysis.key_findings.get('security_concerns', {})
                if security_info.get('security_risks'):
                    print(f"   🚨 Security risks: {len(security_info['security_risks'])}")
                    for risk in security_info['security_risks'][:2]:  # Show first 2
                        print(f"      - {risk}")
                
                if security_info.get('log4shell_vulnerable'):
                    print(f"   ⚠️  Log4Shell VULNERABILITY detected!")
                
                # Performance analysis
                performance_info = analysis.key_findings.get('performance', {})
                if performance_info.get('performance_risks'):
                    print(f"   ⚡ Performance risks: {len(performance_info['performance_risks'])}")
                
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
    print(f"\n{'='*55}")
    print("📊 Log4j Handler Test Results:")
    success_count = sum(1 for _, success, _ in results if success)
    print(f"Success rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    
    for file_path, success, type_name in results:
        status = "✅" if success else "❌"
        print(f"{status} {os.path.basename(file_path)}: {type_name}")
    
    return success_count == len(results)

if __name__ == "__main__":
    success = test_log4j_handler()
    sys.exit(0 if success else 1)