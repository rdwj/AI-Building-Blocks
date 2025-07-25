#!/usr/bin/env python3
"""
LLM Interface for STIG to Ansible Playbook Generation - Fixed for Proper Ansible YAML

Generates properly structured, valid Ansible tasks with strict formatting
"""

import os
import json
import requests
import re
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

class LLMInterface:
    """Interface for LLAMA model API calls with strict Ansible YAML generation"""
    
    def __init__(self, env_file=None):
        """Initialize LLM interface with configuration from .env"""
        
        # Load environment variables
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        self.api_url = os.getenv('GRANITE_3_3_8B_INSTRUCT_URL')
        self.api_key = os.getenv('GRANITE_3_3_8B_INSTRUCT_API_KEY') 
        self.model_name = os.getenv('GRANITE_3_3_8B_INSTRUCT_MODEL_NAME', 'granite-3-3-8b-instruct')
        self.timeout = int(os.getenv('LLM_REQUEST_TIMEOUT', '30'))
        
        # Validate configuration
        if not self.api_url or not self.api_key:
            raise ValueError("GRANITE_3_3_8B_INSTRUCT_URL and GRANITE_3_3_8B_INSTRUCT_API_KEY must be set in .env file")
        
        # Ensure URL has correct endpoint
        if not self.api_url.endswith('/v1/completions'):
            if '/v1/completions' not in self.api_url:
                self.api_url = self.api_url.rstrip('/') + '/v1/completions'
        
        # Prepare headers
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        print(f"🤖 LLM Interface initialized")
        print(f"   Model: {self.model_name}")
        print(f"   URL: {self.api_url}")
    
    def create_ansible_prompt(self, finding: Dict[str, Any]) -> str:
        """Create a very specific prompt for proper Ansible task generation"""
        
        rule_short = finding.get('rule_id', 'UNKNOWN').split('_')[-1].upper()
        
        prompt = f"""Create a single, valid Ansible task for this STIG finding. Follow the EXACT format below.

STIG FINDING:
Rule: {finding.get('rule_id', 'Unknown')}
Title: {finding.get('title', 'No title')}
Severity: {finding.get('severity', 'medium')}
Fix: {finding.get('fix_text', 'No fix available')[:300]}

REQUIRED OUTPUT FORMAT (copy this structure exactly):

- name: "STIG {rule_short}: [Specific action description]"
  [ansible_module]:
    [parameter]: [value]
    [parameter]: [value]
  become: true
  when: ansible_os_family == "RedHat"
  tags:
    - stig
    - security
    - {finding.get('severity', 'medium').lower()}

RULES:
1. Output ONLY the single task in the exact format above
2. Choose ONE appropriate Ansible module: package, file, lineinfile, service, systemd, mount, sysctl, command
3. Use realistic parameter values
4. NO duplicate tasks, NO repetition
5. NO markdown, NO explanations, NO extra text
6. Must be valid YAML that passes ansible-lint
7. Task name must be specific and actionable

EXAMPLE for package removal:
- name: "STIG PRELINK: Remove prelink package"
  package:
    name: prelink
    state: absent
  become: true
  when: ansible_os_family == "RedHat"
  tags:
    - stig
    - security
    - medium

OUTPUT ONLY THE TASK (no other text):"""
        
        return prompt
    
    def validate_ansible_structure(self, yaml_content: str) -> Dict[str, Any]:
        """Validate that the YAML has proper Ansible task structure"""
        
        try:
            import yaml
            
            # Parse YAML
            parsed = yaml.safe_load(yaml_content)
            
            # Check basic structure
            if not parsed:
                return {'valid': False, 'error': 'Empty YAML content'}
            
            # Should be a single task (dict) or list with one task
            if isinstance(parsed, list):
                if len(parsed) != 1:
                    return {'valid': False, 'error': f'Expected 1 task, got {len(parsed)}'}
                task = parsed[0]
            elif isinstance(parsed, dict):
                task = parsed
            else:
                return {'valid': False, 'error': 'Invalid YAML structure'}
            
            # Validate required task fields
            if 'name' not in task:
                return {'valid': False, 'error': 'Missing task name'}
            
            # Check for Ansible module (should have exactly one module)
            ansible_modules = ['package', 'file', 'lineinfile', 'service', 'systemd', 
                             'mount', 'sysctl', 'command', 'shell', 'copy', 'template']
            
            found_modules = [key for key in task.keys() if key in ansible_modules]
            
            if len(found_modules) != 1:
                return {'valid': False, 'error': f'Expected 1 Ansible module, found: {found_modules}'}
            
            # Check for proper task structure (no nested tasks)
            for key, value in task.items():
                if key == 'name':
                    continue
                if isinstance(value, list) and any(isinstance(item, dict) and 'name' in item for item in value):
                    return {'valid': False, 'error': 'Found nested tasks - invalid structure'}
            
            return {
                'valid': True, 
                'task': task, 
                'module': found_modules[0],
                'name': task['name']
            }
            
        except yaml.YAMLError as e:
            return {'valid': False, 'error': f'YAML parsing error: {e}'}
        except Exception as e:
            return {'valid': False, 'error': f'Validation error: {e}'}
    
    def extract_and_fix_yaml(self, content: str) -> str:
        """Extract and fix YAML from LLM response"""
        
        # Remove markdown code blocks
        if '```yaml' in content:
            yaml_blocks = re.findall(r'```yaml\s*(.*?)\s*```', content, re.DOTALL)
            if yaml_blocks:
                content = yaml_blocks[0].strip()
        elif '```yml' in content:
            yml_blocks = re.findall(r'```yml\s*(.*?)\s*```', content, re.DOTALL)
            if yml_blocks:
                content = yml_blocks[0].strip()
        elif '```' in content:
            code_blocks = re.findall(r'```[a-zA-Z]*\s*(.*?)\s*```', content, re.DOTALL)
            if code_blocks:
                content = code_blocks[0].strip()
        
        # Clean up the content line by line
        lines = content.split('\n')
        cleaned_lines = []
        task_started = False
        
        for line in lines:
            line_stripped = line.strip()
            
            # Skip explanatory text
            if any(phrase in line_stripped.lower() for phrase in [
                'here is', 'here\'s', 'this task', 'please note', 'example', 'rules:', 'output only'
            ]):
                continue
            
            # Skip extra YAML headers
            if line_stripped == '---' and task_started:
                continue
            
            # Detect task start
            if line_stripped.startswith('- name:'):
                task_started = True
                cleaned_lines.append(line)
            elif task_started:
                # Stop at explanatory text or new tasks
                if line_stripped.startswith('- name:') and len(cleaned_lines) > 1:
                    break  # Stop at second task
                if any(phrase in line_stripped.lower() for phrase in [
                    'note:', 'example:', 'output only', 'this will', 'make sure'
                ]):
                    break
                cleaned_lines.append(line)
            elif line_stripped.startswith('---'):
                cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines).strip()
        
        # Fix common YAML issues
        # Remove duplicate YAML headers
        if result.count('---') > 1:
            lines = result.split('\n')
            new_lines = []
            yaml_header_seen = False
            for line in lines:
                if line.strip() == '---':
                    if not yaml_header_seen:
                        new_lines.append(line)
                        yaml_header_seen = True
                else:
                    new_lines.append(line)
            result = '\n'.join(new_lines)
        
        return result
    
    def call_llm(self, prompt: str, max_tokens: int = 600) -> Dict[str, Any]:
        """Make API call to LLAMA model"""
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": 0.05  # Very low temperature for consistent structure
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle response format
                if 'choices' in result and result['choices']:
                    content = result['choices'][0].get('text', '').strip()
                    tokens_used = result.get('usage', {}).get('total_tokens', 0)
                elif 'response' in result:
                    content = result['response'].strip()
                    tokens_used = len(content.split())
                else:
                    content = str(result).strip()
                    tokens_used = len(content.split())
                
                return {
                    'success': True,
                    'content': content,
                    'tokens_used': tokens_used
                }
            else:
                error_msg = f"API returned status {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f": {error_detail}"
                except:
                    error_msg += f": {response.text}"
                    
                return {
                    'success': False,
                    'error': error_msg,
                    'content': ''
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"API call failed: {str(e)}",
                'content': ''
            }
    
    def generate_ansible_task(self, finding: Dict[str, Any], max_retries: int = 2) -> Dict[str, Any]:
        """Generate a properly structured Ansible task with validation and retries"""
        
        rule_id = finding.get('rule_id', 'Unknown')
        print(f"🎯 Generating Ansible task for {rule_id}")
        
        for attempt in range(max_retries + 1):
            if attempt > 0:
                print(f"   🔄 Retry attempt {attempt}")
            
            # Create prompt
            prompt = self.create_ansible_prompt(finding)
            
            # Call LLM
            result = self.call_llm(prompt)
            
            if not result['success']:
                print(f"   ❌ LLM call failed: {result['error']}")
                continue
            
            # Extract and clean YAML
            cleaned_yaml = self.extract_and_fix_yaml(result['content'])
            
            # Validate structure
            validation = self.validate_ansible_structure(cleaned_yaml)
            
            if validation['valid']:
                print(f"   ✅ Generated valid Ansible task: {validation['name']}")
                return {
                    'success': True,
                    'content': cleaned_yaml,
                    'yaml_valid': True,
                    'module_used': validation['module'],
                    'task_name': validation['name'],
                    'attempt': attempt + 1
                }
            else:
                print(f"   ⚠️  Validation failed (attempt {attempt + 1}): {validation['error']}")
                if attempt < max_retries:
                    continue
                else:
                    # Return the content anyway for debugging
                    return {
                        'success': True,
                        'content': cleaned_yaml,
                        'yaml_valid': False,
                        'validation_error': validation['error'],
                        'attempt': attempt + 1
                    }
        
        return {
            'success': False,
            'error': f"Failed to generate valid task after {max_retries + 1} attempts",
            'content': ''
        }
    
    async def generate_ansible_task_async(self, prompt: str, max_tokens: int = 500, max_retries: int = 3) -> str:
        """Generate response using async for custom prompts"""
        import aiohttp
        
        for attempt in range(max_retries):
            try:
                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "temperature": 0.3,
                    "max_tokens": max_tokens,
                    "top_p": 0.9,
                    "frequency_penalty": 0.5,
                    "presence_penalty": 0.3
                }
                
                # Debug: print payload (remove in production)
                # print(f"🔍 API Payload: {json.dumps(payload, indent=2)}")
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.api_url,
                        headers=self.headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            # print(f"🔍 API Response: {json.dumps(data, indent=2)}")
                            return data['choices'][0]['text'].strip()
                        else:
                            error_text = await response.text()
                            # print(f"❌ API Error: {response.status} - {error_text}")
                            if response.status == 429:  # Rate limit
                                wait_time = (attempt + 1) * 2
                                await asyncio.sleep(wait_time)
                                continue
                            raise Exception(f"API error: {response.status} - {error_text}")
                            
            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                    continue
                raise
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                    continue
                raise
                
        raise Exception(f"Failed after {max_retries} attempts")

