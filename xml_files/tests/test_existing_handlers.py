#!/usr/bin/env python3
"""
Test Existing XML Handlers

This script tests all existing XML handlers with the available sample data
to ensure they work correctly before we begin migration.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import traceback

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from core.analyzer import XMLDocumentAnalyzer
    from xml_schema_analyzer_fixed import XMLSchemaAnalyzer
except ImportError as e:
    print(f"❌ Failed to import required modules: {e}")
    sys.exit(1)

class HandlerTester:
    """Test framework for XML handlers"""
    
    def __init__(self):
        self.analyzer = XMLDocumentAnalyzer()
        self.schema_analyzer = XMLSchemaAnalyzer()
        self.test_results = {
            'total_files': 0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'handler_coverage': {},
            'detailed_results': []
        }
    
    def run_comprehensive_tests(self):
        """Run tests on all available sample files"""
        print("🧪 Starting Comprehensive Handler Testing")
        print("=" * 60)
        
        # Test files that should match existing handlers
        test_cases = [
            # SCAP Handler tests
            ("SCAP Handler", [
                "../sample_data/stigs_old/node2.example.com-STIG-20250710162433.xml",
                "../sample_data/test_files/small/scap/ios-sample-1.0.xccdf.xml",
                "../sample_data/test_files/small/scap/ios-sample-1.1.xccdf.xml",
                "../sample_data/test_files_synthetic/small/scap/security-assessment-report.xml"
            ]),
            
            # RSS Handler tests
            ("RSS Handler", [
                "../sample_data/test_files_synthetic/small/rss/sample-feed.xml"
            ]),
            
            # Maven POM Handler tests
            ("Maven POM Handler", [
                "../sample_data/test_files_synthetic/small/pom/spring-boot-example-pom.xml"
            ]),
            
            # Spring Config Handler tests
            ("Spring Config Handler", [
                "../sample_data/test_files_synthetic/small/spring/applicationContext-example.xml"
            ]),
            
            # Log4j Config Handler tests
            ("Log4j Config Handler", [
                "../sample_data/test_files_synthetic/small/log4j/log4j2-example.xml"
            ]),
            
            # SVG Handler tests
            ("SVG Handler", [
                "../sample_data/test_files_synthetic/small/svg/sample-icon.svg"
            ]),
            
            # DocBook Handler tests
            ("DocBook Handler", [
                "../sample_data/test_files_synthetic/small/docbook/sample-docbook-guide.xml"
            ]),
            
            # Sitemap Handler tests
            ("Sitemap Handler", [
                "../sample_data/test_files_synthetic/small/sitemap/sitemap-example.xml"
            ]),
            
            # WSDL Handler tests (from src/handlers)
            ("WSDL Handler", [
                "../sample_data/test_files/small/wsdl/calculator-soap.wsdl",
                "../sample_data/test_files/small/wsdl/bet365-contacts-soap.wsdl",
                "../sample_data/test_files_synthetic/small/wsdl/hotel-reservation-service.wsdl"
            ]),
            
            # XSD Handler tests (from src/handlers)
            ("XSD Handler", [
                "../sample_data/test_files/small/scap/xccdf_1.2_bundle_2_xml.xsd",
                "../sample_data/test_files_synthetic/small/xsd/library-schema.xsd"
            ])
        ]
        
        # Run tests for each handler
        for handler_name, file_paths in test_cases:
            print(f"\n🔍 Testing {handler_name}")
            print("-" * 40)
            
            handler_results = {
                'handler': handler_name,
                'files_tested': 0,
                'files_passed': 0,
                'files_failed': 0,
                'details': []
            }
            
            for file_path in file_paths:
                result = self.test_single_file(file_path, handler_name)
                handler_results['files_tested'] += 1
                handler_results['details'].append(result)
                
                if result['success']:
                    handler_results['files_passed'] += 1
                    print(f"  ✅ {Path(file_path).name} - {result['detected_type']}")
                else:
                    handler_results['files_failed'] += 1
                    print(f"  ❌ {Path(file_path).name} - {result['error']}")
            
            self.test_results['handler_coverage'][handler_name] = handler_results
            
            # Summary for this handler
            success_rate = (handler_results['files_passed'] / handler_results['files_tested']) * 100 if handler_results['files_tested'] > 0 else 0
            print(f"  📊 Success Rate: {success_rate:.1f}% ({handler_results['files_passed']}/{handler_results['files_tested']})")
        
        # Test some additional files to see generic handler behavior
        print(f"\n🔍 Testing Additional Files (Generic Behavior)")
        print("-" * 40)
        additional_files = [
            "../sample_data/test_files/small/ant/build.xml",  # Should be generic (no ant handler yet)
            "../sample_data/test_files/small/kml/mapbox-example.kml",  # Should be generic
            "../sample_data/test_files/small/nuget/example-nuspec.xml"  # Should be generic
        ]
        
        for file_path in additional_files:
            result = self.test_single_file(file_path, "Generic")
            if result['success']:
                print(f"  ✅ {Path(file_path).name} - {result['detected_type']}")
            else:
                print(f"  ❌ {Path(file_path).name} - {result['error']}")
        
        self.print_final_summary()
        return self.test_results
    
    def test_single_file(self, file_path: str, expected_handler: str = None) -> Dict[str, Any]:
        """Test analysis of a single XML file"""
        result = {
            'file_path': file_path,
            'expected_handler': expected_handler,
            'success': False,
            'detected_type': None,
            'handler_used': None,
            'analysis_time': 0.0,
            'error': None,
            'findings_count': 0
        }
        
        try:
            # Check if file exists
            if not Path(file_path).exists():
                result['error'] = "File not found"
                return result
            
            # Time the analysis
            import time
            start_time = time.time()
            
            # Run the analysis
            analysis_result = self.analyzer.analyze_document(file_path)
            
            end_time = time.time()
            result['analysis_time'] = end_time - start_time
            
            # Check if analysis was successful (no error key means success)
            if 'error' not in analysis_result:
                result['success'] = True
                doc_type = analysis_result.get('document_type')
                result['detected_type'] = doc_type.type_name if doc_type else 'Unknown'
                result['handler_used'] = analysis_result.get('handler_used', 'Unknown')
                
                # Count findings
                analysis = analysis_result.get('analysis')
                if analysis and hasattr(analysis, 'key_findings'):
                    findings = analysis.key_findings
                    result['findings_count'] = len(findings) if isinstance(findings, dict) else 0
                else:
                    result['findings_count'] = 0
                
            else:
                result['error'] = analysis_result.get('error', 'Unknown analysis error')
                
        except Exception as e:
            result['error'] = f"Exception: {str(e)}"
            traceback.print_exc()
        
        self.test_results['total_files'] += 1
        if result['success']:
            self.test_results['successful_analyses'] += 1
        else:
            self.test_results['failed_analyses'] += 1
        
        self.test_results['detailed_results'].append(result)
        return result
    
    def print_final_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📋 FINAL TEST SUMMARY")
        print("=" * 60)
        
        total = self.test_results['total_files']
        success = self.test_results['successful_analyses']
        failed = self.test_results['failed_analyses']
        
        success_rate = (success / total) * 100 if total > 0 else 0
        
        print(f"Total Files Tested: {total}")
        print(f"Successful Analyses: {success}")
        print(f"Failed Analyses: {failed}")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        print(f"\n📊 Handler Performance:")
        for handler_name, results in self.test_results['handler_coverage'].items():
            files_tested = results['files_tested']
            files_passed = results['files_passed']
            rate = (files_passed / files_tested) * 100 if files_tested > 0 else 0
            print(f"  {handler_name}: {rate:.1f}% ({files_passed}/{files_tested})")
        
        # Identify any critical failures
        critical_failures = []
        for handler_name, results in self.test_results['handler_coverage'].items():
            if results['files_failed'] > 0:
                critical_failures.append(f"{handler_name}: {results['files_failed']} failures")
        
        if critical_failures:
            print(f"\n⚠️  Critical Issues Found:")
            for failure in critical_failures:
                print(f"  - {failure}")
            print("\n❌ RECOMMENDATION: Fix these issues before proceeding with migration")
            return False
        else:
            print(f"\n✅ All handlers working correctly!")
            print("✅ RECOMMENDATION: Safe to proceed with migration")
            return True
    
    def save_results(self, output_file: str = "handler_test_results.json"):
        """Save detailed test results to JSON file"""
        with open(output_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n💾 Detailed results saved to: {output_file}")

def main():
    """Main test execution"""
    print("🚀 XML Handler Testing Suite")
    print("Testing existing handlers before migration...")
    print()
    
    tester = HandlerTester()
    results = tester.run_comprehensive_tests()
    
    # Save results
    tester.save_results()
    
    # Determine if migration should proceed
    overall_success_rate = (results['successful_analyses'] / results['total_files']) * 100 if results['total_files'] > 0 else 0
    
    if overall_success_rate >= 80:  # 80% threshold for proceeding
        print(f"\n🎉 Handler testing PASSED! (Success rate: {overall_success_rate:.1f}%)")
        print("✅ Safe to proceed with handler migration.")
        return True
    else:
        print(f"\n❌ Handler testing FAILED! (Success rate: {overall_success_rate:.1f}%)")
        print("🛑 Fix issues before proceeding with migration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)