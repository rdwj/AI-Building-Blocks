#!/usr/bin/env python3
"""Test individual workflow steps"""

import asyncio
import sys
sys.path.append('src')

from llm_interface import LLMInterface
from simple_workflow import SimpleSTIGWorkflow

async def test_workflow_steps():
    """Test individual workflow steps"""
    
    # Sample finding
    sample_finding = {
        "rule_id": "xccdf_org.ssgproject.content_rule_package_telnet_removed",
        "severity": "high",
        "title": "Remove telnet Package",
        "description": "The telnet package contains the telnet client.",
        "check_text": "Run: $ rpm -q telnet",
        "fix_text": "Remove: $ sudo yum erase telnet",
        "status": "fail",
        "references": ["CCE-27305-2"],
        "weight": "10.0"
    }
    
    # Initialize workflow
    llm = LLMInterface()
    workflow = SimpleSTIGWorkflow(llm)
    
    # Initialize state
    from simple_workflow import SimpleWorkflowState
    from datetime import datetime
    
    state = SimpleWorkflowState(
        finding=sample_finding,
        action_type=None,
        target=None,
        parameters=None,
        task_name=None,
        final_playbook=None,
        validation_result=None,
        annotated_playbook=None,
        errors=[],
        metadata={'workflow_start': datetime.now().isoformat()}
    )
    
    print("=== Testing Steps 1-6 ===")
    
    # Step 1: Extract action
    print("Step 1: Extracting action type...")
    state = await workflow.extract_action(state)
    print(f"Action type: {state.get('action_type')}")
    
    # Step 2: Extract target
    print("Step 2: Extracting target...")
    state = await workflow.extract_target(state)
    print(f"Target: {state.get('target')}")
    
    # Step 3: Extract parameters
    print("Step 3: Extracting parameters...")
    state = await workflow.extract_parameters(state)
    print(f"Parameters: {state.get('parameters')}")
    
    # Step 4: Generate task name
    print("Step 4: Generating task name...")
    state = await workflow.generate_task_name(state)
    print(f"Task name: {state.get('task_name')}")
    
    # Step 5: Assemble playbook
    print("Step 5: Assembling playbook...")
    state = await workflow.assemble_playbook(state)
    print(f"Playbook assembled: {bool(state.get('final_playbook'))}")
    if state.get('final_playbook'):
        print("First 200 chars of playbook:")
        print(state['final_playbook'][:200] + "...")
    
    # Step 6: Validate playbook
    print("Step 6: Validating playbook...")
    state = await workflow.validate_playbook(state)
    validation = state.get('validation_result', {})
    print(f"Validation complete - Valid: {validation.get('is_valid', False)}")
    print(f"Issues: {len(validation.get('issues_found', []))}")
    print(f"Fixes: {len(validation.get('fixes_applied', []))}")
    
    print("\n=== Testing Step 7 (with timeout) ===")
    
    # Step 7: Annotate playbook (with manual timeout)
    print("Step 7: Annotating playbook...")
    try:
        state = await asyncio.wait_for(workflow.annotate_playbook(state), timeout=30)
        print(f"Annotation complete: {bool(state.get('annotated_playbook'))}")
    except asyncio.TimeoutError:
        print("❌ Step 7 timed out after 30 seconds")
        state['annotated_playbook'] = state.get('final_playbook', '')
    
    # Finalize
    print("Step 8: Finalizing...")
    state = await workflow.finalize_output(state)
    print(f"Final quality: {state['metadata'].get('final_quality', 'unknown')}")
    
    # Save outputs
    print("Saving outputs...")
    files = workflow._save_outputs(sample_finding, state)
    print(f"Files saved: {files}")
    
    return state

if __name__ == "__main__":
    asyncio.run(test_workflow_steps())