def test_improved_generation():
    """Test the improved generation with strict validation"""
    
    test_finding = {
        'rule_id': 'xccdf_org.ssgproject.content_rule_package_prelink_removed',
        'severity': 'medium',
        'title': 'The prelink package should be removed',
        'description': 'The prelink package can be used to enhance performance by reducing startup time.',
        'fix_text': 'Remove the prelink package: yum remove prelink'
    }
    
    try:
        llm = LLMInterface()
        result = llm.generate_ansible_task(test_finding)
        
        print(f"\n📋 Test Result:")
        print(f"Success: {result['success']}")
        
        if result['success']:
            print(f"YAML Valid: {result.get('yaml_valid', 'Unknown')}")
            if result.get('yaml_valid'):
                print(f"Module Used: {result.get('module_used', 'Unknown')}")
                print(f"Task Name: {result.get('task_name', 'Unknown')}")
            else:
                print(f"Validation Error: {result.get('validation_error', 'Unknown')}")
            
            print(f"Generated Content:\n{result['content']}")
        else:
            print(f"Error: {result['error']}")
            
        return result['success'] and result.get('yaml_valid', False)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Improved Ansible Task Generation")
    print("=" * 50)
    
    success = test_improved_generation()
    
    if success:
        print("\n✅ Improved generation working with valid structure!")
    else:
        print("\n❌ Test failed - check the output above")
