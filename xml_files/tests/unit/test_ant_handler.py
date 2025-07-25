#!/usr/bin/env python3
"""
Test Ant Build Handler

Test the new Ant Build Handler implementation.
"""

import sys
from pathlib import Path
import json

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_ant_handler():
    """Test the Ant Build Handler"""
    print("🧪 Testing Ant Build Handler")
    print("=" * 50)
    
    # Test files available
    test_files = [
        "../../sample_data/test_files_synthetic/small/ant/build.xml",
        "../../sample_data/test_files/small/ant/apache-ant-build.xml",
        "../../sample_data/test_files/small/ant/ant-ivy-build.xml",
        "../../sample_data/test_files/small/ant/maven-resolver-ant-build.xml"
    ]
    
    try:
        # Import the handler
        from handlers.ant_build_handler import AntBuildHandler
        print("✅ AntBuildHandler imported successfully")
        
        # Create handler instance
        handler = AntBuildHandler()
        print("✅ Handler instantiated successfully")
        
        # Test each file
        results = []
        for test_file in test_files:
            file_path = Path(test_file)
            if not file_path.exists():
                print(f"⏭️  Skipping {file_path.name} - file not found")
                continue
            
            print(f"\n🧪 Testing: {file_path.name}")
            
            try:
                # Parse XML
                import xml.etree.ElementTree as ET
                tree = ET.parse(file_path)
                root = tree.getroot()
                
                # Extract namespaces
                namespaces = {}
                try:
                    for event, elem in ET.iterparse(str(file_path), events=['start-ns']):
                        namespaces[event[0] if event[0] else 'default'] = event[1]
                except:
                    pass  # Some files might not have proper namespace parsing
                
                # Test detection
                can_handle, confidence = handler.can_handle(root, namespaces)
                print(f"  🎯 Detection: can_handle={can_handle}, confidence={confidence:.2f}")
                
                if can_handle:
                    # Test type detection
                    doc_type = handler.detect_type(root, namespaces)
                    print(f"  📄 Document Type: {doc_type.type_name}")
                    print(f"  📊 Metadata: {doc_type.metadata}")
                    
                    # Test analysis
                    analysis = handler.analyze(root, str(file_path))
                    print(f"  🔍 Analysis completed")
                    print(f"    - Targets: {len(analysis.key_findings['targets'])}")
                    print(f"    - Properties: {len(analysis.key_findings['properties']['inline_properties'])}")
                    print(f"    - Dependencies: {analysis.key_findings['dependencies']['total_count']}")
                    print(f"    - Tasks: {analysis.key_findings['tasks']['total_count']}")
                    print(f"    - Quality Score: {analysis.quality_metrics['overall']:.2f}")
                    
                    results.append({
                        'file': file_path.name,
                        'success': True,
                        'confidence': confidence,
                        'type': doc_type.type_name,
                        'targets': len(analysis.key_findings['targets']),
                        'quality': analysis.quality_metrics['overall']
                    })
                else:
                    print(f"  ❌ Handler cannot process this file")
                    results.append({
                        'file': file_path.name,
                        'success': False,
                        'confidence': confidence,
                        'error': 'Handler rejected file'
                    })
                    
            except Exception as e:
                print(f"  ❌ Error processing file: {e}")
                results.append({
                    'file': file_path.name,
                    'success': False,
                    'error': str(e)
                })
        
        # Summary
        print("\n" + "=" * 50)
        print("📋 TEST SUMMARY")
        print("=" * 50)
        
        successful = [r for r in results if r.get('success', False)]
        print(f"✅ Successful: {len(successful)}/{len(results)}")
        
        if successful:
            avg_confidence = sum(r['confidence'] for r in successful) / len(successful)
            avg_quality = sum(r['quality'] for r in successful) / len(successful)
            print(f"📊 Average Confidence: {avg_confidence:.2f}")
            print(f"📊 Average Quality Score: {avg_quality:.2f}")
            
            print(f"\n📂 Processed Files:")
            for result in successful:
                print(f"  ✅ {result['file']} - {result['targets']} targets, quality: {result['quality']:.2f}")
        
        failed = [r for r in results if not r.get('success', False)]
        if failed:
            print(f"\n❌ Failed Files:")
            for result in failed:
                print(f"  ❌ {result['file']} - {result.get('error', 'Unknown error')}")
        
        # Save detailed results
        with open('ant_handler_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Detailed results saved to: ant_handler_test_results.json")
        
        # Determine success
        success_rate = len(successful) / len(results) if results else 0
        if success_rate >= 0.8:  # 80% success threshold
            print(f"\n🎉 Ant Handler Test PASSED! ({success_rate:.1%} success rate)")
            return True
        else:
            print(f"\n❌ Ant Handler Test FAILED! ({success_rate:.1%} success rate)")
            return False
            
    except Exception as e:
        print(f"❌ Critical error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    success = test_ant_handler()
    
    if success:
        print("\n🚀 Ready to add Ant Handler to registry!")
    else:
        print("\n🛑 Fix issues before proceeding")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)