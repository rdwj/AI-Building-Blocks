#!/usr/bin/env python3
"""
Comprehensive test runner for all XML handler tests

Runs tests from the organized test directory structure:
- tests/unit/: Individual handler unit tests
- tests/integration/: Handler integration tests
- tests/comprehensive/: Full system tests
- tests/: Framework tests
"""

import sys
import os
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Tuple

def run_python_script(script_path: Path) -> Tuple[bool, str, float]:
    """Run a Python script and return success status, output, and execution time"""
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=60,  # 60 second timeout
            cwd=script_path.parent
        )
        
        execution_time = time.time() - start_time
        success = result.returncode == 0
        output = result.stdout + result.stderr
        
        return success, output, execution_time
        
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        return False, "Test timed out after 60 seconds", execution_time
    except Exception as e:
        execution_time = time.time() - start_time
        return False, f"Error running test: {e}", execution_time

def find_test_files(test_dir: Path) -> List[Path]:
    """Find all test_*.py files in a directory"""
    if not test_dir.exists():
        return []
    return sorted(test_dir.glob("test_*.py"))

def run_test_category(category_name: str, test_files: List[Path]) -> Dict:
    """Run all tests in a category and return results"""
    print(f"\n🧪 Running {category_name} Tests")
    print("=" * 60)
    
    results = {
        'category': category_name,
        'total': len(test_files),
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'total_time': 0.0,
        'test_results': []
    }
    
    if not test_files:
        print(f"  ⏭️  No test files found in {category_name}")
        return results
    
    for test_file in test_files:
        print(f"\n🔍 Running {test_file.name}")
        
        success, output, exec_time = run_python_script(test_file)
        results['total_time'] += exec_time
        
        test_result = {
            'name': test_file.name,
            'success': success,
            'execution_time': exec_time,
            'output': output
        }
        results['test_results'].append(test_result)
        
        if success:
            print(f"  ✅ PASSED ({exec_time:.2f}s)")
            results['passed'] += 1
        else:
            print(f"  ❌ FAILED ({exec_time:.2f}s)")
            results['failed'] += 1
            # Print first few lines of error for debugging
            error_lines = output.split('\n')[:5]
            for line in error_lines:
                if line.strip():
                    print(f"     {line}")
    
    # Category summary
    success_rate = (results['passed'] / results['total']) * 100 if results['total'] > 0 else 0
    print(f"\n📊 {category_name} Summary: {results['passed']}/{results['total']} tests passed ({success_rate:.1f}%)")
    print(f"   ⏱️  Total time: {results['total_time']:.2f}s")
    
    return results

def main():
    """Run all tests in organized structure"""
    print("🧪 XML HANDLERS COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print("Testing all handlers from organized test directory structure")
    
    # Change to the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    # Test categories
    test_categories = [
        ("Unit Tests", find_test_files(script_dir / "unit")),
        ("Integration Tests", find_test_files(script_dir / "integration")),
        ("Framework Tests", find_test_files(script_dir)),
        ("Comprehensive Tests", find_test_files(script_dir / "comprehensive"))
    ]
    
    # Run all test categories
    all_results = []
    total_start_time = time.time()
    
    for category_name, test_files in test_categories:
        if test_files or category_name == "Framework Tests":  # Always run framework tests
            category_results = run_test_category(category_name, test_files)
            all_results.append(category_results)
    
    total_execution_time = time.time() - total_start_time
    
    # Overall summary
    print("\n" + "=" * 80)
    print("📊 OVERALL TEST RESULTS SUMMARY")
    print("=" * 80)
    
    grand_total = sum(r['total'] for r in all_results)
    grand_passed = sum(r['passed'] for r in all_results)
    grand_failed = sum(r['failed'] for r in all_results)
    overall_success_rate = (grand_passed / grand_total) * 100 if grand_total > 0 else 0
    
    print(f"Total Tests Run: {grand_total}")
    print(f"Passed: {grand_passed}")
    print(f"Failed: {grand_failed}")
    print(f"Overall Success Rate: {overall_success_rate:.1f}%")
    print(f"Total Execution Time: {total_execution_time:.2f}s")
    
    # Category breakdown
    print(f"\n📋 Results by Category:")
    for result in all_results:
        category_rate = (result['passed'] / result['total']) * 100 if result['total'] > 0 else 0
        print(f"  {result['category']:20} {result['passed']:3}/{result['total']:3} ({category_rate:5.1f}%) - {result['total_time']:5.2f}s")
    
    # Failed tests detail
    failed_tests = []
    for result in all_results:
        for test_result in result['test_results']:
            if not test_result['success']:
                failed_tests.append((result['category'], test_result['name'], test_result['output']))
    
    if failed_tests:
        print(f"\n❌ Failed Tests Details:")
        for category, test_name, output in failed_tests:
            print(f"  {category}/{test_name}")
            # Show first error line
            error_lines = [line for line in output.split('\n') if line.strip() and ('❌' in line or 'Error' in line)]
            if error_lines:
                print(f"    → {error_lines[0]}")
    
    # Performance analysis
    print(f"\n⚡ Performance Summary:")
    avg_time = total_execution_time / grand_total if grand_total > 0 else 0
    print(f"  Average test time: {avg_time:.3f}s")
    
    # Find slowest tests
    all_test_times = []
    for result in all_results:
        for test_result in result['test_results']:
            all_test_times.append((test_result['execution_time'], f"{result['category']}/{test_result['name']}"))
    
    if all_test_times:
        slowest_tests = sorted(all_test_times, reverse=True)[:5]
        print(f"  Slowest tests:")
        for exec_time, test_name in slowest_tests:
            print(f"    {test_name}: {exec_time:.3f}s")
    
    print("\n" + "=" * 80)
    
    # Exit with appropriate code
    if overall_success_rate >= 80:
        print("🎉 TEST SUITE PASSED! Excellent success rate.")
        sys.exit(0)
    elif overall_success_rate >= 60:
        print("⚠️  TEST SUITE PARTIAL SUCCESS. Some tests need attention.")
        sys.exit(1)
    else:
        print("❌ TEST SUITE FAILED. Many tests need fixing.")
        sys.exit(1)

if __name__ == "__main__":
    main()