"""
Shared utilities for STIG to Ansible workflow

This package contains utility functions extracted from the prompt engineering
notebook for use in automated workflows.
"""

from .prompt_utils import (
    load_prompt,
    format_prompt,
    extract_json_from_response,
    llm_call_with_json,
    load_reference_file,
    initialize_workflow_state,
    update_workflow_state,
    validate_workflow_state,
    save_workflow_outputs,
    load_prompt_and_call_llm,
    load_findings_file,
    get_severity_counts,
    display_prompt,
    display_result,
    filter_findings_by_severity,
    clean_playbook_response,
    generate_workflow_summary
)

__all__ = [
    'load_prompt',
    'format_prompt',
    'extract_json_from_response',
    'llm_call_with_json',
    'load_reference_file',
    'initialize_workflow_state',
    'update_workflow_state',
    'validate_workflow_state',
    'save_workflow_outputs',
    'load_prompt_and_call_llm',
    'load_findings_file',
    'get_severity_counts',
    'display_prompt',
    'display_result',
    'filter_findings_by_severity',
    'clean_playbook_response',
    'generate_workflow_summary'
]