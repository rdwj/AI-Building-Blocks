#!/usr/bin/env python3
"""
Test script for LangGraph workflow implementation
Tests the multi-step STIG to Ansible conversion process
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Configuration for testing - same as main script
MAX_CONCURRENT_REQUESTS = 1  # Keep low for testing on smaller GPU

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
from llm_interface import LLMInterface
from langgraph_workflow import STIGToAnsibleWorkflow


def save_test_results(test_finding, result, workflow_state=None):
    """Save test results to files for inspection"""
    # Create test output directory
    test_dir = Path("test_output")
    test_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save the original finding
    finding_file = test_dir / f"test_finding_{timestamp}.json"
    with open(finding_file, 'w') as f:
        json.dump(test_finding, f, indent=2)
    
    # Save the workflow result
    result_file = test_dir / f"test_result_{timestamp}.json"
    with open(result_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    # Save the final YAML task
    if result.get('task'):
        yaml_file = test_dir / f"test_task_{timestamp}.yml"
        with open(yaml_file, 'w') as f:
            f.write("---\n")
            f.write(f"# Test run: {timestamp}\n")
            f.write(f"# Finding: {test_finding['rule_id']}\n")
            f.write(f"# Success: {result['success']}\n")
            f.write(f"# Quality: {result.get('quality', 'unknown')}\n")
            f.write("\n")
            f.write(result['task'])
    
    # Save the complete workflow state if available
    if workflow_state:
        state_file = test_dir / f"test_workflow_state_{timestamp}.json"
        with open(state_file, 'w') as f:
            json.dump(workflow_state, f, indent=2)
    
    print(f"\n💾 Test results saved to {test_dir}:")
    print(f"   Original finding: {finding_file}")
    print(f"   Workflow result: {result_file}")
    if result.get('task'):
        print(f"   Final YAML task: {yaml_file}")
    if workflow_state:
        print(f"   Complete workflow state: {state_file}")
    
    return test_dir

async def test_single_finding_detailed():
    """Test the workflow with a single STIG finding and save detailed results"""
    
    # Sample STIG finding with good detail
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
    
    print("🧪 Testing LangGraph Workflow - Detailed Analysis")
    print("=" * 70)
    print(f"Test Finding: {test_finding['rule_id']}")
    print(f"Severity: {test_finding['severity']}")
    print(f"Title: {test_finding['title']}")
    print("-" * 70)
    
    # Initialize workflow
    load_dotenv()
    llm = LLMInterface()
    workflow = STIGToAnsibleWorkflow(llm)
    
    # Process the finding and capture detailed state
    try:
        print("\n⚙️  Processing through workflow steps...")
        print("   Step 1: Analyzing finding and extracting requirements...")
        
        # We'll need to modify the workflow to capture intermediate states
        # For now, let's run it and capture what we can
        result = await workflow.process_finding(test_finding)
        
        print(f"\n✅ Workflow completed!")
        print(f"Success: {result['success']}")
        print(f"Quality: {result.get('quality', 'unknown')}")
        
        if result.get('errors'):
            print(f"\n⚠️  Errors encountered:")
            for error in result['errors']:
                print(f"  - {error}")
        
        print(f"\n📊 Metadata:")
        for key, value in result.get('metadata', {}).items():
            print(f"  {key}: {value}")
        
        if result.get('task'):
            print(f"\n📄 Generated Ansible Task:")
            print("-" * 70)
            print(result['task'])
            print("-" * 70)
            
        # Show workflow steps information
        if result.get('workflow_state'):
            print(f"\n🔍 Workflow Step Analysis:")
            ws = result['workflow_state']
            
            # Step 1: Requirements
            if ws.get('requirements'):
                print("\n   Step 1 - Requirements Extraction: ✅")
                print(f"     Action Type: {ws['requirements'].get('action_type', 'unknown')}")
                print(f"     Target: {ws['requirements'].get('target_name', 'unknown')}")
            else:
                print("\n   Step 1 - Requirements Extraction: ❌")
                
            # Step 2: Basic Task
            if ws.get('ansible_task'):
                print("\n   Step 2 - Basic Task Generation: ✅")
                print(f"     Task length: {len(ws['ansible_task'])} characters")
            else:
                print("\n   Step 2 - Basic Task Generation: ❌")
                
            # Step 3: Enhanced Task
            if ws.get('enhanced_task'):
                print("\n   Step 3 - Task Enhancement: ✅")
                print(f"     Enhanced task length: {len(ws['enhanced_task'])} characters")
            else:
                print("\n   Step 3 - Task Enhancement: ❌")
                
            # Step 4: Documentation
            if ws.get('documented_task'):
                print("\n   Step 4 - Documentation: ✅")
                print(f"     Final task length: {len(ws['documented_task'])} characters")
            else:
                print("\n   Step 4 - Documentation: ❌")
                
        # If debug info available, show it
        if result.get('debug'):
            print(f"\n🔍 Debug Information:")
            if result['debug'].get('requirements'):
                print("\nStep 1 - Extracted Requirements:")
                print(json.dumps(result['debug']['requirements'], indent=2))
                
        # Save detailed results
        print(f"\n💾 Saving detailed test results...")
        workflow_state = result.get('workflow_state')
        test_dir = save_test_results(test_finding, result, workflow_state)
        
        # Show the new output files
        if result.get('files'):
            print(f"\n📁 Final Output Files:")
            print(f"   Clean Playbook: {result['files']['playbook_file']}")
            print(f"   AI Transparency: {result['files']['transparency_file']}")
            print(f"   Task Quality: {result['files']['task_quality']}")
        
        # Also save a human-readable summary
        summary_file = test_dir / f"test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(summary_file, 'w') as f:
            f.write("STIG to Ansible Workflow Test Summary\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Finding: {test_finding['rule_id']}\n")
            f.write(f"Title: {test_finding['title']}\n")
            f.write(f"Severity: {test_finding['severity']}\n")
            f.write(f"Success: {result['success']}\n")
            f.write(f"Quality: {result.get('quality', 'unknown')}\n\n")
            
            if result.get('errors'):
                f.write("Errors:\n")
                for error in result['errors']:
                    f.write(f"  - {error}\n")
                f.write("\n")
            
            f.write("Metadata:\n")
            for key, value in result.get('metadata', {}).items():
                f.write(f"  {key}: {value}\n")
            f.write("\n")
            
            if result.get('task'):
                f.write("Generated Ansible Task:\n")
                f.write("-" * 40 + "\n")
                f.write(result['task'])
                f.write("\n" + "-" * 40 + "\n")
        
        print(f"   Test summary: {summary_file}")
        
        return result['success']
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_multiple_findings():
    """Test the workflow with multiple STIG findings"""
    
    test_findings = [
        {
            "rule_id": "xccdf_org.ssgproject.content_rule_package_prelink_removed",
            "severity": "medium",
            "title": "Remove prelink Package",
            "description": "The prelink package contains the prelink program which modifies ELF shared libraries and executables.",
            "fix_text": "The prelink package can be removed with: sudo yum erase prelink",
            "status": "fail"
        },
        {
            "rule_id": "xccdf_org.ssgproject.content_rule_sshd_disable_root_login",
            "severity": "medium",
            "title": "Disable SSH Root Login",
            "description": "The root user should never be allowed to login directly over SSH.",
            "fix_text": "To disable root login via SSH, add or correct the following line in /etc/ssh/sshd_config: PermitRootLogin no",
            "status": "fail"
        },
        {
            "rule_id": "xccdf_org.ssgproject.content_rule_file_permissions_etc_passwd",
            "severity": "high",
            "title": "Set Permissions on /etc/passwd File",
            "description": "The /etc/passwd file contains user account information.",
            "fix_text": "To properly set the permissions of /etc/passwd, run: chmod 0644 /etc/passwd",
            "status": "fail"
        }
    ]
    
    print("\n\n🧪 Testing Multiple Findings")
    print("=" * 60)
    
    # Initialize workflow
    load_dotenv()
    llm = LLMInterface()
    workflow = STIGToAnsibleWorkflow(llm)
    
    # Use semaphore to control concurrency just like the main script
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    async def process_with_semaphore(finding):
        async with semaphore:
            return await workflow.process_finding(finding)
    
    results = []
    print(f"\n⚙️  Processing {len(test_findings)} findings with concurrency limit: {MAX_CONCURRENT_REQUESTS}")
    
    # Process all findings with controlled concurrency
    tasks = [process_with_semaphore(finding) for finding in test_findings]
    results = await asyncio.gather(*tasks)
    
    # Print results
    for finding, result in zip(test_findings, results):
        print(f"\n📋 {finding['rule_id']}")
        print(f"   Status: {'✅' if result['success'] else '❌'}")
        print(f"   Quality: {result.get('quality', 'unknown')}")
        if result.get('errors'):
            print(f"   Errors: {', '.join(result['errors'])}")
            
    # Summary
    print(f"\n📊 Summary:")
    print(f"Total findings: {len(test_findings)}")
    print(f"Successful: {sum(1 for r in results if r['success'])}")
    print(f"Failed: {sum(1 for r in results if not r['success'])}")
    
    # Quality breakdown
    quality_counts = {}
    for r in results:
        q = r.get('quality', 'unknown')
        quality_counts[q] = quality_counts.get(q, 0) + 1
    
    print(f"\nQuality breakdown:")
    for quality, count in quality_counts.items():
        print(f"  {quality}: {count}")


async def main():
    """Main test function"""
    print("🚀 LangGraph Workflow Test Suite")
    print("=" * 80)
    
    # Test single finding with detailed output
    success = await test_single_finding_detailed()
    
    if success:
        print("\n🎯 Single finding test successful!")
        
        # Ask if user wants to run multiple findings test
        print("\n" + "=" * 80)
        print("Single finding test completed successfully.")
        print("Multiple findings test available but not running automatically.")
        print("You can uncomment the call below to run it.")
        print("=" * 80)
        
        # Uncomment the line below to run multiple findings test
        # await test_multiple_findings()
    else:
        print("\n⚠️  Single finding test failed")
        
    print("\n✅ Test suite completed!")


if __name__ == "__main__":
    # Enable debug logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Also enable debug for our specific logger
    logger = logging.getLogger('langgraph_workflow')
    logger.setLevel(logging.DEBUG)
    
    asyncio.run(main())