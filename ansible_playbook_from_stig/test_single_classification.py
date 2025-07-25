#!/usr/bin/env python3
"""
Simple test script for a single classification
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

# Import our modules
from llm_interface import LLMInterface
from shared.prompt_utils import load_prompt, format_prompt, llm_call_with_json

# Test one finding
SAMPLE_FINDING = {
    "rule_id": "xccdf_org.ssgproject.content_rule_disable_prelink",
    "title": "Disable Prelinking",
    "description": "The prelinking feature changes binaries in an attempt to decrease their startup time. In order to disable prelinking, the PRELINKING parameter in /etc/sysconfig/prelink must be set to no.",
    "fix_text": "# prelink not installed if test -e /etc/sysconfig/prelink -o -e /usr/sbin/prelink; then if grep -q ^PRELINKING /etc/sysconfig/prelink then sed -i 's/^PRELINKING[:blank:]*=[:blank:]*[:alpha:]*/PRELINKING=no/' /etc/sysconfig/prelink else echo 'PRELINKING=no' >> /etc/sysconfig/prelink fi fi"
}

async def test_single_classification():
    """Test classification of one finding"""
    
    print("🔍 Testing single classification...")
    
    try:
        # Initialize LLM
        llm = LLMInterface()
        print(f"✅ LLM initialized: {llm.model_name}")
        
        # Load classification prompt
        classification_prompt = load_prompt('prompt_1_classification')
        print(f"✅ Loaded prompt: {classification_prompt['name']}")
        
        # Format the prompt
        formatted_prompt = format_prompt(
            classification_prompt,
            rule_id=SAMPLE_FINDING['rule_id'],
            title=SAMPLE_FINDING['title'],
            description=SAMPLE_FINDING['description'],
            fix_text=SAMPLE_FINDING['fix_text']
        )
        
        print(f"✅ Prompt formatted successfully")
        print(f"📏 Formatted length: {len(formatted_prompt)} chars")
        
        # Show the formatted prompt
        print(f"\n📋 Formatted prompt (first 800 chars):")
        print("-" * 60)
        print(formatted_prompt[:800] + "..." if len(formatted_prompt) > 800 else formatted_prompt)
        print("-" * 60)
        
        # Make the LLM call
        print(f"\n🔄 Making LLM call...")
        result = await llm_call_with_json(
            llm,
            formatted_prompt,
            ['category'],
            max_retries=3,
            prompt_params=classification_prompt['parameters']
        )
        
        print(f"\n✅ LLM call completed!")
        print(f"📊 Result: {result}")
        
        # Analyze the result
        category = result.get('category', 'UNKNOWN')
        expected_categories = ['SHELL_SCRIPT', 'PACKAGE_VERIFICATION', 'CONFIG_MODIFICATION', 
                             'BOOT_CONFIGURATION', 'MULTI_STEP_PROCESS', 'CRON_SCHEDULING', 'UNKNOWN']
        
        is_valid = category in expected_categories
        print(f"\n📈 Analysis:")
        print(f"   Classification: {category}")
        print(f"   Valid category: {is_valid}")
        
        if not is_valid:
            print(f"   Expected one of: {expected_categories}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(test_single_classification())
    if result:
        print(f"\n🎉 Test completed successfully!")
        print(f"Final classification: {result.get('category', 'UNKNOWN')}")
    else:
        print(f"\n❌ Test failed")