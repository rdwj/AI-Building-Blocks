#!/usr/bin/env python3
"""
Debug script to test prompt formatting without LLM calls
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

# Import our modules
from shared.prompt_utils import load_prompt, format_prompt

# Sample finding from the notebook
SAMPLE_FINDING = {
    "rule_id": "xccdf_org.ssgproject.content_rule_prefer_64bit_os",
    "title": "Prefer to use a 64-bit Operating System when supported",
    "description": "Prefer installation of 64-bit operating systems when the CPU supports it.",
    "fix_text": ""
}

def test_prompt_formatting():
    """Test the prompt formatting without LLM calls"""
    
    print("🔍 Testing prompt formatting...")
    
    try:
        # Load the classification prompt
        classification_prompt = load_prompt('prompt_1_classification')
        print(f"✅ Loaded prompt: {classification_prompt['name']}")
        print(f"📋 Template length: {len(classification_prompt['template'])} chars")
        
        # Show the template
        print(f"\n📄 Template preview:")
        print("-" * 40)
        print(classification_prompt['template'][:500] + "..." if len(classification_prompt['template']) > 500 else classification_prompt['template'])
        print("-" * 40)
        
        # Try to format the prompt
        print(f"\n🔧 Attempting to format prompt...")
        
        formatted_prompt = format_prompt(
            classification_prompt,
            rule_id=SAMPLE_FINDING['rule_id'],
            title=SAMPLE_FINDING['title'],
            description=SAMPLE_FINDING['description'],
            fix_text=SAMPLE_FINDING['fix_text']
        )
        
        print(f"✅ Prompt formatted successfully!")
        print(f"📏 Formatted length: {len(formatted_prompt)} chars")
        
        print(f"\n📋 Formatted prompt:")
        print("-" * 40)
        print(formatted_prompt)
        print("-" * 40)
        
    except Exception as e:
        print(f"❌ Error formatting prompt: {e}")
        import traceback
        traceback.print_exc()

def test_expected_keys():
    """Test what keys are expected"""
    
    print(f"\n🔍 Testing expected keys...")
    
    try:
        # Test the llm_call_with_json function expectations
        expected_keys = ['category']
        
        # Mock result that should work
        mock_result = {"category": "SHELL_SCRIPT"}
        
        print(f"📋 Expected keys: {expected_keys}")
        print(f"📋 Mock result: {mock_result}")
        
        # Check if all expected keys are present
        missing_keys = [key for key in expected_keys if key not in mock_result]
        
        if not missing_keys:
            print(f"✅ All expected keys present")
        else:
            print(f"❌ Missing keys: {missing_keys}")
            
    except Exception as e:
        print(f"❌ Error testing keys: {e}")

if __name__ == "__main__":
    test_prompt_formatting()
    test_expected_keys()