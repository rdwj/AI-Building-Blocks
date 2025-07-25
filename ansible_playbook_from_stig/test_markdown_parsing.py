#!/usr/bin/env python3
"""
Test the improved markdown parsing for LLM responses
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_markdown_parsing():
    """Test parsing of markdown-formatted LLM responses"""
    
    # Example of problematic LLM response with markdown
    problematic_response = """Here's the Ansible task to remediate this STIG finding:

```yaml
---
- name: "STIG OPT_PARTITION: Ensure /opt Located On Separate Partition"
  mount:
    path: /opt
    src: /dev/sdb1
    fstype: ext4
    opts: defaults
    state: mounted
  when: ansible_os_family == "RedHat"
  become: true
  tags:
    - stig
    - security
    - medium
```

Please note that this task assumes you have a separate partition available for /opt. You may need to create the partition first using tools like fdisk or parted. Also, adjust the device path (/dev/sdb1) according to your system configuration."""
    
    try:
        from llm_interface import LLMInterface
        
        llm = LLMInterface()
        
        # Test the extraction method
        cleaned_yaml = llm.extract_yaml_from_response(problematic_response)
        
        print("📋 Original response:")
        print(f"Length: {len(problematic_response)} chars")
        print(f"Preview: {problematic_response[:100]}...")
        
        print(f"\n🧹 Cleaned YAML:")
        print(f"Length: {len(cleaned_yaml)} chars")
        print(f"Content:\n{cleaned_yaml}")
        
        # Test YAML validation
        try:
            import yaml
            parsed = yaml.safe_load(cleaned_yaml)
            if parsed:
                print(f"\n✅ YAML validation successful!")
                print(f"Task name: {parsed[0]['name'] if isinstance(parsed, list) and 'name' in parsed[0] else 'Not found'}")
                return True
            else:
                print(f"\n❌ YAML validation failed - parsed as None")
                return False
        except Exception as e:
            print(f"\n❌ YAML validation error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_various_formats():
    """Test parsing of various LLM response formats"""
    
    test_cases = [
        ("Standard markdown", """```yaml
- name: "Test task"
  file:
    path: /test
    state: present
```"""),
        ("With yml directive", """```yml
- name: "Test task"
  file:
    path: /test
    state: present
```"""),
        ("With explanatory text", """Here is the Ansible task:

```yaml
- name: "Test task"
  file:
    path: /test
    state: present
```

This task creates a test file."""),
        ("No code blocks", """- name: "Test task"
  file:
    path: /test
    state: present"""),
        ("With YAML header", """---
- name: "Test task"
  file:
    path: /test
    state: present""")
    ]
    
    try:
        from llm_interface import LLMInterface
        llm = LLMInterface()
        
        success_count = 0
        
        for test_name, test_content in test_cases:
            print(f"\n🧪 Testing: {test_name}")
            print(f"Input: {test_content[:50]}...")
            
            cleaned = llm.extract_yaml_from_response(test_content)
            print(f"Output: {cleaned[:50]}...")
            
            try:
                import yaml
                parsed = yaml.safe_load(cleaned)
                if parsed:
                    print("✅ Valid YAML")
                    success_count += 1
                else:
                    print("❌ Invalid YAML")
            except Exception as e:
                print(f"❌ YAML error: {e}")
        
        print(f"\n📊 Results: {success_count}/{len(test_cases)} test cases passed")
        return success_count == len(test_cases)
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return False

def test_actual_llm_generation():
    """Test actual LLM generation with improved parsing"""
    
    if not Path('.env').exists():
        print("⚠️  No .env file - skipping actual LLM test")
        return True
    
    try:
        from llm_interface import LLMInterface
        
        llm = LLMInterface()
        
        # Test with the problematic finding from the user's example
        test_finding = {
            'rule_id': 'xccdf_org.ssgproject.content_rule_partition_for_opt',
            'severity': 'medium',
            'title': 'Ensure /opt Located On Separate Partition',
            'description': 'The /opt directory contains optional software packages.',
            'fix_text': 'Create a separate partition for /opt by adding an entry to /etc/fstab.'
        }
        
        print("🧪 Testing actual LLM generation with improved parsing...")
        result = llm.generate_ansible_task(test_finding)
        
        if result['success']:
            print("✅ LLM generation successful")
            print(f"   YAML valid: {result.get('yaml_valid', 'Unknown')}")
            print(f"   Content length: {len(result['content'])}")
            print(f"   Content preview:\n{result['content'][:300]}...")
            
            # Check for common issues
            content = result['content']
            issues = []
            
            if '```' in content:
                issues.append("Contains markdown code blocks")
            if 'please note' in content.lower():
                issues.append("Contains explanatory text")
            if content.count('- name:') > 1:
                issues.append("Contains multiple tasks")
            
            if issues:
                print(f"⚠️  Potential issues: {', '.join(issues)}")
            else:
                print("✅ Clean YAML output detected")
            
            return True
        else:
            print(f"❌ LLM generation failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Actual LLM test failed: {e}")
        return False

def main():
    """Run all markdown parsing tests"""
    print("🔧 Testing Improved Markdown Parsing")
    print("=" * 50)
    
    tests = [
        ("Markdown Parsing", test_markdown_parsing),
        ("Various Formats", test_various_formats),
        ("Actual LLM Generation", test_actual_llm_generation)
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
        print("\n🎉 Markdown parsing improvements verified!")
        print("The LLM interface should now handle markdown responses correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
