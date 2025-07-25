#!/usr/bin/env python3
"""
STIG to Ansible Playbook Generator - Working Implementation

Usage: python generate_playbooks.py <stig_file.xml>
"""

import sys
import os
import json
import yaml
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from stig_parser_enhanced import STIGParser
    from llm_interface import LLMInterface
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all required modules are in the src/ directory")
    sys.exit(1)

class PlaybookGenerator:
    """Generates Ansible playbooks from STIG findings"""
    
    def __init__(self, env_file=None):
        """Initialize with LLM interface and output directories"""
        
        # Load environment
        load_dotenv(env_file)
        
        # Initialize components
        self.stig_parser = STIGParser()
        self.llm = LLMInterface(env_file)
        
        # Setup output directories
        self.output_dir = Path(os.getenv('OUTPUT_DIR', './playbooks'))
        self.findings_dir = Path(os.getenv('FINDINGS_DIR', './findings'))
        
        self.output_dir.mkdir(exist_ok=True)
        self.findings_dir.mkdir(exist_ok=True)
        
        self.max_findings = int(os.getenv('MAX_FINDINGS_PER_RUN', '50'))
        
        print(f"🎯 Playbook Generator initialized")
        print(f"   Output dir: {self.output_dir}")
        print(f"   Findings dir: {self.findings_dir}")
        print(f"   Max findings per run: {self.max_findings}")
    
    def process_stig_file(self, stig_file: str) -> dict:
        """Process STIG file and generate playbooks"""
        
        print(f"🚀 Processing STIG file: {stig_file}")
        
        # Step 1: Parse STIG file
        print("\n📋 Step 1: Parsing STIG file...")
        findings = self.stig_parser.parse_stig_file(stig_file)
        
        if not findings:
            return {
                'success': False,
                'error': 'No findings extracted from STIG file',
                'findings_count': 0
            }
        
        # Step 2: Export findings 
        print("\n💾 Step 2: Exporting findings...")
        findings_file = self.findings_dir / f"{Path(stig_file).stem}_findings.json"
        self.stig_parser.export_findings_json(str(findings_file))
        
        # Step 3: Filter findings for processing
        print("\n🎯 Step 3: Filtering findings...")
        failed_findings = self.stig_parser.get_failed_findings()
        
        if not failed_findings:
            print("   ℹ️  No failed findings found - processing all findings")
            process_findings = findings[:self.max_findings]
        else:
            print(f"   🎯 Found {len(failed_findings)} failed findings")
            process_findings = failed_findings[:self.max_findings]
        
        print(f"   📊 Will process {len(process_findings)} findings")
        
        # Step 4: Generate playbooks
        print("\n🤖 Step 4: Generating Ansible playbooks...")
        results = self._generate_playbooks_for_findings(process_findings, stig_file)
        
        # Step 5: Create summary
        summary = {
            'success': True,
            'stig_file': stig_file,
            'total_findings': len(findings),
            'failed_findings': len(failed_findings),
            'processed_findings': len(process_findings),
            'successful_generations': results['successful'],
            'failed_generations': results['failed'],
            'output_directory': str(self.output_dir),
            'findings_file': str(findings_file),
            'summary': self.stig_parser.get_findings_summary()
        }
        
        return summary
    
    def _generate_playbooks_for_findings(self, findings: list, stig_file: str) -> dict:
        """Generate Ansible playbooks for list of findings"""
        
        successful = 0
        failed = 0
        playbook_tasks = []
        
        for i, finding in enumerate(findings):
            print(f"\n   🎯 Processing finding {i+1}/{len(findings)}: {finding.rule_id}")
            
            try:
                # Generate Ansible task via LLM
                result = self.llm.generate_ansible_task({
                    'rule_id': finding.rule_id,
                    'severity': finding.severity,
                    'title': finding.title,
                    'description': finding.description,
                    'fix_text': finding.fix_text,
                    'status': finding.status
                })
                
                if result['success']:
                    # Save individual task file
                    task_file = self.output_dir / f"{finding.rule_id.replace(':', '_')}_task.yml"
                    
                    task_content = f"""---
# STIG Finding: {finding.rule_id}
# Severity: {finding.severity}
# Status: {finding.status}
# Title: {finding.title}

{result['content']}
"""
                    
                    with open(task_file, 'w') as f:
                        f.write(task_content)
                    
                    # Add to master playbook
                    playbook_tasks.append({
                        'rule_id': finding.rule_id,
                        'severity': finding.severity,
                        'task_file': str(task_file),
                        'yaml_content': result['content']
                    })
                    
                    successful += 1
                    print(f"      ✅ Generated: {task_file.name}")
                    
                else:
                    print(f"      ❌ Failed: {result['error']}")
                    failed += 1
                    
            except Exception as e:
                print(f"      ❌ Exception: {e}")
                failed += 1
        
        # Create master playbook
        if playbook_tasks:
            self._create_master_playbook(playbook_tasks, stig_file)
        
        return {
            'successful': successful,
            'failed': failed,
            'tasks': playbook_tasks
        }
    
    def _create_master_playbook(self, tasks: list, stig_file: str):
        """Create master playbook that includes all tasks"""
        
        playbook_name = f"{Path(stig_file).stem}_remediation_playbook.yml"
        playbook_path = self.output_dir / playbook_name
        
        # Group tasks by severity
        critical_tasks = [t for t in tasks if t['severity'].lower() == 'critical']
        high_tasks = [t for t in tasks if t['severity'].lower() == 'high']
        medium_tasks = [t for t in tasks if t['severity'].lower() == 'medium']
        other_tasks = [t for t in tasks if t['severity'].lower() not in ['critical', 'high', 'medium']]
        
        playbook_content = f"""---
# STIG Remediation Playbook
# Generated from: {Path(stig_file).name}
# Total tasks: {len(tasks)}
# Critical: {len(critical_tasks)}, High: {len(high_tasks)}, Medium: {len(medium_tasks)}

- name: "STIG Remediation for {Path(stig_file).stem}"
  hosts: all
  become: yes
  gather_facts: yes
  
  vars:
    stig_source_file: "{Path(stig_file).name}"
    generation_date: "{{{{ ansible_date_time.iso8601 }}}}"
  
  tasks:
    - name: "Display STIG remediation start message"
      debug:
        msg: "Starting STIG remediation for {{{{ stig_source_file }}}}"
"""
        
        # Add tasks by severity priority
        all_task_groups = [
            ("Critical Severity Tasks", critical_tasks),
            ("High Severity Tasks", high_tasks),
            ("Medium Severity Tasks", medium_tasks),
            ("Other Tasks", other_tasks)
        ]
        
        for group_name, group_tasks in all_task_groups:
            if group_tasks:
                playbook_content += f"\n\n    # {group_name}\n"
                for task in group_tasks:
                    playbook_content += f"\n    # {task['rule_id']}\n"
                    # Include the YAML content but ensure proper indentation
                    yaml_lines = task['yaml_content'].split('\n')
                    for line in yaml_lines:
                        if line.strip():
                            playbook_content += f"    {line}\n"
        
        # Add completion task
        playbook_content += """
    
    - name: "Display STIG remediation completion message"
      debug:
        msg: "STIG remediation completed. Please review and test all changes."
"""
        
        # Write master playbook
        with open(playbook_path, 'w') as f:
            f.write(playbook_content)
        
        print(f"\n📝 Created master playbook: {playbook_name}")
        print(f"   📊 Total tasks: {len(tasks)}")
        print(f"   🔴 Critical: {len(critical_tasks)}")
        print(f"   🟠 High: {len(high_tasks)}")
        print(f"   🟡 Medium: {len(medium_tasks)}")

