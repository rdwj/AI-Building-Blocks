#!/usr/bin/env python3
"""
Test script for simple workflow optimized for small LLM models
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append('src')

from llm_interface import LLMInterface
from simple_workflow import SimpleSTIGWorkflow

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_simple_workflow():
    """Test the simple workflow with a sample finding"""
    
    # Sample finding
    sample_finding = {
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
    
    try:
        # Initialize workflow
        logger.info("Initializing simple workflow...")
        llm = LLMInterface()
        workflow = SimpleSTIGWorkflow(llm)
        
        # Process finding
        logger.info(f"Processing finding: {sample_finding['rule_id']}")
        result = await workflow.process_finding(sample_finding)
        
        # Print results
        logger.info("=== WORKFLOW RESULTS ===")
        logger.info(f"Rule ID: {result['rule_id']}")
        logger.info(f"Success: {result['success']}")
        logger.info(f"Errors: {len(result['errors'])}")
        
        if result.get('components'):
            logger.info("=== EXTRACTED COMPONENTS ===")
            components = result['components']
            logger.info(f"Action Type: {components.get('action_type')}")
            logger.info(f"Target: {components.get('target')}")
            logger.info(f"Parameters: {components.get('parameters')}")
            logger.info(f"Task Name: {components.get('task_name')}")
        
        if result.get('files'):
            logger.info("=== GENERATED FILES ===")
            files = result['files']
            logger.info(f"Playbook: {files.get('playbook_file')}")
            logger.info(f"Transparency: {files.get('transparency_file')}")
            logger.info(f"Quality: {files.get('quality')}")
        
        if result.get('playbook'):
            logger.info("=== FINAL PLAYBOOK ===")
            print(result['playbook'])
        
        if result.get('validation_result'):
            logger.info("=== VALIDATION RESULTS ===")
            validation = result['validation_result']
            logger.info(f"Valid: {validation.get('is_valid', False)}")
            logger.info(f"Fixes Applied: {len(validation.get('fixes_applied', []))}")
            
            # ansible-lint results
            lint_result = validation.get('ansible_lint', {})
            if lint_result.get('available'):
                logger.info(f"ansible-lint: {'✅ Passed' if lint_result.get('passed', False) else '❌ Failed'}")
            else:
                logger.info("ansible-lint: Not available")
            
            if validation.get('issues_found'):
                logger.warning("Issues Found:")
                for issue in validation['issues_found']:
                    logger.warning(f"  - {issue}")
            
            if validation.get('fixes_applied'):
                logger.info("Fixes Applied:")
                for fix in validation['fixes_applied']:
                    logger.info(f"  - {fix}")
            
            if validation.get('suggestions'):
                logger.info("Suggestions:")
                for suggestion in validation['suggestions']:
                    logger.info(f"  - {suggestion}")
        
        if result.get('errors'):
            logger.warning("=== ERRORS ===")
            for error in result['errors']:
                logger.warning(f"- {error}")
        
        return result
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_simple_workflow())