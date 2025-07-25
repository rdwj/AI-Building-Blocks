#!/usr/bin/env python3
"""
Test script for STIG classification prompts and other prompt engineering.

This script allows testing of classification prompts with real STIG findings
from the notebook to debug and improve prompt engineering.
"""

import sys
import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add src to path
sys.path.insert(0, 'src')

# Import our modules
from llm_interface import LLMInterface
from shared.prompt_utils import (
    load_prompt, format_prompt, llm_call_with_json, 
    display_prompt, display_result
)

# Sample STIG findings from the notebook for testing
SAMPLE_FINDINGS = [
    {
        "rule_id": "xccdf_org.ssgproject.content_rule_prefer_64bit_os",
        "severity": "medium",
        "title": "Prefer to use a 64-bit Operating System when supported",
        "description": "Prefer installation of 64-bit operating systems when the CPU supports it. Prefer installation of 64-bit operating systems when the CPU supports it.",
        "fix_text": ""  # Empty fix text
    },
    {
        "rule_id": "xccdf_org.ssgproject.content_rule_disable_prelink",
        "severity": "medium", 
        "title": "Disable Prelinking",
        "description": "The prelinking feature changes binaries in an attempt to decrease their startup time. In order to disable prelinking, the PRELINKING parameter in /etc/sysconfig/prelink must be set to no.",
        "fix_text": "# prelink not installed if test -e /etc/sysconfig/prelink -o -e /usr/sbin/prelink; then if grep -q ^PRELINKING /etc/sysconfig/prelink then sed -i 's/^PRELINKING[:blank:]*=[:blank:]*[:alpha:]*/PRELINKING=no/' /etc/sysconfig/prelink else echo 'PRELINKING=no' >> /etc/sysconfig/prelink fi fi"
    },
    {
        "rule_id": "xccdf_org.ssgproject.content_rule_rpm_verify_hashes",
        "severity": "high",
        "title": "Verify File Hashes with RPM",
        "description": "Without cryptographic integrity protections, system command and configuration files can be altered by unauthorized users without detection. Cryptographic mechanisms used for protecting the integrity of information include, for example, signed hash functions using asymmetric cryptography enabling distribution of the public key to verify the hash information while maintaining the confidentiality of the secret key used to generate the hash.",
        "fix_text": "The RPM package management system can check the hashes of files for packages it has installed. Run the following command to list which files on the system have hashes that differ from what is expected by the RPM database: $ sudo rpm -Va --noconfig | grep '^..5' Files with altered hashes are displayed. If the file was not expected to be modified, investigate the cause of the change."
    },
    {
        "rule_id": "xccdf_org.ssgproject.content_rule_rpm_verify_ownership",
        "severity": "high",
        "title": "Verify and Correct Ownership with RPM",
        "description": "Discretionary access control is weakened if a user has access to a file and can make copies of it available to others. This check verifies that files are owned by the correct user and group.",
        "fix_text": "The RPM package management system can check ownership of files and directories. Run the following command to list which files on the system have ownership different from what is expected by the RPM database: $ sudo rpm -Va --noconfig | grep '^.....U' Files with incorrect ownership are displayed. If the file was not expected to be modified, investigate the cause of the change."
    },
    {
        "rule_id": "xccdf_org.ssgproject.content_rule_rpm_verify_permissions",
        "severity": "high",
        "title": "Verify and Correct File Permissions with RPM",
        "description": "Discretionary access control is weakened if a user has access to a file and can make copies of it available to others. This check verifies that files have the correct permissions.",
        "fix_text": "The RPM package management system can check file permissions of files and directories. Run the following command to list which files on the system have permissions different from what is expected by the RPM database: $ sudo rpm -Va --noconfig | grep '^.M' Files with incorrect permissions are displayed. If the file was not expected to be modified, investigate the cause of the change."
    }
]

