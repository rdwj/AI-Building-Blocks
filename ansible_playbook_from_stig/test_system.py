#!/usr/bin/env python3
"""
Test script for STIG to Ansible Playbook Generator

This tests the complete pipeline from STIG parsing to playbook generation.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported"""
    try:
        from stig_parser_enhanced import STIGParser, STIGFinding
        from llm_interface import LLMInterface
        print("✅ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_stig_parser():
    """Test STIG parser with sample file"""
    try:
        from stig_parser_enhanced import STIGParser
        
        # Test with sample file if available
        sample_files = [
            "../xml_files/sample_data/node2.example.com-STIG-20250710162433.xml",
            "../xml_files/sample_data/node2.example.com-PCI-20250710162255.xml"
        ]
        
        for sample_file in sample_files:
            if Path(sample_file).exists():
                print(f"🧪 Testing STIG parser with {Path(sample_file).name}")
                
                parser = STIGParser()
                findings = parser.parse_stig_file(sample_file)
                
                if findings:
                    print(f"✅ Extracted {len(findings)} findings")
                    
                    # Show first finding
                    first_finding = findings[0]
                    print(f"   📋 Sample finding:")
                    print(f"      ID: {first_finding.rule_id}")
                    print(f"      Severity: {first_finding.severity}")
                    print(f"      Status: {first_finding.status}")
                    print(f"      Title: {first_finding.title[:60]}...")
                    
                    return True
                else:
                    print(f"⚠️  No findings extracted from {sample_file}")
                    
        print("❌ No sample files found for testing")
        return False
        
    except Exception as e:
        print(f"❌ STIG parser test failed: {e}")
        return False

def test_llm_interface():
    """Test LLM interface"""
    try:
        from llm_interface import LLMInterface
        
        # Check .env file
        if not Path('.env').exists():
            print("⚠️  No .env file found - skipping LLM test")
            print("   Create .env file to test LLM integration")
            return True
        
        print("🤖 Testing LLM interface...")
        
        # Create sample finding
        sample_finding = {
            'rule_id': 'TEST-001',
            'severity': 'High',
            'title': 'Test finding for verification',
            'description': 'This is a test finding to verify LLM integration',
            'fix_text': 'Run test command to fix this issue'
        }
        
        llm = LLMInterface()
        result = llm.generate_ansible_task(sample_finding)
        
        if result['success']:
            print("✅ LLM interface working")
            print(f"   Generated {len(result['content'])} characters")
            if result.get('yaml_valid'):
                print("   ✅ YAML validation passed")
            else:
                print("   ⚠️  YAML validation uncertain")
            return True
        else:
            print(f"❌ LLM interface failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ LLM interface test failed: {e}")
        return False

def test_environment():
    """Test environment setup"""
    print("🔧 Testing environment setup...")
    
    # Check directories
    required_dirs = ['src', 'findings', 'playbooks']
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ Directory {dir_name}/ exists")
        else:
            print(f"❌ Directory {dir_name}/ missing")
            dir_path.mkdir(exist_ok=True)
            print(f"   Created {dir_name}/")
    
    # Check .env file
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .env file exists")
        
        # Check for required variables
        with open(env_file, 'r') as f:
            env_content = f.read()
        
        required_vars = ['LLAMA_3_2_URL', 'LLAMA_3_2_API_KEY', 'LLAMA_3_2_MODEL_NAME']
        for var in required_vars:
            if var in env_content:
                print(f"   ✅ {var} configured")
            else:
                print(f"   ❌ {var} missing")
    else:
        print("⚠️  .env file not found")
        print("   Copy .env.template to .env and configure your LLAMA settings")
    
    return True

def main():
    """Run all tests"""
    print("🧪 STIG to Ansible Playbook Generator - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Environment Setup", test_environment),
        ("Module Imports", test_imports),
        ("STIG Parser", test_stig_parser),
        ("LLM Interface", test_llm_interface)
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
    print(f"\n📊 Test Summary")
    print("=" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Ready to generate playbooks.")
        print("\nNext steps:")
        print("1. Ensure .env file is properly configured")
        print("2. Run: python generate_playbooks.py <stig_file.xml>")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
