#!/usr/bin/env python3
"""
Prompt Engineering Utilities

Utility functions extracted from prompt_engineering_v2.ipynb for use in
the STIG to Ansible workflow. These functions handle prompt loading,
formatting, JSON extraction, and LLM interactions.
"""

import json
import yaml
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime


def load_prompt(prompt_name: str, prompts_dir: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """
    Load a prompt from the prompts directory
    
    Args:
        prompt_name: Name of the prompt file (without .yaml extension)
        prompts_dir: Directory containing prompt files (defaults to ../prompts relative to this file)
    
    Returns:
        Dictionary containing prompt data with keys: name, description, template, parameters
    """
    if prompts_dir is None:
        # Default to prompts directory relative to this file
        current_dir = Path(__file__).parent
        prompts_dir = current_dir.parent.parent / "prompts"
    else:
        prompts_dir = Path(prompts_dir)
    
    prompt_path = prompts_dir / f"{prompt_name}.yaml"
    
    try:
        with open(prompt_path, 'r') as f:
            prompt_data = yaml.safe_load(f)
            
            # Set default parameters if not present
            if 'parameters' not in prompt_data:
                prompt_data['parameters'] = {}
            
            # Convert parameter list to dictionary if needed
            if isinstance(prompt_data['parameters'], list):
                param_dict = {}
                for param in prompt_data['parameters']:
                    if isinstance(param, dict):
                        param_dict.update(param)
                prompt_data['parameters'] = param_dict
            
            # Set default parameter values
            default_params = {
                'temperature': 0.3,
                'max_tokens': 5000,
                'top_p': 0.9,
                'frequency_penalty': 0.0,
                'presence_penalty': 0.0
            }
            
            # Merge defaults with provided parameters
            for key, default_value in default_params.items():
                if key not in prompt_data['parameters']:
                    prompt_data['parameters'][key] = default_value
            
            print(f"📄 Loaded prompt: {prompt_data.get('name', prompt_name)}")
            print(f"   Temperature: {prompt_data['parameters']['temperature']}")
            print(f"   Max tokens: {prompt_data['parameters']['max_tokens']}")
            
            return prompt_data
    except FileNotFoundError:
        print(f"❌ Prompt file not found: {prompt_path}")
        return {
            'name': prompt_name, 
            'description': 'Not found', 
            'template': 'Prompt template not available',
            'parameters': {'temperature': 0.3, 'max_tokens': 5000}
        }
    except Exception as e:
        print(f"❌ Error loading prompt {prompt_name}: {e}")
        return {
            'name': prompt_name, 
            'description': 'Error loading', 
            'template': 'Error loading prompt template',
            'parameters': {'temperature': 0.3, 'max_tokens': 5000}
        }


def format_prompt(prompt_data: Dict[str, Any], **kwargs) -> str:
    """
    Format a prompt template with provided variables
    
    Args:
        prompt_data: Dictionary containing prompt template
        **kwargs: Variables to substitute in the template
    
    Returns:
        Formatted prompt string
    """
    try:
        template_str = prompt_data['template']
        formatted = template_str.format(**kwargs)
        return formatted
    except Exception as e:
        print(f"❌ Error formatting prompt: {e}")
        return f"Error formatting prompt: {e}"


def extract_json_from_response(response: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON from LLM response using regex
    
    Args:
        response: Raw LLM response string
    
    Returns:
        Parsed JSON dictionary or None if no valid JSON found
    """
    try:
        # Remove any markdown code blocks
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*$', '', response)
        
        # Find JSON pattern - improved to handle nested objects
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, response, re.DOTALL)
        
        # Try each match to see if it's valid JSON
        for match in matches:
            try:
                parsed = json.loads(match)
                print(f"✅ Extracted JSON with {len(parsed)} keys")
                return parsed
            except json.JSONDecodeError:
                continue
        
        print("⚠️ No valid JSON found in response")
        return None
        
    except Exception as e:
        print(f"❌ Error extracting JSON: {e}")
        return None


async def llm_call_with_json(llm_interface, prompt: str, expected_keys: List[str], 
                           max_tokens: int = 100, max_retries: int = 3, 
                           prompt_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Make LLM call and extract JSON response with retry logic
    
    Args:
        llm_interface: Initialized LLM interface object
        prompt: Formatted prompt string
        expected_keys: List of expected JSON keys
        max_tokens: Maximum tokens for response (overridden by prompt_params if provided)
        max_retries: Maximum retry attempts
        prompt_params: Optional parameters from prompt (temperature, max_tokens, etc.)
    
    Returns:
        Dictionary with extracted JSON data or fallback values
    """
    # Use prompt parameters if provided
    if prompt_params:
        max_tokens = prompt_params.get('max_tokens', max_tokens)
    
    print(f"🎯 Using max_tokens: {max_tokens}")
    if llm_interface is None:
        print("❌ LLM not initialized")
        return {key: "llm_not_available" for key in expected_keys}
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 LLM call attempt {attempt + 1}/{max_retries}")
            
            # Adjust prompt for retry attempts
            if attempt == 0:
                full_prompt = prompt
            else:
                full_prompt = f"{prompt}\n\nIMPORTANT: The previous response was not valid JSON. Please respond with ONLY valid JSON containing these keys: {expected_keys}"
            
            # Make the LLM call
            response = await llm_interface.generate_ansible_task_async(
                prompt=full_prompt,
                max_tokens=max_tokens
            )
            
            print(f"📝 Raw response length: {len(response)} characters")
            print(f"📝 Raw response preview: {response[:200]}{'...' if len(response) > 200 else ''}")
            
            # Try to extract JSON
            json_data = extract_json_from_response(response)
            
            if json_data:
                # Validate expected keys
                missing_keys = [key for key in expected_keys if key not in json_data]
                if not missing_keys:
                    print(f"✅ Valid JSON extracted with all expected keys")
                    return json_data
                else:
                    print(f"⚠️ JSON missing keys: {missing_keys}")
                    # Fill in missing keys with default values
                    for key in missing_keys:
                        json_data[key] = "unknown"
                    return json_data
            else:
                print(f"⚠️ No valid JSON found in attempt {attempt + 1}")
                
        except Exception as e:
            print(f"❌ Error in LLM call attempt {attempt + 1}: {e}")
    
    # If all retries failed, return fallback
    print(f"❌ All {max_retries} attempts failed")
    return {key: "extraction_failed" for key in expected_keys}


def load_reference_file(filename: str, reference_dir: Optional[Union[str, Path]] = None) -> str:
    """
    Load a reference file from the reference directory
    
    Args:
        filename: Name of the reference file
        reference_dir: Directory containing reference files (defaults to ../reference)
    
    Returns:
        File content as string
    """
    if reference_dir is None:
        # Default to reference directory relative to this file
        current_dir = Path(__file__).parent
        reference_dir = current_dir.parent.parent / "reference"
    else:
        reference_dir = Path(reference_dir)
    
    file_path = reference_dir / filename
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            print(f"📄 Loaded reference file: {filename}")
            return content
    except FileNotFoundError:
        print(f"❌ Reference file not found: {file_path}")
        return f"Reference file {filename} not found"
    except Exception as e:
        print(f"❌ Error loading reference file {filename}: {e}")
        return f"Error loading reference file {filename}: {e}"


def initialize_workflow_state(finding: Dict[str, Any]) -> Dict[str, Any]:
    """
    Initialize workflow state for a STIG finding
    
    Args:
        finding: Dictionary containing STIG finding data
    
    Returns:
        Initialized workflow state dictionary
    """
    return {
        # Core workflow data
        'finding': finding,
        'action_type': None,
        'target': None, 
        'parameters': None,
        'task_name': None,
        'final_playbook': None,
        'validation_result': None,
        'annotated_playbook': None,
        
        # Tracking and metadata
        'errors': [],
        'step_results': {},
        'metadata': {
            'workflow_start': datetime.now().isoformat(),
            'rule_id': finding.get('rule_id', 'unknown'),
            'workflow_type': 'automated',
            'steps_completed': []
        }
    }


def update_workflow_state(state: Dict[str, Any], step_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update workflow state with step results
    
    Args:
        state: Current workflow state
        step_name: Name of the completed step
        result: Result dictionary from the step
    
    Returns:
        Updated workflow state
    """
    state['step_results'][step_name] = result
    state['metadata']['steps_completed'].append(step_name)
    state['metadata'][f'{step_name}_complete'] = datetime.now().isoformat()
    
    return state


def validate_workflow_state(state: Dict[str, Any]) -> List[str]:
    """
    Validate workflow state and return list of issues
    
    Args:
        state: Workflow state to validate
    
    Returns:
        List of validation issues (empty if valid)
    """
    issues = []
    
    # Check required fields
    if not state.get('finding'):
        issues.append("Missing finding data")
    
    if not state.get('action_type'):
        issues.append("Missing action_type")
    
    if not state.get('target'):
        issues.append("Missing target")
    
    if not state.get('task_name'):
        issues.append("Missing task_name")
    
    # Check for errors
    if state.get('errors'):
        issues.extend([f"Error: {error}" for error in state['errors']])
    
    return issues


def save_workflow_outputs(state: Dict[str, Any], output_dir: Optional[Union[str, Path]] = None) -> Dict[str, str]:
    """
    Save workflow outputs to files
    
    Args:
        state: Complete workflow state
        output_dir: Directory to save outputs (defaults to ../playbooks)
    
    Returns:
        Dictionary with paths to saved files
    """
    if output_dir is None:
        # Default to playbooks directory relative to this file
        current_dir = Path(__file__).parent
        output_dir_path = current_dir.parent.parent / "playbooks"
    else:
        output_dir_path = Path(output_dir)
    
    # Create output directory
    output_dir_path.mkdir(exist_ok=True)
    
    # Generate timestamp and rule ID for filenames
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    rule_id = state['finding'].get('rule_id', 'unknown')
    
    saved_files = {}
    
    # Save final playbook
    final_playbook = state.get('annotated_playbook') or state.get('final_playbook')
    if final_playbook:
        playbook_file = output_dir_path / f"auto_{rule_id}_{timestamp}.yml"
        try:
            with open(playbook_file, 'w') as f:
                f.write(final_playbook)
            saved_files['playbook'] = str(playbook_file)
            print(f"💾 Saved playbook to: {playbook_file}")
        except Exception as e:
            print(f"❌ Failed to save playbook: {e}")
    
    # Save workflow state
    state_file = output_dir_path / f"auto_{rule_id}_{timestamp}_state.json"
    try:
        # Create a serializable version of the state
        serializable_state = {
            'metadata': state['metadata'],
            'extracted_components': {
                'action_type': state.get('action_type'),
                'target': state.get('target'),
                'parameters': state.get('parameters'),
                'task_name': state.get('task_name')
            },
            'validation_result': state.get('validation_result'),
            'errors': state.get('errors', []),
            'step_results': state.get('step_results', {}),
            'finding_info': {
                'rule_id': state['finding'].get('rule_id'),
                'title': state['finding'].get('title'),
                'severity': state['finding'].get('severity')
            }
        }
        
        with open(state_file, 'w') as f:
            json.dump(serializable_state, f, indent=2)
        saved_files['state'] = str(state_file)
        print(f"💾 Saved workflow state to: {state_file}")
    except Exception as e:
        print(f"❌ Failed to save workflow state: {e}")
    
    return saved_files


def load_prompt_and_call_llm(llm_interface, prompt_name: str, expected_keys: List[str], 
                           max_retries: int = 3, **format_kwargs) -> Dict[str, Any]:
    """
    Load a prompt, format it, and make LLM call in one function
    
    Args:
        llm_interface: Initialized LLM interface object
        prompt_name: Name of the prompt file to load
        expected_keys: List of expected JSON keys in response
        max_retries: Maximum retry attempts
        **format_kwargs: Variables to substitute in the prompt template
    
    Returns:
        Dictionary with extracted JSON data or fallback values
    """
    import asyncio
    
    # Load the prompt
    prompt_data = load_prompt(prompt_name)
    
    # Format the prompt with provided variables
    formatted_prompt = format_prompt(prompt_data, **format_kwargs)
    
    # Make the LLM call using the prompt's parameters
    return asyncio.run(llm_call_with_json(
        llm_interface, 
        formatted_prompt, 
        expected_keys, 
        max_retries=max_retries,
        prompt_params=prompt_data.get('parameters', {})
    ))


def load_findings_file(findings_file: str) -> List[Dict[str, Any]]:
    """
    Load STIG findings from JSON file
    
    Args:
        findings_file: Path to findings JSON file
    
    Returns:
        List of finding dictionaries
    """
    try:
        with open(findings_file, 'r') as f:
            findings_data = json.load(f)
        
        # Extract the findings array from the JSON structure
        all_findings = findings_data.get('findings', [])
        print(f"📊 Loaded {len(all_findings)} findings from {findings_file}")
        
        return all_findings
        
    except FileNotFoundError:
        print(f"❌ Findings file not found: {findings_file}")
        return []
    except Exception as e:
        print(f"❌ Error loading findings: {e}")
        return []


def get_severity_counts(findings: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Get severity distribution from list of findings
    
    Args:
        findings: List of finding dictionaries
    
    Returns:
        Dictionary with severity counts
    """
    severity_counts = {}
    for finding in findings:
        severity = finding.get('severity', 'unknown')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    return severity_counts


def display_prompt(prompt_text: str, max_length: int = 10000):
    """
    Display a prompt nicely formatted with optional truncation
    
    Args:
        prompt_text: The prompt text to display
        max_length: Maximum length before truncation
    """
    try:
        # For notebook environments
        from IPython.display import display, Markdown
        
        if len(prompt_text) > max_length:
            truncated = prompt_text[:max_length] + "\n\n... [TRUNCATED] ..."
            display(Markdown(f"### 📋 Prompt (showing first {max_length} characters):\n```\n{truncated}\n```"))
        else:
            display(Markdown(f"### 📋 Prompt:\n```\n{prompt_text}\n```"))
    except ImportError:
        # For non-notebook environments, use regular print
        print(f"📋 Prompt (length: {len(prompt_text)} chars):")
        print("-" * 60)
        if len(prompt_text) > max_length:
            truncated = prompt_text[:max_length] + "\n\n... [TRUNCATED] ..."
            print(truncated)
        else:
            print(prompt_text)
        print("-" * 60)


def display_result(step_name: str, result: Dict[str, Any]):
    """
    Display step results nicely formatted
    
    Args:
        step_name: Name of the step
        result: Result dictionary to display
    """
    try:
        # For notebook environments
        from IPython.display import display, Markdown, JSON
        
        display(Markdown(f"### ✅ {step_name} Result:"))
        display(JSON(result, expanded=True))
    except ImportError:
        # For non-notebook environments, use regular print
        print(f"✅ {step_name} Result:")
        print(json.dumps(result, indent=2))


def filter_findings_by_severity(findings: List[Dict[str, Any]], severity: str) -> List[Dict[str, Any]]:
    """
    Filter findings by severity level
    
    Args:
        findings: List of finding dictionaries
        severity: Severity level to filter by
    
    Returns:
        Filtered list of findings
    """
    return [f for f in findings if f.get('severity', '').lower() == severity.lower()]


def clean_playbook_response(playbook_content: str) -> str:
    """
    Clean playbook content from LLM response
    
    Args:
        playbook_content: Raw playbook content from LLM
    
    Returns:
        Cleaned playbook content
    """
    # Clean up markdown formatting if present
    if playbook_content.startswith('```yaml'):
        playbook_content = playbook_content[7:]
    if playbook_content.startswith('```'):
        playbook_content = playbook_content[3:]
    if playbook_content.endswith('```'):
        playbook_content = playbook_content[:-3]
    
    # Ensure it starts with document separator
    if not playbook_content.strip().startswith('---'):
        playbook_content = '---\n' + playbook_content
    
    return playbook_content.strip()


def generate_workflow_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a summary of the workflow results
    
    Args:
        state: Complete workflow state
    
    Returns:
        Summary dictionary with key metrics
    """
    # Calculate workflow quality
    if state.get('final_playbook') and len(state.get('errors', [])) == 0:
        validation = state.get('validation_result', {})
        if validation.get('is_valid', False):
            final_quality = 'high'
        else:
            final_quality = 'medium'
    elif state.get('final_playbook'):
        final_quality = 'low'
    else:
        final_quality = 'failed'
    
    return {
        "workflow_info": {
            "finding_id": state['finding'].get('rule_id', 'unknown'),
            "finding_title": state['finding'].get('title', 'unknown'),
            "severity": state['finding'].get('severity', 'unknown'),
            "workflow_quality": final_quality,
            "total_errors": len(state.get('errors', []))
        },
        "extracted_components": {
            "action_type": state.get('action_type'),
            "target": state.get('target'),
            "parameters": state.get('parameters'),
            "task_name": state.get('task_name')
        },
        "workflow_progress": {
            "steps_completed": len(state['metadata']['steps_completed']),
            "total_steps": 7,
            "completed_steps": state['metadata']['steps_completed'],
            "start_time": state['metadata']['workflow_start'],
            "end_time": state['metadata'].get('workflow_complete')
        },
        "outputs": {
            "has_final_playbook": bool(state.get('final_playbook')),
            "has_annotated_playbook": bool(state.get('annotated_playbook')),
            "validation_passed": state.get('validation_result', {}).get('is_valid', False),
            "playbook_length": len(state.get('annotated_playbook') or state.get('final_playbook', '')),
        }
    }


if __name__ == "__main__":
    print("🧰 Prompt Engineering Utilities")
    print("=" * 40)
    print("This module provides utilities for:")
    print("- Loading and formatting prompts")
    print("- Extracting JSON from LLM responses")
    print("- Managing workflow state")
    print("- Saving workflow outputs")
    print("\nImport this module to use in your workflow scripts.")