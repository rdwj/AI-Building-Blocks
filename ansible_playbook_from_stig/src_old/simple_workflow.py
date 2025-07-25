#!/usr/bin/env python3
"""
Simple workflow for small LLM models - breaks down complex tasks into simple extractions
"""

import json
import logging
import os
import uuid
import re
import subprocess
import tempfile
from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime
from pathlib import Path
import yaml

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage

from llm_interface import LLMInterface

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleWorkflowState(TypedDict):
    """State for simple workflow with extracted components"""
    finding: Dict[str, Any]  # Original STIG finding
    action_type: Optional[str]  # Step 1: action type
    target: Optional[str]  # Step 2: target name
    parameters: Optional[str]  # Step 3: parameters
    task_name: Optional[str]  # Step 4: task name
    final_playbook: Optional[str]  # Step 5: assembled playbook
    validation_result: Optional[Dict[str, Any]]  # Step 6: validation results
    annotated_playbook: Optional[str]  # Step 7: documented playbook
    errors: List[str]  # Error tracking
    metadata: Dict[str, Any]  # Workflow metadata


class SimpleSTIGWorkflow:
    """Simple workflow optimized for small LLM models"""
    
    def __init__(self, llm_interface: LLMInterface):
        self.llm = llm_interface
        self.prompts_dir = "prompts"
        self.prompts = {}
        self._load_prompts()
        self.graph = self._build_graph()
        
    def _load_prompts(self):
        """Load all simple prompt templates"""
        prompt_files = {
            'extract_action': 'extract_action.yaml',
            'extract_target': 'extract_target.yaml',
            'extract_parameters': 'extract_parameters.yaml',
            'generate_task_name': 'generate_task_name.yaml',
            'assemble_playbook': 'assemble_playbook.yaml',
            'validate_playbook': 'validate_playbook.yaml',
            'validate_and_fix_playbook': 'validate_and_fix_playbook.yaml',
            'annotate_playbook': 'annotate_playbook.yaml'
        }
        
        for key, filename in prompt_files.items():
            filepath = os.path.join(self.prompts_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    prompt_data = yaml.safe_load(f)
                    self.prompts[key] = prompt_data
                    logger.info(f"Loaded prompt: {filename}")
            except Exception as e:
                logger.error(f"Failed to load prompt {filename}: {e}")
                raise
    
    def _format_prompt(self, prompt_key: str, **kwargs) -> str:
        """Format a prompt template with provided variables"""
        from string import Template
        template_str = self.prompts[prompt_key]['template']
        template = Template(template_str)
        return template.safe_substitute(**kwargs)
    
    def _extract_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from LLM response using regex"""
        # Remove any markdown code blocks
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*$', '', response)
        
        # Find JSON pattern
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, response)
        
        # Try each match to see if it's valid JSON
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
        
        return None
    
    async def _llm_call_with_json_validation(self, prompt: str, expected_keys: List[str], 
                                           max_retries: int = 3, max_tokens: int = 100) -> Dict[str, Any]:
        """Make LLM call with JSON validation and retry logic"""
        for attempt in range(max_retries):
            try:
                # Make the LLM call
                if attempt == 0:
                    full_prompt = prompt
                else:
                    full_prompt = f"{prompt}\n\nThat response did not have valid JSON with the expected format. Please respond with only JSON containing these keys: {expected_keys}"
                
                response = await self.llm.generate_ansible_task_async(
                    prompt=full_prompt,
                    max_tokens=max_tokens
                )
                
                # Log the full response for debugging
                logger.info(f"FULL API RESPONSE (attempt {attempt + 1}): {repr(response)}")
                
                # Try to extract JSON
                json_data = self._extract_json_from_response(response)
                
                if json_data:
                    # Validate expected keys
                    if all(key in json_data for key in expected_keys):
                        logger.debug(f"Valid JSON extracted: {json_data}")
                        return json_data
                    else:
                        logger.warning(f"JSON missing expected keys. Got: {list(json_data.keys())}, Expected: {expected_keys}")
                else:
                    logger.warning(f"No valid JSON found in response: {response[:100]}...")
                    
            except Exception as e:
                logger.error(f"Error in LLM call attempt {attempt + 1}: {e}")
        
        # If all retries failed, return fallback
        logger.error(f"All {max_retries} attempts failed to get valid JSON")
        return {key: "unknown" for key in expected_keys}
    
    def _run_ansible_lint(self, playbook_content: str) -> Dict[str, Any]:
        """Run ansible-lint on the playbook content"""
        try:
            # Check if ansible-lint is available
            result = subprocess.run(['ansible-lint', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return {"available": False, "error": "ansible-lint not found"}
            
            # Create temporary file for the playbook
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
                f.write(playbook_content)
                temp_file = f.name
            
            try:
                # Run ansible-lint
                result = subprocess.run(['ansible-lint', '--format', 'json', temp_file], 
                                      capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    return {"available": True, "passed": True, "issues": []}
                else:
                    # Parse JSON output for issues
                    try:
                        issues = json.loads(result.stdout)
                        return {"available": True, "passed": False, "issues": issues}
                    except json.JSONDecodeError:
                        # Fallback to text parsing
                        return {"available": True, "passed": False, "issues": [result.stdout]}
                        
            finally:
                # Clean up temporary file
                os.unlink(temp_file)
                
        except subprocess.TimeoutExpired:
            return {"available": True, "error": "ansible-lint timeout"}
        except Exception as e:
            return {"available": False, "error": f"Error running ansible-lint: {e}"}
    
    def _build_graph(self) -> StateGraph:
        """Build the simple workflow graph"""
        workflow = StateGraph(SimpleWorkflowState)
        
        # Add nodes for each extraction step
        workflow.add_node("extract_action", self.extract_action)
        workflow.add_node("extract_target", self.extract_target)
        workflow.add_node("extract_parameters", self.extract_parameters)
        workflow.add_node("generate_task_name", self.generate_task_name)
        workflow.add_node("assemble_playbook", self.assemble_playbook)
        workflow.add_node("validate_playbook", self.validate_playbook)
        workflow.add_node("annotate_playbook", self.annotate_playbook)
        workflow.add_node("finalize", self.finalize_output)
        
        # Add sequential edges
        workflow.add_edge("extract_action", "extract_target")
        workflow.add_edge("extract_target", "extract_parameters")
        workflow.add_edge("extract_parameters", "generate_task_name")
        workflow.add_edge("generate_task_name", "assemble_playbook")
        workflow.add_edge("assemble_playbook", "validate_playbook")
        workflow.add_edge("validate_playbook", "annotate_playbook")
        workflow.add_edge("annotate_playbook", "finalize")
        workflow.add_edge("finalize", END)
        
        # Set entry point
        workflow.set_entry_point("extract_action")
        
        return workflow.compile(checkpointer=MemorySaver())
    
    async def extract_action(self, state: SimpleWorkflowState) -> SimpleWorkflowState:
        """Step 1: Extract action type"""
        logger.info(f"Step 1: Extracting action type for {state['finding'].get('rule_id')}")
        
        try:
            prompt = self._format_prompt(
                'extract_action',
                title=state['finding'].get('title', ''),
                description=state['finding'].get('description', ''),
                fix_text=state['finding'].get('fix_text', '')
            )
            
            json_data = await self._llm_call_with_json_validation(
                prompt=prompt,
                expected_keys=['action_type'],
                max_tokens=50
            )
            
            action_type = json_data.get('action_type', 'other')
            state['action_type'] = action_type
            state['metadata']['step1_complete'] = datetime.now().isoformat()
            
            logger.info(f"Extracted action type: {action_type}")
            
        except Exception as e:
            error_msg = f"Error extracting action type: {e}"
            logger.error(error_msg)
            state['errors'].append(error_msg)
            state['action_type'] = "other"
            
        return state
    
    async def extract_target(self, state: SimpleWorkflowState) -> SimpleWorkflowState:
        """Step 2: Extract target name"""
        logger.info("Step 2: Extracting target name")
        
        try:
            prompt = self._format_prompt(
                'extract_target',
                title=state['finding'].get('title', ''),
                fix_text=state['finding'].get('fix_text', ''),
                action_type=state.get('action_type', 'other')
            )
            
            json_data = await self._llm_call_with_json_validation(
                prompt=prompt,
                expected_keys=['target'],
                max_tokens=50
            )
            
            target = json_data.get('target', 'unknown')
            state['target'] = target
            state['metadata']['step2_complete'] = datetime.now().isoformat()
            
            logger.info(f"Extracted target: {target}")
            
        except Exception as e:
            error_msg = f"Error extracting target: {e}"
            logger.error(error_msg)
            state['errors'].append(error_msg)
            state['target'] = "unknown"
            
        return state
    
    async def extract_parameters(self, state: SimpleWorkflowState) -> SimpleWorkflowState:
        """Step 3: Extract parameters"""
        logger.info("Step 3: Extracting parameters")
        
        try:
            prompt = self._format_prompt(
                'extract_parameters',
                title=state['finding'].get('title', ''),
                fix_text=state['finding'].get('fix_text', ''),
                action_type=state.get('action_type', 'other'),
                target=state.get('target', 'unknown')
            )
            
            json_data = await self._llm_call_with_json_validation(
                prompt=prompt,
                expected_keys=['parameter'],
                max_tokens=50
            )
            
            parameters = json_data.get('parameter', 'default')
            state['parameters'] = parameters
            state['metadata']['step3_complete'] = datetime.now().isoformat()
            
            logger.info(f"Extracted parameters: {parameters}")
            
        except Exception as e:
            error_msg = f"Error extracting parameters: {e}"
            logger.error(error_msg)
            state['errors'].append(error_msg)
            state['parameters'] = "default"
            
        return state
    
    async def generate_task_name(self, state: SimpleWorkflowState) -> SimpleWorkflowState:
        """Step 4: Generate task name"""
        logger.info("Step 4: Generating task name")
        
        try:
            prompt = self._format_prompt(
                'generate_task_name',
                rule_id=state['finding'].get('rule_id', ''),
                action_type=state.get('action_type', 'other'),
                target=state.get('target', 'unknown'),
                severity=state['finding'].get('severity', 'medium')
            )
            
            json_data = await self._llm_call_with_json_validation(
                prompt=prompt,
                expected_keys=['task_name'],
                max_tokens=100
            )
            
            task_name = json_data.get('task_name', f"STIG Task: {state.get('target', 'unknown')}")
            state['task_name'] = task_name
            state['metadata']['step4_complete'] = datetime.now().isoformat()
            
            logger.info(f"Generated task name: {task_name}")
            
        except Exception as e:
            error_msg = f"Error generating task name: {e}"
            logger.error(error_msg)
            state['errors'].append(error_msg)
            state['task_name'] = f"STIG Task: {state.get('target', 'unknown')}"
            
        return state
    
    async def assemble_playbook(self, state: SimpleWorkflowState) -> SimpleWorkflowState:
        """Step 5: Assemble final playbook"""
        logger.info("Step 5: Assembling final playbook")
        
        try:
            # Load the template for reference
            template_path = "examples/ansible_playbook_template.yaml"
            template_content = ""
            try:
                with open(template_path, 'r') as f:
                    template_content = f.read()
            except Exception as e:
                logger.warning(f"Could not load template for assembly: {e}")
            
            prompt = self._format_prompt(
                'assemble_playbook',
                task_name=state.get('task_name', 'STIG Task'),
                action_type=state.get('action_type', 'other'),
                target=state.get('target', 'unknown'),
                parameters=state.get('parameters', 'default'),
                rule_id=state['finding'].get('rule_id', ''),
                severity=state['finding'].get('severity', 'medium'),
                template_content=template_content
            )
            
            # Call LLM with JSON validation
            json_data = await self._llm_call_with_json_validation(
                prompt=prompt,
                expected_keys=['playbook'],
                max_tokens=500
            )
            
            # Extract playbook from JSON response
            playbook = json_data.get('playbook', '')
            
            # Remove markdown formatting
            if playbook.startswith('```yaml'):
                playbook = playbook[7:]
            if playbook.endswith('```'):
                playbook = playbook[:-3]
            
            # Split by document separator and take first valid one
            documents = playbook.split('---')
            best_doc = None
            
            for doc in documents:
                doc = doc.strip()
                if doc and 'name:' in doc and 'hosts:' in doc and 'tasks:' in doc:
                    # Found a valid-looking playbook
                    best_doc = '---\n' + doc
                    break
            
            if best_doc:
                playbook = best_doc
            else:
                # Fallback: take everything up to first explanatory text
                lines = playbook.split('\n')
                yaml_lines = []
                for line in lines:
                    if (line.strip().startswith('Output') or line.strip().startswith('Note:') or 
                        line.strip().startswith('```') or line.strip().startswith('Task name:') or
                        line.strip().startswith('Target:') or line.strip().startswith('Severity:') or
                        line.strip().startswith('Category:') or line.strip().startswith('STIG ID:') or
                        line.strip().startswith('Description:')):
                        break
                    yaml_lines.append(line)
                playbook = '\n'.join(yaml_lines).strip()
            
            # Ensure it starts with document separator
            if not playbook.startswith('---'):
                playbook = '---\n' + playbook
            
            # Fix any missing quotes in names
            import re
            playbook = re.sub(r'name: "([^"]*)"([^"])', r'name: "\1"\2', playbook)
            playbook = re.sub(r'name: "([^"]*)"$', r'name: "\1"', playbook, flags=re.MULTILINE)
            
            state['final_playbook'] = playbook
            state['metadata']['step5_complete'] = datetime.now().isoformat()
            
            logger.info("Assembled final playbook")
            
        except Exception as e:
            error_msg = f"Error assembling playbook: {e}"
            logger.error(error_msg)
            state['errors'].append(error_msg)
            # Create fallback playbook
            state['final_playbook'] = self._create_fallback_playbook(state)
            
        return state
    
    def _create_fallback_playbook(self, state: SimpleWorkflowState) -> str:
        """Create a basic fallback playbook"""
        rule_id = state['finding'].get('rule_id', 'unknown')
        action = state.get('action_type', 'other')
        target = state.get('target', 'unknown')
        severity = state['finding'].get('severity', 'medium')
        
        return f"""---
- name: "STIG {severity.upper()}: {action} {target}"
  hosts: all
  become: true
  vars:
    stig_enabled: true
  
  tasks:
    - name: "Manual remediation required for {rule_id}"
      debug:
        msg: "Please manually address: {action} {target}"
      tags:
        - stig
        - security
        - {severity.lower()}
        - manual_review
"""
    
    async def validate_playbook(self, state: SimpleWorkflowState) -> SimpleWorkflowState:
        """Step 6: Validate and potentially fix the generated playbook"""
        logger.info("Step 6: Validating and fixing playbook syntax and structure")
        
        if not state.get('final_playbook'):
            state['errors'].append("No playbook available for validation")
            return state
        
        try:
            # First, run ansible-lint if available
            lint_result = self._run_ansible_lint(state['final_playbook'])
            logger.info(f"ansible-lint available: {lint_result.get('available', False)}")
            
            # Load the template for comparison
            template_path = "examples/ansible_playbook_template.yaml"
            template_content = ""
            try:
                with open(template_path, 'r') as f:
                    template_content = f.read()
            except Exception as e:
                logger.warning(f"Could not load template: {e}")
            
            # Use the enhanced validation/fix prompt
            prompt = self._format_prompt(
                'validate_and_fix_playbook',
                playbook_content=state['final_playbook'],
                template_content=template_content
            )
            
            json_data = await self._llm_call_with_json_validation(
                prompt=prompt,
                expected_keys=['is_valid', 'issues_found', 'fixes_applied', 'fixed_playbook', 'suggestions'],
                max_tokens=800
            )
            
            validation_result = {
                'is_valid': json_data.get('is_valid', False),
                'issues_found': json_data.get('issues_found', []),
                'fixes_applied': json_data.get('fixes_applied', []),
                'fixed_playbook': json_data.get('fixed_playbook', ''),
                'suggestions': json_data.get('suggestions', []),
                'ansible_lint': lint_result
            }
            
            # If fixes were applied, update the playbook
            if validation_result['fixes_applied'] and validation_result['fixed_playbook']:
                logger.info(f"Applied {len(validation_result['fixes_applied'])} fixes to playbook")
                state['final_playbook'] = validation_result['fixed_playbook']
                
                # Re-run ansible-lint on the fixed playbook
                if lint_result.get('available'):
                    fixed_lint_result = self._run_ansible_lint(state['final_playbook'])
                    validation_result['ansible_lint_after_fix'] = fixed_lint_result
                    logger.info(f"ansible-lint after fix: {fixed_lint_result.get('passed', False)}")
            
            state['validation_result'] = validation_result
            state['metadata']['step6_complete'] = datetime.now().isoformat()
            
            logger.info(f"Validation complete - Valid: {validation_result['is_valid']}, Issues: {len(validation_result['issues_found'])}, Fixes: {len(validation_result['fixes_applied'])}")
            
            # Add validation issues to errors if playbook is still invalid
            if not validation_result['is_valid']:
                for issue in validation_result['issues_found']:
                    state['errors'].append(f"Validation: {issue}")
            
        except Exception as e:
            error_msg = f"Error validating playbook: {e}"
            logger.error(error_msg)
            state['errors'].append(error_msg)
            state['validation_result'] = {
                'is_valid': False,
                'issues_found': ['Validation process failed'],
                'fixes_applied': [],
                'fixed_playbook': '',
                'suggestions': [],
                'ansible_lint': {'available': False, 'error': str(e)}
            }
            
        return state
    
    async def annotate_playbook(self, state: SimpleWorkflowState) -> SimpleWorkflowState:
        """Step 7: Add comprehensive documentation to the playbook"""
        logger.info("Step 7: Adding comprehensive documentation to playbook")
        
        if not state.get('final_playbook'):
            state['errors'].append("No playbook available for annotation")
            return state
        
        try:
            # Use the final playbook (potentially fixed) for annotation
            playbook_to_annotate = state['final_playbook']
            
            # Extract finding information
            finding = state['finding']
            
            prompt = self._format_prompt(
                'annotate_playbook',
                playbook_content=playbook_to_annotate,
                rule_id=finding.get('rule_id', ''),
                title=finding.get('title', ''),
                severity=finding.get('severity', ''),
                description=finding.get('description', ''),
                check_text=finding.get('check_text', ''),
                fix_text=finding.get('fix_text', ''),
                references=', '.join(finding.get('references', []))
            )
            
            json_data = await self._llm_call_with_json_validation(
                prompt=prompt,
                expected_keys=['annotated_playbook'],
                max_tokens=600
            )
            
            annotated_playbook = json_data.get('annotated_playbook', '')
            
            if annotated_playbook:
                state['annotated_playbook'] = annotated_playbook
                logger.info("Successfully added comprehensive documentation to playbook")
            else:
                logger.warning("No annotated playbook received, keeping original")
                state['annotated_playbook'] = playbook_to_annotate
            
            state['metadata']['step7_complete'] = datetime.now().isoformat()
            
        except Exception as e:
            error_msg = f"Error annotating playbook: {e}"
            logger.error(error_msg)
            state['errors'].append(error_msg)
            # Fall back to the original playbook
            state['annotated_playbook'] = state.get('final_playbook', '')
            
        return state
    
    async def finalize_output(self, state: SimpleWorkflowState) -> SimpleWorkflowState:
        """Finalize workflow output"""
        logger.info("Finalizing workflow output")
        
        state['metadata']['workflow_complete'] = datetime.now().isoformat()
        state['metadata']['total_errors'] = len(state['errors'])
        
        # Determine final quality based on validation results
        if state.get('final_playbook') and len(state['errors']) == 0:
            validation = state.get('validation_result', {})
            if validation.get('is_valid', False):
                state['metadata']['final_quality'] = 'high'
            else:
                state['metadata']['final_quality'] = 'medium'
        elif state.get('final_playbook'):
            state['metadata']['final_quality'] = 'low'
        else:
            state['metadata']['final_quality'] = 'failed'
            
        return state
    
    def _save_outputs(self, finding: Dict[str, Any], final_state: SimpleWorkflowState) -> Dict[str, str]:
        """Save final outputs"""
        rule_id = finding.get('rule_id', 'unknown')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create playbooks directory
        playbooks_dir = Path("playbooks")
        playbooks_dir.mkdir(exist_ok=True)
        
        # Save playbook (use annotated version if available)
        playbook_file = playbooks_dir / f"{rule_id}_{timestamp}.yml"
        with open(playbook_file, 'w') as f:
            if final_state.get('annotated_playbook'):
                f.write(final_state['annotated_playbook'])
            elif final_state.get('final_playbook'):
                f.write(final_state['final_playbook'])
            else:
                f.write(self._create_fallback_playbook(final_state))
        
        # Save transparency report
        transparency_file = playbooks_dir / f"{rule_id}_{timestamp}_simple_transparency.md"
        with open(transparency_file, 'w') as f:
            f.write("# Simple Workflow Transparency Report\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\\n")
            f.write(f"**Rule ID:** {rule_id}\\n")
            f.write(f"**Final Quality:** {final_state['metadata'].get('final_quality', 'unknown')}\\n")
            f.write(f"**Workflow:** Simple 5-Step Extraction\\n\\n")
            
            # Extraction steps
            f.write("## Extraction Steps\\n\\n")
            f.write(f"1. **Action Type:** {final_state.get('action_type', 'N/A')}\\n")
            f.write(f"2. **Target:** {final_state.get('target', 'N/A')}\\n")
            f.write(f"3. **Parameters:** {final_state.get('parameters', 'N/A')}\\n")
            f.write(f"4. **Task Name:** {final_state.get('task_name', 'N/A')}\\n")
            f.write(f"5. **Final Playbook:** {'Generated' if final_state.get('final_playbook') else 'Failed'}\\n")
            
            # Validation results
            validation = final_state.get('validation_result', {})
            f.write(f"6. **Validation:** {'✅ Valid' if validation.get('is_valid', False) else '❌ Invalid'}\\n")
            
            if validation.get('fixes_applied'):
                f.write(f"   **Fixes Applied:** {len(validation['fixes_applied'])}\\n")
            
            # ansible-lint results
            lint_result = validation.get('ansible_lint', {})
            if lint_result.get('available'):
                f.write(f"   **ansible-lint:** {'✅ Passed' if lint_result.get('passed', False) else '❌ Failed'}\\n")
            else:
                f.write(f"   **ansible-lint:** Not available\\n")
            
            f.write("\\n")
            
            if validation.get('issues_found'):
                f.write("### Issues Found\\n")
                for issue in validation['issues_found']:
                    f.write(f"- {issue}\\n")
                f.write("\\n")
            
            if validation.get('fixes_applied'):
                f.write("### Fixes Applied\\n")
                for fix in validation['fixes_applied']:
                    f.write(f"- {fix}\\n")
                f.write("\\n")
            
            if validation.get('suggestions'):
                f.write("### Improvement Suggestions\\n")
                for suggestion in validation['suggestions']:
                    f.write(f"- {suggestion}\\n")
                f.write("\\n")
            
            # ansible-lint details
            if lint_result.get('available') and not lint_result.get('passed', True):
                f.write("### ansible-lint Issues\\n")
                issues = lint_result.get('issues', [])
                if isinstance(issues, list):
                    for issue in issues:
                        if isinstance(issue, dict):
                            f.write(f"- {issue.get('message', 'Unknown issue')}\\n")
                        else:
                            f.write(f"- {issue}\\n")
                f.write("\\n")
            
            # Errors
            if final_state.get('errors'):
                f.write("## Errors\\n\\n")
                for i, error in enumerate(final_state['errors'], 1):
                    f.write(f"{i}. {error}\\n")
        
        return {
            'playbook_file': str(playbook_file),
            'transparency_file': str(transparency_file),
            'quality': final_state['metadata'].get('final_quality', 'unknown')
        }
    
    async def process_finding(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single finding through the simple workflow"""
        initial_state = SimpleWorkflowState(
            finding=finding,
            action_type=None,
            target=None,
            parameters=None,
            task_name=None,
            final_playbook=None,
            validation_result=None,
            errors=[],
            metadata={
                'workflow_start': datetime.now().isoformat(),
                'rule_id': finding.get('rule_id', 'unknown')
            }
        )
        
        try:
            # Run workflow
            thread_id = str(uuid.uuid4())
            config = {"configurable": {"thread_id": thread_id}}
            final_state = await self.graph.ainvoke(initial_state, config=config)
            
            # Save outputs
            file_info = self._save_outputs(finding, final_state)
            
            return {
                'rule_id': finding.get('rule_id'),
                'success': len(final_state['errors']) == 0,
                'errors': final_state['errors'],
                'metadata': final_state['metadata'],
                'files': file_info,
                'components': {
                    'action_type': final_state.get('action_type'),
                    'target': final_state.get('target'),
                    'parameters': final_state.get('parameters'),
                    'task_name': final_state.get('task_name')
                },
                'playbook': final_state.get('final_playbook'),
                'validation_result': final_state.get('validation_result')
            }
            
        except Exception as e:
            logger.error(f"Simple workflow failed for {finding.get('rule_id')}: {e}")
            return {
                'rule_id': finding.get('rule_id'),
                'success': False,
                'errors': [str(e)],
                'playbook': self._create_fallback_playbook(initial_state)
            }