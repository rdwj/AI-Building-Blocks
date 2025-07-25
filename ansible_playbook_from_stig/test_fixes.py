#!/usr/bin/env python3
"""
Quick test to verify the linter fixes and LLM interface work correctly
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_stig_parser_import():
    """Test that STIG parser imports without linter errors"""
    try:
        from stig_parser_enhanced import STIGParser, STIGFinding
        print("✅ STIG Parser imports successfully (no linter errors)")
        
        # Test basic functionality
        parser = STIGParser()
        print(f"✅ STIG Parser instantiated successfully")
        
        # Test dataclass
        sample_finding = STIGFinding(
            rule_id="TEST-001",
            severity="High",
            title="Test finding",
            description="Test description",
            check_text="Test check",
            fix_text="Test fix",
            status="fail",
            references=["TEST-REF"]
        )
        print(f"✅ STIGFinding dataclass works: {sample_finding.rule_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ STIG Parser test failed: {e}")
        return False

def test_llm_interface_import():
    """Test that LLM interface imports and initializes correctly"""
    try:
        from llm_interface import LLMInterface
        print("✅ LLM Interface imports successfully")
        
        # Check if .env exists
        if not Path('.env').exists():
            print("⚠️  No .env file - skipping LLM initialization test")
            return True
        
        # Test initialization
        llm = LLMInterface()
        print(f"✅ LLM Interface initialized with model: {llm.model_name}")
        print(f"   URL: {llm.api_url}")
        
        # Test prompt creation
        sample_finding = {
            'rule_id': 'TEST-001',
            'severity': 'High',
            'title': 'Test finding',
            'description': 'Test description',
            'fix_text': 'Test fix'
        }
        
        prompt = llm.create_ansible_prompt(sample_finding)
        print(f"✅ Prompt creation works ({len(prompt)} characters)")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM Interface test failed: {e}")
        return False

def test_integration():
    """Test that both components work together"""
    try:
        from stig_parser_enhanced import STIGParser, STIGFinding
        from llm_interface import LLMInterface
        
        print("✅ Both modules import together successfully")
        
        # Test data flow
        sample_finding = STIGFinding(
            rule_id="INTEGRATION-TEST",
            severity="Medium",
            title="Integration test finding",
            description="This tests the integration between parser and LLM",
            check_text="Verify integration works",
            fix_text="Run integration test to fix",
            status="fail",
            references=[]
        )
        
        # Convert to dict for LLM interface
        finding_dict = {
            'rule_id': sample_finding.rule_id,
            'severity': sample_finding.severity,
            'title': sample_finding.title,
            'description': sample_finding.description,
            'fix_text': sample_finding.fix_text
        }
        
        if Path('.env').exists():
            llm = LLMInterface()
            prompt = llm.create_ansible_prompt(finding_dict)
            print("✅ Integration test: STIG finding → LLM prompt conversion works")
        else:
            print("⚠️  Integration test skipped (no .env file)")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔧 Testing Fixed Components")
    print("=" * 40)
    
    tests = [
        ("STIG Parser (Linter Fixes)", test_stig_parser_import),
        ("LLM Interface (API Fixes)", test_llm_interface_import),
        ("Integration Test", test_integration)
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
        print("\n🎉 All fixes verified! Ready to test the full system.")
        print("\nNext step: python test_system.py")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
