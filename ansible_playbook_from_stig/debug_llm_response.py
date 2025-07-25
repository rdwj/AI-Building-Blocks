#!/usr/bin/env python3
"""
Debug script to test raw LLM response
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
from llm_interface import LLMInterface

async def test_raw_llm():
    """Test raw LLM response without any processing"""
    load_dotenv()
    
    # Initialize LLM
    llm = LLMInterface()
    
    # Test finding
    test_finding = {
        "rule_id": "xccdf_org.ssgproject.content_rule_package_telnet_removed",
        "severity": "high",
        "title": "Remove telnet Package",
        "description": "The telnet package contains the telnet client, which allows users to start connections to other systems via the telnet protocol.",
        "check_text": "Run the following command to determine if the telnet package is installed: $ rpm -q telnet",
        "fix_text": "The telnet package can be removed with the following command: $ sudo yum erase telnet",
        "status": "fail",
        "references": ["CCE-27305-2"],
        "weight": "10.0"
    }
    
    # Simple STIG prompt
    prompt = f"""Analyze this STIG finding and return JSON:

Finding: {test_finding['title']} - {test_finding['description']}
Fix: {test_finding['fix_text']}

Return JSON with action_type and target_name:
{{"action_type": "remove_package", "target_name": "telnet"}}"""
    
    print("🔍 Testing raw LLM response...")
    print("Prompt length:", len(prompt))
    print("Prompt:", prompt)
    
    try:
        # Call LLM with simple prompt first
        print("\n🤖 Calling LLM with simple prompt...")
        response = await llm.generate_ansible_task_async(
            prompt=prompt,
            max_tokens=200
        )
        print("✅ LLM call completed")
        
        print("\n✅ Raw LLM Response:")
        print(f"Response type: {type(response)}")
        print(f"Response length: {len(response)}")
        print(f"Response content: '{response}'")
        print(f"Response bytes: {response.encode()}")
        
        # Try to parse as JSON
        try:
            parsed = json.loads(response.strip())
            print("\n✅ JSON parsing successful:")
            print(json.dumps(parsed, indent=2))
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON parsing failed: {e}")
            print(f"Attempting to clean response...")
            
            # Try cleaning
            clean = response.strip()
            if clean.startswith('```json'):
                clean = clean[7:]
            if clean.endswith('```'):
                clean = clean[:-3]
            clean = clean.strip()
            
            print(f"Cleaned response: '{clean}'")
            
            try:
                parsed = json.loads(clean)
                print("✅ JSON parsing successful after cleaning:")
                print(json.dumps(parsed, indent=2))
            except json.JSONDecodeError as e2:
                print(f"❌ JSON parsing still failed: {e2}")
        
    except Exception as e:
        print(f"❌ LLM call failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_raw_llm())