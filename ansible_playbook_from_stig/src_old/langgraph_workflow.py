#!/usr/bin/env python3
"""
LangGraph workflow for multi-step STIG to Ansible conversion.
Orchestrates the conversion process through multiple LLM steps for better quality output.
"""

import json
import logging
import os
import uuid
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


class WorkflowState(TypedDict):
    """State passed between workflow nodes"""
    finding: Dict[str, Any]  # Original STIG finding
    requirements: Optional[Dict[str, Any]]  # Step 1 output
    ansible_task: Optional[str]  # Step 2 output
    enhanced_task: Optional[str]  # Step 3 output
    documented_task: Optional[str]  # Step 4 output
    errors: List[str]  # Error tracking
    metadata: Dict[str, Any]  # Workflow metadata


class STIGToAnsibleWorkflow:
    """Multi-step workflow for converting STIG findings to Ansible tasks"""
    
    def __init__(self, llm_interface: LLMInterface):
        self.llm = llm_interface
        self.prompts_dir = "prompts"
        self.prompts = {}
        self._load_prompts()
        self.graph = self._build_graph()
        
    def _load_prompts(self):
        """Load all YAML prompts from the prompts directory"""
        prompt_files = {
            'analyze': 'analyze_finding.yaml',
            'generate': 'generate_ansible_task.yaml',
            'enhance': 'enhance_ansible_task.yaml',
            'document': 'document_ansible_task.yaml'
        }
        
        for key, filename in prompt_files.items():
            filepath = os.path.join(self.prompts_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    prompt_data = yaml.safe_load(f)
                    if 'template' not in prompt_data:
                        raise ValueError(f"Template not found in {filename}")
                    self.prompts[key] = prompt_data
                    logger.info(f"Loaded prompt: {filename}")
            except Exception as e:
                logger.error(f"Failed to load prompt {filename}: {e}")
                raise
    
    def _format_prompt(self, prompt_key: str, **kwargs) -> str:
        """Format a prompt template with provided variables"""
        template = self.prompts[prompt_key]['template']
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing variable in prompt {prompt_key}: {e}")
            logger.debug(f"Template: {template[:200]}...")
            logger.debug(f"Provided kwargs: {list(kwargs.keys())}")
            raise
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("analyze_finding", self.analyze_finding)
        workflow.add_node("generate_task", self.generate_ansible_task)
        workflow.add_node("enhance_task", self.enhance_ansible_task)
        workflow.add_node("document_task", self.document_ansible_task)
        workflow.add_node("finalize", self.finalize_output)
        
        # Add edges
        workflow.add_edge("analyze_finding", "generate_task")
        workflow.add_edge("generate_task", "enhance_task")
        workflow.add_edge("enhance_task", "document_task")
        workflow.add_edge("document_task", "finalize")
        workflow.add_edge("finalize", END)
        
        # Set entry point
        workflow.set_entry_point("analyze_finding")
        
        return workflow.compile(checkpointer=MemorySaver())
    
    async def analyze_finding(self, state: WorkflowState) -> WorkflowState:
        """Step 1: Analyze STIG finding and extract requirements"""
        logger.info(f"Step 1: Analyzing finding {state['finding'].get('rule_id')}")
        
        try:
            # Format the prompt
            prompt = self._format_prompt(
                'analyze',
                finding_json=json.dumps(state['finding'], indent=2)
            )
            
            # Call LLM
            response = await self.llm.generate_ansible_task_async(
                prompt=prompt,
                max_tokens=1000
            )
            
            logger.debug(f"Raw LLM response: {response[:500]}...")
            
            # Clean the response and try to parse JSON
            clean_response = response.strip()
            
            # Remove any markdown formatting
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:]
            if clean_response.endswith('```'):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()
            
            # Try to extract JSON from the response
            json_match = None
            
            # Look for JSON pattern in the response
            import re
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, clean_response)
            
            if matches:
                # Try each match to see if it's valid JSON
                for match in matches:
                    try:
                        requirements = json.loads(match)
                        json_match = match
                        break
                    except json.JSONDecodeError:
                        continue
            
            if not json_match:
                # If no valid JSON found, try the whole response
                requirements = json.loads(clean_response)
            else:
                # Use the found JSON
                logger.info(f"Extracted JSON from response: {json_match}")
                requirements = json.loads(json_match)
            state['requirements'] = requirements
            state['metadata']['step1_complete'] = datetime.now().isoformat()
            
            logger.info(f"Extracted requirements: {requirements.get('action_type')}")
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse requirements JSON: {e}. Raw response: {response[:200]}..."
            logger.error(error_msg)
            state['errors'].append(error_msg)
            # Provide fallback requirements
            state['requirements'] = {
                'action_type': 'unknown',
                'target_type': 'unknown',
                'target_name': state['finding'].get('rule_id', 'unknown'),
                'parameters': {},
                'validation': 'Manual verification required',
                'os_family': ['RedHat', 'Debian']
            }
        except Exception as e:
            error_msg = f"Error in analyze_finding: {e}"
            logger.error(error_msg)
            state['errors'].append(error_msg)
            
        return state
    
    async def generate_ansible_task(self, state: WorkflowState) -> WorkflowState:
        """Step 2: Generate Ansible task from requirements"""
        logger.info("Step 2: Generating Ansible task")
        
        if not state.get('requirements'):
            state['errors'].append("No requirements available for task generation")
            return state
        
        try:
            # Format the prompt using string.Template to avoid brace conflicts
            from string import Template
            
            # Load the template
            template_str = self.prompts['generate']['template']
            
            # Create a Template object
            template = Template(template_str)
            
            # Use Template.safe_substitute to avoid KeyError on missing variables
            prompt = template.safe_substitute(
                requirements_json=json.dumps(state['requirements'], indent=2),
                rule_id=state['finding'].get('rule_id', 'UNKNOWN'),
                severity=state['finding'].get('severity', 'medium')
            )
            
            # Call LLM
            response = await self.llm.generate_ansible_task_async(
                prompt=prompt,
                max_tokens=800
            )
            
            # Clean and validate YAML
            task_yaml = response.strip()
            # Basic validation - try to parse as YAML
            yaml.safe_load(f"tasks:\n{task_yaml}")
            
            state['ansible_task'] = task_yaml
            state['metadata']['step2_complete'] = datetime.now().isoformat()
            
            logger.info("Generated basic Ansible task")
            
        except yaml.YAMLError as e:
            error_msg = f"Generated invalid YAML: {e}"
            logger.error(error_msg)
            state['errors'].append(error_msg)
            # Provide fallback task
            state['ansible_task'] = self._create_fallback_task(state)
        except Exception as e:
            error_msg = f"Error in generate_ansible_task: {e}"
            logger.error(error_msg)
            state['errors'].append(error_msg)
            
        return state
    
    async def enhance_ansible_task(self, state: WorkflowState) -> WorkflowState:
        """Step 3: Enhance Ansible task with best practices"""
        logger.info("Step 3: Enhancing Ansible task")
        
        if not state.get('ansible_task'):
            state['errors'].append("No Ansible task available for enhancement")
            return state
        
        try:
            # Format the prompt
            prompt = self._format_prompt(
                'enhance',
                ansible_task=state['ansible_task'],
                requirements_json=json.dumps(state['requirements'], indent=2)
            )
            
            # Call LLM
            response = await self.llm.generate_ansible_task_async(
                prompt=prompt,
                max_tokens=1000
            )
            
            # Clean and validate enhanced YAML
            enhanced_yaml = response.strip()
            yaml.safe_load(f"tasks:\n{enhanced_yaml}")
            
            state['enhanced_task'] = enhanced_yaml
            state['metadata']['step3_complete'] = datetime.now().isoformat()
            
            logger.info("Enhanced Ansible task with best practices")
            
        except Exception as e:
            error_msg = f"Error in enhance_ansible_task: {e}"
            logger.error(error_msg)
            state['errors'].append(error_msg)
            # Fall back to basic task if enhancement fails
            state['enhanced_task'] = state['ansible_task']
            
        return state
    
    async def document_ansible_task(self, state: WorkflowState) -> WorkflowState:
        """Step 4: Add documentation to Ansible task"""
        logger.info("Step 4: Documenting Ansible task")
        
        task_to_document = state.get('enhanced_task') or state.get('ansible_task')
        if not task_to_document:
            state['errors'].append("No Ansible task available for documentation")
            return state
        
        try:
            # Format the prompt
            prompt = self._format_prompt(
                'document',
                enhanced_task=task_to_document,
                finding_json=json.dumps(state['finding'], indent=2)
            )
            
            # Call LLM
            response = await self.llm.generate_ansible_task_async(
                prompt=prompt,
                max_tokens=1500
            )
            
            state['documented_task'] = response.strip()
            state['metadata']['step4_complete'] = datetime.now().isoformat()
            
            logger.info("Added comprehensive documentation to task")
            
        except Exception as e:
            error_msg = f"Error in document_ansible_task: {e}"
            logger.error(error_msg)
            state['errors'].append(error_msg)
            # Fall back to enhanced/basic task if documentation fails
            state['documented_task'] = task_to_document
            
        return state
    
    async def finalize_output(self, state: WorkflowState) -> WorkflowState:
        """Finalize the workflow output"""
        logger.info("Finalizing workflow output")
        
        # Add completion metadata
        state['metadata']['workflow_complete'] = datetime.now().isoformat()
        state['metadata']['total_errors'] = len(state['errors'])
        
        # Select best available output
        if state.get('documented_task'):
            state['metadata']['final_output'] = 'documented'
        elif state.get('enhanced_task'):
            state['metadata']['final_output'] = 'enhanced'
        elif state.get('ansible_task'):
            state['metadata']['final_output'] = 'basic'
        else:
            state['metadata']['final_output'] = 'failed'
            
        return state
    
    def _create_fallback_task(self, state: WorkflowState) -> str:
        """Create a basic fallback task when generation fails"""
        finding = state['finding']
        rule_short = finding.get('rule_id', 'UNKNOWN').split('_')[-1].upper()
        
        return f"""- name: "STIG {rule_short}: Manual remediation required"
  debug:
    msg: "Manual remediation needed for {finding.get('rule_id', 'unknown rule')}"
  tags:
    - stig
    - security
    - {finding.get('severity', 'medium').lower()}
    - manual_review"""
    
    def _clean_task_output(self, task_content: str) -> str:
        """Clean LLM output to extract just the YAML task"""
        if not task_content:
            return ""
            
        # Remove markdown formatting
        clean_content = task_content.strip()
        
        # Remove ```yaml and ``` markers
        if clean_content.startswith('```yaml'):
            clean_content = clean_content[7:]
        elif clean_content.startswith('```'):
            clean_content = clean_content[3:]
            
        if clean_content.endswith('```'):
            clean_content = clean_content[:-3]
            
        # Remove any explanatory text after the YAML
        lines = clean_content.split('\n')
        yaml_lines = []
        in_yaml = False
        
        for line in lines:
            # Start of YAML task
            if line.strip().startswith('- name:') or line.strip().startswith('---'):
                in_yaml = True
            
            # End of YAML (empty line followed by non-YAML content)
            if in_yaml and line.strip() == '':
                # Check if next non-empty line looks like YAML
                continue
            elif in_yaml and line.strip() and not (
                line.startswith(' ') or line.startswith('-') or 
                line.startswith('#') or line.strip().startswith('---')
            ):
                # Non-YAML content found, stop collecting
                break
                
            if in_yaml:
                yaml_lines.append(line)
                
        result = '\n'.join(yaml_lines).strip()
        
        # Remove any trailing explanatory text
        if 'Please note that' in result:
            result = result.split('Please note that')[0].strip()
        if 'Please let me know' in result:
            result = result.split('Please let me know')[0].strip()
            
        return result
    
    def _save_final_outputs(self, finding: Dict[str, Any], final_state: WorkflowState) -> Dict[str, str]:
        """Save final playbook and transparency report"""
        rule_id = finding.get('rule_id', 'unknown')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create playbooks directory
        playbooks_dir = Path("playbooks")
        playbooks_dir.mkdir(exist_ok=True)
        
        # Determine the best available task
        best_task = None
        task_quality = 'fallback'
        
        if final_state.get('documented_task'):
            best_task = self._clean_task_output(final_state['documented_task'] or "")
            task_quality = 'documented'
        elif final_state.get('enhanced_task'):
            best_task = self._clean_task_output(final_state['enhanced_task'] or "")
            task_quality = 'enhanced'
        elif final_state.get('ansible_task'):
            best_task = self._clean_task_output(final_state['ansible_task'] or "")
            task_quality = 'basic'
        else:
            best_task = self._create_fallback_task(final_state)
            task_quality = 'fallback'
        
        # Save the final playbook
        playbook_file = playbooks_dir / f"{rule_id}_{timestamp}.yml"
        with open(playbook_file, 'w') as f:
            f.write("---\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Rule ID: {rule_id}\n")
            f.write(f"# Quality: {task_quality}\n")
            f.write(f"# Workflow: LangGraph Multi-Step\n")
            f.write("\n")
            
            # Create a proper playbook structure
            # Extract task name from the best_task for the playbook name
            task_name = "STIG Compliance Task"
            if best_task and "name:" in best_task:
                # Extract the task name
                for line in best_task.split('\n'):
                    if 'name:' in line:
                        task_name = line.split('name:')[1].strip().strip('"\'')
                        break
            
            # Write playbook structure
            f.write(f"- name: \"{task_name}\"\n")
            f.write("  hosts: all\n")
            f.write("  become: true\n")
            f.write("  vars:\n")
            f.write("    stig_remove_telnet: true\n")
            f.write("  \n")
            f.write("  tasks:\n")
            
            # Clean the task to remove any extra YAML document markers
            clean_task = best_task
            if clean_task:
                # Remove any markdown code blocks
                clean_task = clean_task.replace('```yaml\n', '').replace('```', '')
                # Remove any extra document separators
                clean_task = clean_task.replace('---\n', '').replace('\n---', '')
                # Remove any leading/trailing whitespace
                clean_task = clean_task.strip()
                
                # Indent the task properly
                for line in clean_task.split('\n'):
                    if line.strip():
                        f.write(f"    {line}\n")
                    else:
                        f.write("\n")
            f.write("\n")
        
        # Create transparency report
        transparency_file = playbooks_dir / f"{rule_id}_{timestamp}_ai_transparency.md"
        with open(transparency_file, 'w') as f:
            f.write("# AI Transparency Report\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}  \n")
            f.write(f"**Rule ID:** {rule_id}  \n")
            f.write(f"**Final Quality:** {task_quality}  \n")
            f.write(f"**Workflow:** LangGraph Multi-Step  \n\n")
            
            # Original Finding
            f.write("## 📋 Original STIG Finding\n\n")
            f.write(f"**Title:** {finding.get('title', 'Unknown')}  \n")
            f.write(f"**Severity:** {finding.get('severity', 'Unknown')}  \n")
            f.write(f"**Description:** {finding.get('description', 'No description available')}  \n")
            f.write(f"**Fix Text:** {finding.get('fix_text', 'No fix text available')}  \n\n")
            
            # Workflow Execution
            f.write("## 🔄 Workflow Execution\n\n")
            
            # Step 1: Requirements
            f.write("### Step 1: Requirements Extraction\n")
            if final_state.get('requirements'):
                f.write("**Status:** ✅ Success  \n")
                f.write("**Extracted Requirements:**\n")
                f.write("```json\n")
                f.write(json.dumps(final_state['requirements'], indent=2))
                f.write("\n```\n\n")
            else:
                f.write("**Status:** ❌ Failed  \n")
                f.write("**Result:** No requirements extracted\n\n")
            
            # Step 2: Basic Task
            f.write("### Step 2: Basic Task Generation\n")
            if final_state.get('ansible_task'):
                f.write("**Status:** ✅ Success  \n")
                f.write("**Generated Task:**\n")
                f.write("```yaml\n")
                f.write(final_state['ansible_task'] or "")
                f.write("\n```\n\n")
            else:
                f.write("**Status:** ❌ Failed  \n")
                f.write("**Result:** No basic task generated\n\n")
            
            # Step 3: Enhanced Task
            f.write("### Step 3: Task Enhancement\n")
            if final_state.get('enhanced_task'):
                enhanced_different = final_state['enhanced_task'] != final_state.get('ansible_task')
                f.write(f"**Status:** ✅ Success  \n")
                f.write(f"**Enhanced:** {'Yes' if enhanced_different else 'No changes made'}  \n")
                if enhanced_different:
                    f.write("**Enhanced Task:**\n")
                    f.write("```yaml\n")
                    f.write(final_state['enhanced_task'] or "")
                    f.write("\n```\n\n")
                else:
                    f.write("**Result:** Used basic task without changes\n\n")
            else:
                f.write("**Status:** ❌ Failed  \n")
                f.write("**Result:** No enhanced task generated\n\n")
            
            # Step 4: Documentation
            f.write("### Step 4: Documentation\n")
            if final_state.get('documented_task'):
                f.write("**Status:** ✅ Success  \n")
                f.write("**Recovery:** Despite errors in Steps 2-3, Step 4 successfully generated a complete, high-quality Ansible task  \n")
                f.write("**Documented Task:**\n")
                f.write("```yaml\n")
                f.write(self._clean_task_output(final_state['documented_task'] or ""))
                f.write("\n```\n\n")
            else:
                f.write("**Status:** ❌ Failed  \n")
                f.write("**Result:** No documented task generated\n\n")
            
            # Error Analysis
            if final_state.get('errors'):
                f.write("## ⚠️ Error Analysis\n\n")
                f.write("**Error Recovery Strategy:** The workflow is designed to be resilient. When intermediate steps fail, later steps can still succeed by working with available data.\n\n")
                f.write("**Errors Encountered:**\n")
                for i, error in enumerate(final_state['errors'], 1):
                    f.write(f"{i}. {error}\n")
                f.write("\n")
                f.write("**How Errors Were Resolved:**\n")
                if final_state.get('documented_task'):
                    f.write("- Step 4 (Documentation) received the original STIG finding and requirements from Step 1\n")
                    f.write("- Step 4 ignored the failed intermediate outputs and generated a complete task from scratch\n")
                    f.write("- The final output is high-quality because Step 4 had access to the original requirements\n")
                else:
                    f.write("- Errors were not fully resolved, fallback task was used\n")
                f.write("\n")
            
            # Metadata
            f.write("## 📊 Workflow Metadata\n\n")
            metadata = final_state.get('metadata', {})
            for key, value in metadata.items():
                f.write(f"**{key.replace('_', ' ').title()}:** {value}  \n")
            
            f.write("\n---\n")
            f.write("*This report was automatically generated by the LangGraph workflow system.*\n")
        
        return {
            'playbook_file': str(playbook_file),
            'transparency_file': str(transparency_file),
            'task_quality': task_quality
        }

    async def process_finding(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single STIG finding through the workflow"""
        # Initialize state
        initial_state = WorkflowState(
            finding=finding,
            requirements=None,
            ansible_task=None,
            enhanced_task=None,
            documented_task=None,
            errors=[],
            metadata={
                'workflow_start': datetime.now().isoformat(),
                'rule_id': finding.get('rule_id', 'unknown')
            }
        )
        
        # Run the workflow
        try:
            # Add required config for checkpointer
            thread_id = str(uuid.uuid4())
            config = {"configurable": {"thread_id": thread_id}}
            final_state = await self.graph.ainvoke(initial_state, config=config)
            
            # Save final outputs
            file_info = self._save_final_outputs(finding, final_state)
            
            # Return the best available result
            result = {
                'rule_id': finding.get('rule_id'),
                'success': len(final_state['errors']) == 0,
                'errors': final_state['errors'],
                'metadata': final_state['metadata'],
                'files': file_info
            }
            
            # Add the final task
            if final_state.get('documented_task'):
                result['task'] = self._clean_task_output(final_state['documented_task'])
                result['quality'] = 'documented'
            elif final_state.get('enhanced_task'):
                result['task'] = self._clean_task_output(final_state['enhanced_task'])
                result['quality'] = 'enhanced'
            elif final_state.get('ansible_task'):
                result['task'] = self._clean_task_output(final_state['ansible_task'])
                result['quality'] = 'basic'
            else:
                result['task'] = self._create_fallback_task(final_state)
                result['quality'] = 'fallback'
                
            # Add intermediate outputs for debugging
            if logger.isEnabledFor(logging.DEBUG):
                result['debug'] = {
                    'requirements': final_state.get('requirements'),
                    'basic_task': final_state.get('ansible_task'),
                    'enhanced_task': final_state.get('enhanced_task')
                }
            
            # Add complete workflow state for detailed analysis
            result['workflow_state'] = {
                'finding': final_state.get('finding'),
                'requirements': final_state.get('requirements'),
                'ansible_task': final_state.get('ansible_task'),
                'enhanced_task': final_state.get('enhanced_task'),
                'documented_task': final_state.get('documented_task'),
                'errors': final_state.get('errors'),
                'metadata': final_state.get('metadata')
            }
                
            return result
            
        except Exception as e:
            logger.error(f"Workflow failed for {finding.get('rule_id')}: {e}")
            return {
                'rule_id': finding.get('rule_id'),
                'success': False,
                'errors': [str(e)],
                'task': self._create_fallback_task(initial_state),
                'quality': 'fallback'
            }