def main():
    """Main entry point"""
    
    print("🛡️  STIG to Ansible Playbook Generator")
    print("=" * 60)
    
    if len(sys.argv) != 2:
        print("Usage: python generate_playbooks.py <stig_file.xml>")
        print("\nExample:")
        print("  python generate_playbooks.py ../xml_files/sample_data/node2.example.com-STIG-20250710162433.xml")
        sys.exit(1)
    
    stig_file = sys.argv[1]
    
    # Validate input file
    if not Path(stig_file).exists():
        print(f"❌ Error: File not found: {stig_file}")
        sys.exit(1)
    
    # Check .env file
    env_file = Path('.env')
    if not env_file.exists():
        print(f"❌ Error: .env file not found. Please create .env file with LLAMA configuration.")
        print(f"See .env.template for required variables.")
        sys.exit(1)
    
    try:
        # Initialize generator
        generator = PlaybookGenerator('.env')
        
        # Process STIG file
        result = generator.process_stig_file(stig_file)
        
        # Display results
        if result['success']:
            print(f"\n✅ Processing completed successfully!")
            print(f"\n📊 Results Summary:")
            print(f"   📄 STIG file: {Path(result['stig_file']).name}")
            print(f"   🔍 Total findings: {result['total_findings']}")
            print(f"   ❌ Failed findings: {result['failed_findings']}")
            print(f"   🎯 Processed: {result['processed_findings']}")
            print(f"   ✅ Successful generations: {result['successful_generations']}")
            print(f"   ❌ Failed generations: {result['failed_generations']}")
            print(f"   📁 Output directory: {result['output_directory']}")
            
            # Display severity breakdown
            summary = result['summary']
            if 'by_severity' in summary:
                print(f"\n📈 Findings by Severity:")
                for severity, count in summary['by_severity'].items():
                    print(f"   {severity.title()}: {count}")
            
            print(f"\n🎉 Ansible playbooks generated successfully!")
            print(f"💡 Review the generated playbooks before running in production.")
            
        else:
            print(f"❌ Processing failed: {result['error']}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
