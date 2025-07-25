#!/usr/bin/env python3
"""
Enhanced STIG to Ansible Playbook Generator using LangGraph workflow.
This version uses a multi-step workflow for higher quality output.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import hashlib

import yaml
from dotenv import load_dotenv

# Import configuration
from config import (
    MAX_CONCURRENT_REQUESTS, BATCH_SIZE, INTER_BATCH_DELAY,
    OUTPUT_BASE_DIR, PRESERVE_FAILED_OUTPUTS, ENABLE_DEBUG_OUTPUT,
    MAX_FINDINGS_PER_RUN
)

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from stig_parser_enhanced import STIGParser
from llm_interface import LLMInterface
from langgraph_workflow import STIGToAnsibleWorkflow


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PlaybookGeneratorLangGraph:
    """Enhanced generator using LangGraph workflow"""
    
    def __init__(self):
        load_dotenv()
        self.llm = LLMInterface()
        self.workflow = STIGToAnsibleWorkflow(self.llm)
        self.parser = STIGParser()
        
    def create_run_directory(self, input_filename: str) -> Path:
        """Create hierarchical output directory structure"""
        # Clean filename for directory name
        base_name = Path(input_filename).stem
        # Truncate if too long and create hash for uniqueness
        if len(base_name) > 50:
            name_hash = hashlib.md5(base_name.encode()).hexdigest()[:8]
            base_name = f"{base_name[:50]}_{name_hash}"
            
        # Create timestamp ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_id = f"{timestamp}_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:6]}"
        
        # Create directory structure
        output_dir = Path(OUTPUT_BASE_DIR) / base_name / run_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (output_dir / "individual_tasks").mkdir(exist_ok=True)
        
        # Create/update latest symlink
        latest_link = Path(OUTPUT_BASE_DIR) / base_name / "latest"
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        latest_link.symlink_to(run_id)
        
        logger.info(f"Created output directory: {output_dir}")
        return output_dir
    
    def save_run_metadata(self, output_dir: Path, metadata: Dict[str, Any]):
        """Save run metadata"""
        metadata_file = output_dir / "run_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def save_workflow_log(self, output_dir: Path, results: List[Dict[str, Any]]):
        """Save detailed workflow log"""
        log_file = output_dir / "workflow_log.txt"
        with open(log_file, 'w') as f:
            f.write("STIG to Ansible Workflow Log\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")
            
            # Configuration info
            f.write("Configuration:\n")
            f.write(f"  Max Concurrent Requests: {MAX_CONCURRENT_REQUESTS}\n")
            f.write(f"  Batch Size: {BATCH_SIZE}\n")
            f.write(f"  Inter-batch Delay: {INTER_BATCH_DELAY}s\n\n")
            
            # Summary statistics
            total = len(results)
            successful = sum(1 for r in results if r['success'])
            by_quality = {}
            for r in results:
                quality = r.get('quality', 'unknown')
                by_quality[quality] = by_quality.get(quality, 0) + 1
                
            f.write(f"Total findings processed: {total}\n")
            f.write(f"Successful: {successful} ({successful/total*100:.1f}%)\n")
            f.write(f"Failed: {total - successful}\n\n")
            
            f.write("Output quality breakdown:\n")
            for quality, count in sorted(by_quality.items()):
                f.write(f"  {quality}: {count}\n")
            f.write("\n" + "=" * 80 + "\n\n")
            
            # Detailed results
            for result in results:
                f.write(f"Rule ID: {result['rule_id']}\n")
                f.write(f"Success: {result['success']}\n")
                f.write(f"Quality: {result.get('quality', 'unknown')}\n")
                if result.get('errors'):
                    f.write(f"Errors: {', '.join(result['errors'])}\n")
                f.write("-" * 40 + "\n\n")
    
    async def process_findings_batch(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process findings in batches with controlled concurrency"""
        results = []
        total = len(findings)
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        
        async def process_with_semaphore(finding):
            """Process a single finding with semaphore control"""
            async with semaphore:
                return await self.workflow.process_finding(finding)
        
        # Process in batches
        for i in range(0, total, BATCH_SIZE):
            batch = findings[i:i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1
            total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
            
            logger.info(f"Processing batch {batch_num}/{total_batches} "
                       f"({i+1}-{min(i+BATCH_SIZE, total)} of {total}) "
                       f"[concurrency: {MAX_CONCURRENT_REQUESTS}]")
            
            # Process batch with controlled concurrency
            batch_tasks = [
                process_with_semaphore(finding) 
                for finding in batch
            ]
            batch_results = await asyncio.gather(*batch_tasks)
            results.extend(batch_results)
            
            # Log batch completion
            successful_in_batch = sum(1 for r in batch_results if r['success'])
            logger.info(f"Batch {batch_num} completed: {successful_in_batch}/{len(batch)} successful")
            
            # Delay between batches to avoid overwhelming the GPU
            if i + BATCH_SIZE < total:
                logger.debug(f"Waiting {INTER_BATCH_DELAY}s before next batch...")
                await asyncio.sleep(INTER_BATCH_DELAY)
                
        return results
    
    def save_individual_tasks(self, output_dir: Path, results: List[Dict[str, Any]]):
        """Save individual task files"""
        tasks_dir = output_dir / "individual_tasks"
        
        for result in results:
            if result.get('task'):
                rule_id = result['rule_id']
                filename = f"{rule_id}_task.yml"
                filepath = tasks_dir / filename
                
                # Add header comment with metadata
                content = f"---\n# Generated: {datetime.now().isoformat()}\n"
                content += f"# Quality: {result.get('quality', 'unknown')}\n"
                content += f"# Success: {result['success']}\n"
                if result.get('errors'):
                    content += f"# Errors: {', '.join(result['errors'])}\n"
                content += "\n"
                content += result['task']
                
                with open(filepath, 'w') as f:
                    f.write(content)
    
    def create_master_playbook(self, output_dir: Path, results: List[Dict[str, Any]]):
        """Create master playbook that includes all tasks"""
        playbook = {
            'name': 'STIG Compliance Playbook',
            'hosts': 'all',
            'become': True,
            'gather_facts': True,
            'vars': {
                'stig_compliance_mode': True,
                'generated_date': datetime.now().isoformat()
            },
            'tasks': []
        }
        
        # Add tasks sorted by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'unknown': 4}
        sorted_results = sorted(
            results,
            key=lambda r: (
                severity_order.get(r.get('metadata', {}).get('severity', 'unknown'), 4),
                r['rule_id']
            )
        )
        
        for result in sorted_results:
            if result.get('task') and result['success']:
                # Parse the task YAML
                try:
                    task_data = yaml.safe_load(result['task'])
                    if isinstance(task_data, list):
                        playbook['tasks'].extend(task_data)
                    else:
                        playbook['tasks'].append(task_data)
                except yaml.YAMLError:
                    logger.error(f"Failed to parse task for {result['rule_id']}")
        
        # Save master playbook
        master_file = output_dir / "master_playbook.yml"
        with open(master_file, 'w') as f:
            yaml.dump(playbook, f, default_flow_style=False, sort_keys=False)
            
        logger.info(f"Created master playbook with {len(playbook['tasks'])} tasks")
    
    async def generate_playbooks(self, stig_file: str):
        """Main entry point for playbook generation"""
        logger.info(f"Starting enhanced playbook generation for: {stig_file}")
        
        # Log configuration
        logger.info(f"Configuration: max_concurrent={MAX_CONCURRENT_REQUESTS}, "
                   f"batch_size={BATCH_SIZE}, delay={INTER_BATCH_DELAY}s")
        
        # Create output directory
        output_dir = self.create_run_directory(stig_file)
        
        # Initialize metadata
        metadata = {
            'input_file': stig_file,
            'start_time': datetime.now().isoformat(),
            'workflow_version': '2.0',
            'using_langgraph': True,
            'concurrency_settings': {
                'max_concurrent_requests': MAX_CONCURRENT_REQUESTS,
                'batch_size': BATCH_SIZE,
                'inter_batch_delay': INTER_BATCH_DELAY
            }
        }
        
        try:
            # Parse STIG file or JSON file
            logger.info("Parsing STIG file...")
            
            if stig_file.endswith('.json'):
                # Handle JSON file directly
                import json
                with open(stig_file, 'r') as f:
                    data = json.load(f)
                findings_dict = data.get('findings', [])
                logger.info(f"Loaded {len(findings_dict)} findings from JSON file")
            else:
                # Handle XML file with parser
                findings = self.parser.parse_stig_file(stig_file)
                
                if not findings:
                    logger.warning("No findings extracted from STIG file")
                    return
                    
                logger.info(f"Found {len(findings)} STIG findings")
                
                # Convert findings to dict format
                findings_dict = []
                for f in findings:
                    if hasattr(f, 'to_dict'):
                        findings_dict.append(f.to_dict())
                    else:
                        # Convert dataclass to dict
                        findings_dict.append({
                            'rule_id': f.rule_id,
                            'severity': f.severity,
                            'title': f.title,
                            'description': f.description,
                            'check_text': f.check_text,
                            'fix_text': f.fix_text,
                            'status': f.status,
                            'references': f.references,
                            'group_id': getattr(f, 'group_id', None),
                            'version': getattr(f, 'version', None),
                            'weight': getattr(f, 'weight', None)
                        })
            
            metadata['total_findings'] = len(findings_dict)
            
            # Apply MAX_FINDINGS_PER_RUN limit
            if len(findings_dict) > MAX_FINDINGS_PER_RUN:
                logger.info(f"Limiting processing to {MAX_FINDINGS_PER_RUN} findings (out of {len(findings_dict)} total)")
                metadata['original_findings_count'] = len(findings_dict)
                findings_dict = findings_dict[:MAX_FINDINGS_PER_RUN]
                metadata['findings_limited'] = True
            
            # Process through workflow
            logger.info("Processing findings through LangGraph workflow...")
            results = await self.process_findings_batch(findings_dict)
            
            # Calculate statistics
            successful = sum(1 for r in results if r['success'])
            metadata['successful_tasks'] = successful
            metadata['success_rate'] = successful / len(results) * 100
            
            # Save outputs
            logger.info("Saving results...")
            self.save_individual_tasks(output_dir, results)
            self.create_master_playbook(output_dir, results)
            self.save_workflow_log(output_dir, results)
            
            # Finalize metadata
            metadata['end_time'] = datetime.now().isoformat()
            metadata['output_directory'] = str(output_dir)
            self.save_run_metadata(output_dir, metadata)
            
            # Print summary
            print(f"\n{'='*60}")
            print(f"Playbook Generation Complete!")
            print(f"{'='*60}")
            print(f"Total findings: {len(findings)}")
            print(f"Successful tasks: {successful} ({metadata['success_rate']:.1f}%)")
            print(f"Output directory: {output_dir}")
            print(f"Master playbook: {output_dir / 'master_playbook.yml'}")
            print(f"\nTo access the latest run:")
            print(f"  cd {output_dir.parent / 'latest'}")
            
        except Exception as e:
            logger.error(f"Error generating playbooks: {e}")
            metadata['error'] = str(e)
            metadata['end_time'] = datetime.now().isoformat()
            self.save_run_metadata(output_dir, metadata)
            raise


async def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: python generate_playbooks_langgraph.py <stig_file.xml>")
        sys.exit(1)
        
    stig_file = sys.argv[1]
    if not os.path.exists(stig_file):
        print(f"Error: File not found: {stig_file}")
        sys.exit(1)
        
    generator = PlaybookGeneratorLangGraph()
    await generator.generate_playbooks(stig_file)


if __name__ == "__main__":
    asyncio.run(main())