#!/usr/bin/env python3
"""Test annotation step specifically"""

import asyncio
import sys
sys.path.append('src')

from llm_interface import LLMInterface
from simple_workflow import SimpleSTIGWorkflow

async def test_annotation():
    """Test the annotation step specifically"""
    
    # Sample finding
    sample_finding = {
        "rule_id": "xccdf_org.ssgproject.content_rule_package_telnet_removed",
        "severity": "high",
        "title": "Remove telnet Package",
        "description": "The telnet package contains the telnet client.",
        "check_text": "Run: $ rpm -q telnet",
        "fix_text": "Remove: $ sudo yum erase telnet",
        "references": ["CCE-27305-2"],
    }
    
    # Sample playbook to annotate
    playbook_content = '''---
- name: "STIG HIGH: Remove telnet package to ensure secure communications"
  hosts: "all"
  become: true
  tags:
    - high_security
  tasks:
    - name: STIG HIGH: Remove telnet package to ensure secure communications
      action: remove_package
      args:
        name: telnet
        state: absent'''
    
    # Initialize workflow
    llm = LLMInterface()
    workflow = SimpleSTIGWorkflow(llm)
    
    # Create state for annotation
    from simple_workflow import SimpleWorkflowState
    from datetime import datetime
    
    state = SimpleWorkflowState(
        finding=sample_finding,
        action_type="remove_package",
        target="telnet",
        parameters="absent",
        task_name="STIG HIGH: Remove telnet package to ensure secure communications",
        final_playbook=playbook_content,
        validation_result={"is_valid": True, "issues_found": [], "fixes_applied": []},
        annotated_playbook=None,
        errors=[],
        metadata={'workflow_start': datetime.now().isoformat()}
    )
    
    print("=== Testing Annotation Step ===")
    print("Original playbook:")
    print(playbook_content)
    print("\n" + "="*50 + "\n")
    
    try:
        # Test annotation with timeout
        print("Running annotation step with 60-second timeout...")
        state = await asyncio.wait_for(workflow.annotate_playbook(state), timeout=60)
        
        if state.get('annotated_playbook'):
            print("✅ Annotation successful!")
            print("\nAnnotated playbook:")
            print(state['annotated_playbook'])
        else:
            print("❌ No annotated playbook returned")
            
    except asyncio.TimeoutError:
        print("❌ Annotation timed out after 60 seconds")
    except Exception as e:
        print(f"❌ Annotation failed: {e}")
    
    return state

if __name__ == "__main__":
    asyncio.run(test_annotation())