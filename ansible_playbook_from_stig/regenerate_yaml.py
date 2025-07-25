#!/usr/bin/env python3
"""
Regenerate problematic YAML files with improved validation

This script will regenerate the files that have YAML structure issues
"""

import sys
import json
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

def load_findings_from_json():
    """Load findings from the previously exported JSON"""
    
    findings_dir = Path("./findings")
    json_files = list(findings_dir.glob("*_findings.json"))
    
    if not json_files:
        print("❌ No findings JSON files found in ./findings/")
        return []
    
    # Use the most recent findings file
    latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
    print(f"📂 Loading findings from: {latest_file.name}")
    
    try:
        with open(latest_file, 'r') as f:
            data = json.load(f)
        
        findings = data.get('findings', [])
        print(f"✅ Loaded {len(findings)} findings")
        return findings
        
    except Exception as e:
        print(f"❌ Error loading findings: {e}")
        return []

def identify_problematic_files():
    """Identify YAML files that have structure issues"""
    
    playbooks_dir = Path("./playbooks")
    if not playbooks_dir.exists():
        print("❌ No playbooks directory found")
        return []
    
    yaml_files = list(playbooks_dir.glob("*_task.yml"))
    problematic_files = []
    
    print(f"🔍 Checking {len(yaml_files)} task files for issues...")
    
    try:
        import yaml
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    content = f.read()
                
                # Check for obvious issues
                issues = []
                
                # Multiple YAML headers
                if content.count('---') > 1:
                    issues.append("Multiple YAML headers")
                
                # Invalid task structure (module calls not under proper task)
                lines = content.split('\n')
                in_task = False
                module_found_outside_task = False
                
                ansible_modules = ['package:', 'file:', 'lineinfile:', 'service:', 'systemd:', 'mount:', 'sysctl:', 'command:', 'shell:']
                
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('- name:'):
                        in_task = True
                    elif any(stripped.startswith(mod) for mod in ansible_modules):
                        if not in_task:
                            module_found_outside_task = True
                            break
                
                if module_found_outside_task:
                    issues.append("Module calls outside task structure")
                
                # Try YAML parsing
                try:
                    parsed = yaml.safe_load(content)
                    if not parsed:
                        issues.append("Empty YAML")
                except yaml.YAMLError as e:
                    issues.append(f"YAML syntax error: {str(e)[:50]}")
                
                # Check for repetitive content
                if content.count('- name:') > 5:
                    issues.append("Too many tasks (likely repetitive)")
                
                if issues:
                    problematic_files.append({
                        'file': yaml_file,
                        'issues': issues,
                        'size': len(content)
                    })
                    print(f"   ❌ {yaml_file.name}: {', '.join(issues)}")
                
            except Exception as e:
                problematic_files.append({
                    'file': yaml_file,
                    'issues': [f"Read error: {e}"],
                    'size': 0
                })
                print(f"   ❌ {yaml_file.name}: Read error")
    
    except ImportError:
        print("⚠️  PyYAML not available - checking basic structure only")
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    content = f.read()
                
                # Basic checks without YAML parsing
                issues = []
                if content.count('---') > 1:
                    issues.append("Multiple YAML headers")
                if content.count('- name:') > 3:
                    issues.append("Too many tasks")
                
                if issues:
                    problematic_files.append({
                        'file': yaml_file,
                        'issues': issues,
                        'size': len(content)
                    })
                    
            except Exception as e:
                problematic_files.append({
                    'file': yaml_file,
                    'issues': [f"Read error: {e}"],
                    'size': 0
                })
    
    print(f"\n📊 Found {len(problematic_files)} problematic files")
    return problematic_files

def regenerate_file(finding_data: dict, output_file: Path) -> bool:
    """Regenerate a single file using the improved LLM interface"""
    
    try:
        from llm_interface import LLMInterface
        
        # Check if .env exists
        if not Path('.env').exists():
            print("❌ No .env file found - cannot regenerate")
            return False
        
        llm = LLMInterface()
        
        # Generate new task
        result = llm.generate_ansible_task(finding_data)
        
        if result['success'] and result.get('yaml_valid', False):
            # Create new file content
            new_content = f"""---
# STIG Finding: {finding_data.get('rule_id', 'Unknown')}
# Severity: {finding_data.get('severity', 'unknown')}
# Status: {finding_data.get('status', 'unknown')}
# Title: {finding_data.get('title', 'No title')}

{result['content']}
"""
            
            # Write to file
            with open(output_file, 'w') as f:
                f.write(new_content)
            
            print(f"      ✅ Regenerated: {result.get('task_name', 'Task')}")
            return True
        else:
            error = result.get('error') or result.get('validation_error', 'Unknown error')
            print(f"      ❌ Failed: {error}")
            return False
            
    except Exception as e:
        print(f"      ❌ Exception: {e}")
        return False

def main():
    """Main regeneration function"""
    
    print("🔧 YAML File Regeneration Utility")
    print("=" * 50)
    print("This will regenerate problematic YAML files with improved validation.")
    
    # Load findings data
    findings_data = load_findings_from_json()
    if not findings_data:
        print("❌ Cannot proceed without findings data")
        return
    
    # Create lookup dict by rule_id
    findings_lookup = {f['rule_id']: f for f in findings_data}
    
    # Identify problematic files
    problematic_files = identify_problematic_files()
    if not problematic_files:
        print("✅ No problematic files found!")
        return
    
    # Ask for confirmation
    print(f"\n⚠️  Found {len(problematic_files)} files with issues.")
    print("Files to regenerate:")
    for item in problematic_files[:10]:  # Show first 10
        print(f"   - {item['file'].name}: {', '.join(item['issues'])}")
    
    if len(problematic_files) > 10:
        print(f"   ... and {len(problematic_files) - 10} more")
    
    response = input(f"\nRegenerate these {len(problematic_files)} files? (y/N): ")
    if response.lower() != 'y':
        print("❌ Cancelled by user")
        return
    
    # Regenerate files
    print(f"\n🔄 Regenerating {len(problematic_files)} files...")
    
    success_count = 0
    error_count = 0
    
    for item in problematic_files:
        file_path = item['file']
        file_name = file_path.name
        
        # Extract rule_id from filename
        rule_id = file_name.replace('_task.yml', '').replace('_', ':')
        
        # Find matching finding data
        finding_data = None
        for rule, data in findings_lookup.items():
            if rule.replace(':', '_') in file_name or rule == rule_id:
                finding_data = data
                break
        
        if not finding_data:
            print(f"   ⚠️  {file_name}: No matching finding data found")
            error_count += 1
            continue
        
        print(f"   🔄 Regenerating {file_name}...")
        
        if regenerate_file(finding_data, file_path):
            success_count += 1
        else:
            error_count += 1
    
    # Summary
    print(f"\n📊 Regeneration Results:")
    print(f"   ✅ Successfully regenerated: {success_count}")
    print(f"   ❌ Failed to regenerate: {error_count}")
    
    if success_count > 0:
        print(f"\n🎉 Regeneration complete!")
        print("   Files should now have proper YAML structure.")
        print("   Run 'python cleanup_yaml.py' to validate the results.")
    else:
        print(f"\n⚠️  No files were successfully regenerated.")

if __name__ == "__main__":
    main()