class PromptTester:
    def __init__(self):
        self.llm = None
        self.results = []
        
    async def initialize_llm(self):
        """Initialize LLM interface"""
        try:
            self.llm = LLMInterface()
            print(f"✅ LLM initialized successfully")
            print(f"   Model: {self.llm.model_name}")
            print(f"   API URL: {self.llm.api_url}")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize LLM: {e}")
            return False
    
    async def test_classification_prompt(self, prompt_name: str = 'prompt_1_classification', 
                                       findings: List[Dict] = None,
                                       show_prompts: bool = False) -> List[Dict]:
        """Test classification prompt with sample findings"""
        
        if not self.llm:
            print("❌ LLM not initialized")
            return []
            
        if findings is None:
            findings = SAMPLE_FINDINGS
            
        print(f"\n🎯 Testing {prompt_name}")
        print("=" * 50)
        
        try:
            # Load the prompt
            classification_prompt = load_prompt(prompt_name)
            print(f"📄 Loaded prompt: {classification_prompt['name']}")
            print(f"🌡️ Temperature: {classification_prompt['parameters']['temperature']}")
            print(f"🎯 Max tokens: {classification_prompt['parameters']['max_tokens']}")
            
        except Exception as e:
            print(f"❌ Error loading prompt: {e}")
            return []
        
        results = []
        
        for i, finding in enumerate(findings):
            print(f"\n{'='*60}")
            print(f"🔍 Testing Finding {i+1}/{len(findings)}")
            print(f"📋 Rule ID: {finding['rule_id']}")
            print(f"📝 Title: {finding['title'][:80]}...")
            print(f"🔧 Fix text length: {len(finding['fix_text'])} chars")
            
            try:
                # Format the prompt
                formatted_prompt = format_prompt(
                    classification_prompt,
                    rule_id=finding['rule_id'],
                    title=finding['title'],
                    description=finding['description'],
                    fix_text=finding['fix_text'][:2000]  # Limit length
                )
                
                if show_prompts:
                    print(f"\\n📋 Formatted Prompt:")
                    print("-" * 40)
                    print(formatted_prompt[:500] + "..." if len(formatted_prompt) > 500 else formatted_prompt)
                    print("-" * 40)
                
                # Make the LLM call
                result = await llm_call_with_json(
                    self.llm,
                    formatted_prompt,
                    ['category'],
                    max_retries=3,
                    prompt_params=classification_prompt['parameters']
                )
                
                # Store result
                test_result = {
                    'finding_index': i,
                    'rule_id': finding['rule_id'],
                    'title': finding['title'],
                    'classification': result.get('category', 'UNKNOWN'),
                    'raw_result': result,
                    'success': result.get('category') is not None,
                    'expected_categories': ['SHELL_SCRIPT', 'PACKAGE_VERIFICATION', 'CONFIG_MODIFICATION', 
                                          'BOOT_CONFIGURATION', 'MULTI_STEP_PROCESS', 'CRON_SCHEDULING', 'UNKNOWN']
                }
                
                results.append(test_result)
                
                # Display result
                category = result.get('category', 'UNKNOWN')
                is_valid = category in test_result['expected_categories']
                status = "✅" if is_valid else "❌"
                
                print(f"{status} Classification: {category}")
                if not is_valid:
                    print(f"   ⚠️ Invalid category! Expected one of: {test_result['expected_categories']}")
                    
            except Exception as e:
                print(f"❌ Error processing finding: {e}")
                results.append({
                    'finding_index': i,
                    'rule_id': finding['rule_id'],
                    'title': finding['title'],
                    'classification': 'ERROR',
                    'raw_result': {'error': str(e)},
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def analyze_results(self, results: List[Dict]) -> Dict:
        """Analyze classification results"""
        if not results:
            return {}
            
        total = len(results)
        successful = sum(1 for r in results if r['success'])
        valid_categories = sum(1 for r in results if r['success'] and 
                             r['classification'] in r.get('expected_categories', []))
        
        category_counts = {}
        for result in results:
            cat = result['classification']
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        analysis = {
            'total_tests': total,
            'successful_calls': successful,
            'valid_categories': valid_categories,
            'success_rate': successful / total * 100 if total > 0 else 0,
            'valid_category_rate': valid_categories / total * 100 if total > 0 else 0,
            'category_distribution': category_counts
        }
        
        return analysis
    
    def print_analysis(self, analysis: Dict):
        """Print analysis results"""
        print(f"\n📊 ANALYSIS RESULTS")
        print("=" * 30)
        print(f"Total tests: {analysis['total_tests']}")
        print(f"Successful LLM calls: {analysis['successful_calls']}")
        print(f"Valid categories: {analysis['valid_categories']}")
        print(f"Success rate: {analysis['success_rate']:.1f}%")
        print(f"Valid category rate: {analysis['valid_category_rate']:.1f}%")
        
        print(f"\\n📈 Category Distribution:")
        for category, count in sorted(analysis['category_distribution'].items()):
            print(f"   {category}: {count}")
    
    async def test_processing_prompt(self, prompt_name: str, finding: Dict, 
                                   expected_keys: List[str] = None) -> Dict:
        """Test a processing prompt with a single finding"""
        
        if not self.llm:
            print("❌ LLM not initialized")
            return {}
        
        if expected_keys is None:
            expected_keys = ['target_type', 'target_name', 'ansible_module', 'ansible_params']
        
        print(f"\n🔄 Testing processing prompt: {prompt_name}")
        print(f"📋 Finding: {finding['rule_id']}")
        
        try:
            # Load the prompt
            processing_prompt = load_prompt(prompt_name)
            print(f"📄 Loaded prompt: {processing_prompt['name']}")
            
            # Format the prompt
            formatted_prompt = format_prompt(
                processing_prompt,
                rule_id=finding['rule_id'],
                title=finding['title'],
                description=finding['description'],
                fix_text=finding['fix_text'][:3000]
            )
            
            # Make the LLM call
            result = await llm_call_with_json(
                self.llm,
                formatted_prompt,
                expected_keys,
                max_retries=3,
                prompt_params=processing_prompt['parameters']
            )
            
            # Analyze result
            has_required_keys = all(key in result for key in expected_keys)
            
            test_result = {
                'prompt_name': prompt_name,
                'finding_id': finding['rule_id'],
                'result': result,
                'expected_keys': expected_keys,
                'has_required_keys': has_required_keys,
                'missing_keys': [key for key in expected_keys if key not in result],
                'success': has_required_keys
            }
            
            status = "✅" if has_required_keys else "❌"
            print(f"{status} Processing result:")
            print(f"   Target type: {result.get('target_type', 'Missing')}")
            print(f"   Ansible module: {result.get('ansible_module', 'Missing')}")
            if not has_required_keys:
                print(f"   Missing keys: {test_result['missing_keys']}")
            
            return test_result
            
        except Exception as e:
            print(f"❌ Error testing processing prompt: {e}")
            return {
                'prompt_name': prompt_name,
                'finding_id': finding['rule_id'],
                'error': str(e),
                'success': False
            }
    
    def save_results(self, results: List[Dict], filename: str = None):
        """Save test results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"prompt_test_results_{timestamp}.json"
        
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'analysis': self.analyze_results(results)
        }
        
        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"💾 Results saved to: {filename}")

async def main():
    """Main test function"""
    tester = PromptTester()
    
    # Initialize LLM
    if not await tester.initialize_llm():
        return
    
    print("🚀 Starting prompt testing...")
    
    # Test classification prompt
    print("\\n" + "="*60)
    print("TESTING CLASSIFICATION PROMPT")
    print("="*60)
    
    results = await tester.test_classification_prompt(
        prompt_name='prompt_1_classification',
        findings=SAMPLE_FINDINGS,
        show_prompts=True  # Set to True to see formatted prompts
    )
    
    # Analyze results
    analysis = tester.analyze_results(results)
    tester.print_analysis(analysis)
    
    # Save results
    tester.save_results(results)
    
    # Test specific processing prompts if needed
    print("\\n" + "="*60)
    print("TESTING PROCESSING PROMPTS")
    print("="*60)
    
    # Test fallback prompt with one finding
    fallback_result = await tester.test_processing_prompt(
        'prompt_8_fallback',
        SAMPLE_FINDINGS[1]  # Test with prelink finding
    )
    
    print("\\n🎉 Testing complete!")
    print("Check the saved results file for detailed analysis.")

if __name__ == "__main__":
    asyncio.run(main())