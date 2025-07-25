#!/usr/bin/env python3
"""
Deterministic Ansible Playbook Generator

Generates properly formatted Ansible playbooks from STIG targets without LLM.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PlaybookTask:
    name: str
    module: str
    params: Dict[str, Any]
    tags: List[str]
    register: str = None
    when: str = None
    notify: List[str] = None

class DeterministicPlaybookGenerator:
    """Generate Ansible playbooks deterministically from STIG targets"""
    
    def __init__(self):
        self.service_restart_map = {
            'sshd_config': 'sshd',
            'ssh_config': 'sshd', 
            'httpd.conf': 'httpd',
            'nginx.conf': 'nginx',
            'auditd.conf': 'auditd',
            'rsyslog.conf': 'rsyslog'
        }
        
        self.package_groups = {
            'security': ['aide', 'audit', 'audit-libs', 'usbguard'],
            'crypto': ['dracut-fips', 'dracut-fips-aesni'],
            'unwanted': ['prelink', 'gdm', 'xorg-x11-server-common']
        }
    
    def generate_playbook_from_targets(self, targets_file: str, output_file: str):
        """Generate complete Ansible playbook from targets JSON"""
        
        with open(targets_file, 'r') as f:
            data = json.load(f)
        
        targets = data['targets']
        metadata = data['metadata']
        
        # Group targets by type for better organization
        grouped_targets = self._group_targets_by_type(targets)
        
        # Generate playbook structure
        playbook = self._create_playbook_structure(metadata, grouped_targets)
        
        # Write to file
        self._write_playbook(playbook, output_file)
        
        print(f"✅ Generated playbook with {len(targets)} tasks: {output_file}")
        return playbook
    
    def _group_targets_by_type(self, targets: List[Dict]) -> Dict[str, List[Dict]]:
        """Group targets by type for logical organization"""
        
        groups = {
            'packages_install': [],
            'packages_remove': [],
            'services': [],
            'file_ownership': [],
            'file_permissions': [],
            'sysctl': [],
            'mounts': [],
            'unknown': []
        }
        
        for target in targets:
            target_type = target['target_type']
            
            if target_type == 'package':
                if target['action_context'] == 'state=absent':
                    groups['packages_remove'].append(target)
                else:
                    groups['packages_install'].append(target)
            elif target_type == 'service':
                groups['services'].append(target)
            elif target_type == 'file_ownership':
                groups['file_ownership'].append(target)
            elif target_type == 'file_permission':
                groups['file_permissions'].append(target)
            elif target_type == 'sysctl':
                groups['sysctl'].append(target)
            elif target_type == 'mount':
                groups['mounts'].append(target)
            else:
                groups['unknown'].append(target)
        
        # Remove empty groups
        return {k: v for k, v in groups.items() if v}
    
    def _create_playbook_structure(self, metadata: Dict, grouped_targets: Dict) -> Dict:
        """Create the main playbook structure"""
        
        playbook = {
            'name': 'STIG Compliance Remediation Playbook',
            'hosts': 'all',
            'become': True,
            'gather_facts': True,
            'vars': {
                'stig_remediation_date': datetime.now().isoformat(),
                'total_remediations': metadata.get('total_actionable', 0)
            },
            'tasks': []
        }
        
        # Add header task
        playbook['tasks'].append({
            'name': 'Display STIG remediation information',
            'debug': {
                'msg': [
                    'Starting STIG compliance remediation',
                    'Total remediations: {{ total_remediations }}',
                    'Generated on: {{ stig_remediation_date }}'
                ]
            },
            'tags': ['info']
        })
        
        # Generate tasks for each group
        for group_name, targets in grouped_targets.items():
            playbook['tasks'].extend(self._generate_tasks_for_group(group_name, targets))
        
        # Add handlers
        playbook['handlers'] = self._generate_handlers(grouped_targets)
        
        return [playbook]  # Ansible playbook is a list of plays
    
    def _generate_tasks_for_group(self, group_name: str, targets: List[Dict]) -> List[Dict]:
        """Generate tasks for a specific group"""
        
        tasks = []
        
        # Add group header
        tasks.append({
            'name': f"=== {group_name.replace('_', ' ').title()} ===",
            'debug': {
                'msg': f"Starting {group_name.replace('_', ' ')} remediation"
            },
            'tags': [group_name, 'info']
        })
        
        # Generate individual tasks
        for target in targets:
            task = self._generate_single_task(target, group_name)
            tasks.append(task)
        
        return tasks
    
    def _generate_single_task(self, target: Dict, group_name: str) -> Dict:
        """Generate a single Ansible task from target"""
        
        # Base task structure
        task = {
            'name': self._generate_task_name(target),
            target['ansible_module']: target['ansible_params'].copy(),
            'tags': self._generate_task_tags(target, group_name)
        }
        
        # Add register for file operations that might need service restarts
        if target['target_type'] in ['file_ownership', 'file_permission']:
            register_name = self._generate_register_name(target)
            task['register'] = register_name
            
            # Check if this file change should trigger a service restart
            service_name = self._get_service_for_file(target['target_name'])
            if service_name:
                task['notify'] = [f'restart {service_name}']
        
        # Add validation for critical operations
        if target['severity'] in ['high', 'critical']:
            task['validate'] = self._generate_validation(target)
        
        return task
    
    def _generate_task_name(self, target: Dict) -> str:
        """Generate descriptive task name"""
        
        # Use the title if available, otherwise generate from target info
        base_name = target.get('title', f"Configure {target['target_name']}")
        
        # Add compliance reference if available
        nist_refs = target.get('compliance', {}).get('nist_refs', [])
        if nist_refs:
            ref = nist_refs[0]
            return f"{ref}: {base_name}"
        
        return base_name
    
    def _generate_task_tags(self, target: Dict, group_name: str) -> List[str]:
        """Generate appropriate tags for the task"""
        
        tags = ['stig', 'security', group_name]
        
        # Add severity tag
        if target.get('severity'):
            tags.append(f"severity_{target['severity']}")
        
        # Add specific tags based on target type
        if target['target_type'] == 'package':
            tags.append('packages')
        elif target['target_type'] in ['file_ownership', 'file_permission']:
            tags.append('file_security')
        elif target['target_type'] == 'service':
            tags.append('services')
        elif target['target_type'] == 'sysctl':
            tags.append('kernel_parameters')
        
        # Add compliance tags
        nist_refs = target.get('compliance', {}).get('nist_refs', [])
        for ref in nist_refs:
            tags.append(ref.lower().replace('-', '_'))
        
        return tags
    
    def _generate_register_name(self, target: Dict) -> str:
        """Generate register variable name"""
        
        # Clean up target name for variable
        clean_name = target['target_name'].replace('/', '_').replace('-', '_').replace('.', '_')
        action = target['target_type'].replace('_', '_')
        return f"{action}{clean_name}_result"
    
    def _get_service_for_file(self, file_path: str) -> str:
        """Determine which service should be restarted for a file change"""
        
        for file_pattern, service in self.service_restart_map.items():
            if file_pattern in file_path:
                return service
        
        return None
    
    def _generate_validation(self, target: Dict) -> str:
        """Generate validation command for critical operations"""
        
        if target['ansible_module'] == 'file':
            return f"test -f {target['target_name']}"
        elif target['ansible_module'] == 'systemd':
            return f"systemctl is-active {target['ansible_params']['name']}"
        
        return None
    
    def _generate_handlers(self, grouped_targets: Dict) -> List[Dict]:
        """Generate handlers for service restarts"""
        
        handlers = []
        services_to_restart = set()
        
        # Find all services that might need restarting
        for group_name, targets in grouped_targets.items():
            if group_name in ['file_ownership', 'file_permissions']:
                for target in targets:
                    service = self._get_service_for_file(target['target_name'])
                    if service:
                        services_to_restart.add(service)
        
        # Generate restart handlers
        for service in services_to_restart:
            handlers.append({
                'name': f'restart {service}',
                'systemd': {
                    'name': service,
                    'state': 'restarted'
                },
                'listen': f'restart {service}'
            })
        
        return handlers
    
    def _write_playbook(self, playbook: List[Dict], output_file: str):
        """Write playbook to YAML file with proper formatting"""
        
        # Ensure output directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Custom YAML formatting for readability
        yaml.add_representer(type(None), lambda dumper, value: dumper.represent_scalar('tag:yaml.org,2002:null', ''))
        
        with open(output_file, 'w') as f:
            # Write header comment
            f.write("---\n")
            f.write("# STIG Compliance Remediation Playbook\n")
            f.write(f"# Generated automatically on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("# DO NOT EDIT MANUALLY - Regenerate from STIG targets\n\n")
            
            # Write playbook
            yaml.dump(playbook, f, 
                     default_flow_style=False,
                     indent=2,
                     width=120,
                     sort_keys=False)

def generate_playbook_from_targets(targets_file: str, output_file: str = None):
    """Main function to generate playbook from targets file"""
    
    if not output_file:
        base_name = Path(targets_file).stem.replace('_ansible_targets', '')
        output_file = f"playbooks/{base_name}_remediation_playbook.yml"
    
    generator = DeterministicPlaybookGenerator()
    return generator.generate_playbook_from_targets(targets_file, output_file)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python playbook_generator.py <targets_file.json> [output_file.yml]")
        sys.exit(1)
    
    targets_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"🚀 Generating Ansible playbook from {targets_file}")
    
    try:
        playbook = generate_playbook_from_targets(targets_file, output_file)
        print("✅ Playbook generation completed!")
        
        # Show some stats
        total_tasks = sum(len(play.get('tasks', [])) for play in playbook)
        print(f"📊 Generated {total_tasks} tasks across {len(playbook)} play(s)")
        
    except Exception as e:
        print(f"❌ Error generating playbook: {e}")
        sys.exit(1)