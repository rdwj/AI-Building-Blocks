#!/usr/bin/env python3
"""
Test the improved LLM interface for proper Ansible YAML generation
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_yaml_structure_validation():
    """Test the YAML validation logic"""
    
    try:
        from llm_interface import LLMInterface
        
        llm = LLMInterface()
        
        # Test cases: valid and invalid YAML structures
        test_cases = [
            ("Valid single task", """- name: "Test task"
  package:
    name: test
    state: absent
  become: true
  tags:
    - stig""", True),
            
            ("Invalid - multiple tasks", """- name: "Task 1"
  package:
    name: test1
    state: absent
- name: "Task 2"
  package:
    name: test2
    state: absent""", False),
            
            ("Invalid - no module", """- name: "Test task"
  become: true
  tags:
    - stig""", False),
            
            ("Invalid - malformed structure", """- name: "Test task"
  become: true
  package:
    name: test
    state: absent
  file:
    path: /test
    state: present""", False),
            
            ("Valid with when clause", """- name: "STIG TEST: Remove package"
  package:
    name: prelink
    state: absent
  become: true
  when: ansible_os_family == "RedHat"
  tags:
    - stig
    - security
    - medium""", True)
        ]
        
        print("🧪 Testing YAML validation logic...")
        
        passed = 0
        for test_name, yaml_content, should_be_valid in test_cases:
            result = llm.validate_ansible_structure(yaml_content)
            
            if result['valid'] == should_be_valid:
                print(f"   ✅ {test_name}")
                passed += 1
            else:
                print(f"   ❌ {test_name}: Expected {should_be_valid}, got {result['valid']}")
                if not result['valid']:
                    print(f"      Error: {result['error']}")
        
        print(f"\n📊 Validation tests: {passed}/{len(test_cases)} passed")
        return passed == len(test_cases)
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False

def test_content_extraction():
    """Test extraction of clean YAML from various LLM response formats"""
    
    try:
        from llm_interface import LLMInterface
        
        llm = LLMInterface()
        
        # Test problematic responses similar to what the user saw
        test_responses = [
            ("Clean response", """- name: "STIG TEST: Remove package"
  package:
    name: prelink
    state: absent
  become: true
  tags:
    - stig"""),
            
            ("With markdown", """Here's the task:

```yaml
- name: "STIG TEST: Remove package"
  package:
    name: prelink
    state: absent
  become: true
  tags:
    - stig
```

This task removes the package."""),
            
            ("With extra headers", """---
- name: "STIG TEST: Remove package"
  package:
    name: prelink
    state: absent
  become: true
  tags:
    - stig
---
Please note this task..."""),
            
            ("With explanatory text", """- name: "STIG TEST: Remove package"
  package:
    name: prelink
    state: absent
  become: true
  tags:
    - stig

Please note that this task requires additional configuration.""")
        ]
        
        print("🧪 Testing content extraction...")
        
        passed = 0
        for test_name, response in test_responses:
            cleaned = llm.extract_and_fix_yaml(response)
            validation = llm.validate_ansible_structure(cleaned)
            
            if validation['valid']:
                print(f"   ✅ {test_name}")
                passed += 1
            else:
                print(f"   ❌ {test_name}: {validation['error']}")
                print(f"      Cleaned content: {cleaned[:100]}...")
        
        print(f"\n📊 Extraction tests: {passed}/{len(test_responses)} passed")
        return passed == len(test_responses)
        
    except Exception as e:
        print(f"❌ Extraction test failed: {e}")
        return False

def test_actual_generation():
    """Test actual generation with the problematic finding"""
    
    if not Path('.env').exists():
        print("⚠️  No .env file - skipping actual generation test")
        return True
    
    try:
        from llm_interface import LLMInterface
        
        # Use the exact finding that was problematic for the user
        problematic_finding = {
            'rule_id': 'xccdf_org.ssgproject.content_rule_package_prelink_removed',
            'severity': 'medium',
            'title': 'Rule xccdf_org.ssgproject.content_rule_package_prelink_removed',
            'description': 'The prelink package should be removed from the system',
            'fix_text': 'Remove the prelink package using: yum remove prelink'
        }
        
        print("🧪 Testing actual generation with problematic finding...")
        
        llm = LLMInterface()
        result = llm.generate_ansible_task(problematic_finding)
        
        if result['success']:
            print(f"✅ Generation successful")
            print(f"   YAML Valid: {result.get('yaml_valid', 'Unknown')}")
            print(f"   Attempts: {result.get('attempt', 1)}")
            
            if result.get('yaml_valid'):
                print(f"   Module: {result.get('module_used', 'Unknown')}")
                print(f"   Task: {result.get('task_name', 'Unknown')[:50]}...")
                
                # Show the generated content
                content = result['content']
                print(f"\n📋 Generated Content:")
                print(content)
                
                # Check for issues that were in the original
                issues = []
                if content.count('- name:') > 1:
                    issues.append("Multiple tasks")
                if '```' in content:
                    issues.append("Contains markdown")
                if content.count('prelink') > 5:
                    issues.append("Repetitive content")
                
                if issues:
                    print(f"⚠️  Potential issues: {', '.join(issues)}")
                    return False
                else:
                    print("✅ Clean, single task generated")
                    return True
            else:
                print(f"❌ Invalid YAML: {result.get('validation_error', 'Unknown')}")
                return False
        else:
            print(f"❌ Generation failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Generation test failed: {e}")
        return False

def main():
    """Run all tests for the improved LLM interface"""
    
    print("🔧 Testing Improved LLM Interface")
    print("=" * 50)
    
    tests = [
        ("YAML Validation Logic", test_yaml_structure_validation),
        ("Content Extraction", test_content_extraction),
        ("Actual Generation", test_actual_generation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n📊 Test Results")
    print("=" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed!")
        print("The improved LLM interface should generate proper Ansible YAML.")
        print("\nNext steps:")
        print("1. Run: python regenerate_yaml.py")
        print("2. This will fix your existing problematic files")
    else:
        print("\n⚠️  Some tests failed.")
        print("The LLM interface may still have issues.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
