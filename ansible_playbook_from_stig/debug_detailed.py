#!/usr/bin/env python3
"""
Detailed debug script to find the exact formatting issue
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

# Import our modules
from shared.prompt_utils import load_prompt

# Sample finding from the notebook
SAMPLE_FINDING = {
    "rule_id": "xccdf_org.ssgproject.content_rule_prefer_64bit_os",
    "title": "Prefer to use a 64-bit Operating System when supported",
    "description": "Prefer installation of 64-bit operating systems when the CPU supports it.",
    "fix_text": ""
}

def debug_template_formatting():
    """Debug the template formatting issue step by step"""
    
    print("🔍 Debugging template formatting...")
    
    try:
        # Load the classification prompt
        classification_prompt = load_prompt('prompt_1_classification')
        print(f"✅ Loaded prompt successfully")
        
        # Get the template string
        template_str = classification_prompt['template']
        print(f"📄 Template string type: {type(template_str)}")
        print(f"📏 Template length: {len(template_str)} chars")
        
        # Show the template
        print(f"\n📋 Full template:")
        print("-" * 60)
        print(template_str)
        print("-" * 60)
        
        # Try to identify placeholder variables
        import re
        placeholders = re.findall(r'\{([^}]+)\}', template_str)
        print(f"\n🔍 Found placeholders: {placeholders}")
        
        # Check our kwargs
        kwargs = {
            'rule_id': SAMPLE_FINDING['rule_id'],
            'title': SAMPLE_FINDING['title'],
            'description': SAMPLE_FINDING['description'],
            'fix_text': SAMPLE_FINDING['fix_text']
        }
        print(f"\n📝 Kwargs keys: {list(kwargs.keys())}")
        
        # Check for missing placeholders
        missing = [p for p in placeholders if p not in kwargs]
        extra = [k for k in kwargs.keys() if k not in placeholders]
        
        print(f"\n🔍 Missing placeholders: {missing}")
        print(f"🔍 Extra kwargs: {extra}")
        
        # Try manual formatting
        print(f"\n🔧 Attempting manual format...")
        try:
            formatted = template_str.format(**kwargs)
            print(f"✅ Manual formatting successful!")
            print(f"📏 Formatted length: {len(formatted)} chars")
            
            # Show first part of formatted result
            print(f"\n📋 Formatted result (first 500 chars):")
            print("-" * 60)
            print(formatted[:500])
            print("-" * 60)
            
        except Exception as format_error:
            print(f"❌ Manual formatting failed: {format_error}")
            print(f"Error type: {type(format_error)}")
            
    except Exception as e:
        print(f"❌ Error in debug function: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_template_formatting()