#!/usr/bin/env python3
"""
Clean up existing playbook files that have markdown formatting issues
"""

import os
import re
from pathlib import Path

def clean_yaml_file(file_path: Path) -> bool:
    """Clean a single YAML file of markdown formatting issues"""
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Extract just the YAML content, removing markdown
        lines = content.split('\n')
        cleaned_lines = []
        in_yaml_block = False
        yaml_content_started = False
        
        for line in lines:
            line_stripped = line.strip()
            
            # Skip the header comments (keep them)
            if line.startswith('# STIG Finding:') or line.startswith('# Severity:') or line.startswith('# Status:') or line.startswith('# Title:'):
                cleaned_lines.append(line)
                continue
            
            # Detect markdown code block start
            if line_stripped == '```yaml' or line_stripped == '```yml':
                in_yaml_block = True
                continue
            
            # Detect markdown code block end
            if line_stripped == '```' and in_yaml_block:
                in_yaml_block = False
                continue
            
            # Detect YAML content start
            if line_stripped.startswith('---') or line_stripped.startswith('- name:'):
                yaml_content_started = True
            
            # Include YAML content
            if in_yaml_block or yaml_content_started:
                # Stop at explanatory text
                if any(phrase in line_stripped.lower() for phrase in [
                    'please note', 'this task is', 'also note', 'to improve',
                    'you could consider', 'additional configuration', 'this is a known limitation'
                ]):
                    break
                
                cleaned_lines.append(line)
        
        # Write cleaned content back
        cleaned_content = '\n'.join(cleaned_lines).rstrip() + '\n'
        
        # Only update if content actually changed
        if cleaned_content != content:
            with open(file_path, 'w') as f:
                f.write(cleaned_content)
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error cleaning {file_path}: {e}")
        return False

def clean_playbook_directory(playbooks_dir: str = "./playbooks"):
    """Clean all YAML files in the playbooks directory"""
    
    playbooks_path = Path(playbooks_dir)
    
    if not playbooks_path.exists():
        print(f"❌ Playbooks directory not found: {playbooks_dir}")
        return
    
    # Find all YAML files
    yaml_files = list(playbooks_path.glob("*.yml")) + list(playbooks_path.glob("*.yaml"))
    
    if not yaml_files:
        print(f"ℹ️  No YAML files found in {playbooks_dir}")
        return
    
    print(f"🧹 Cleaning {len(yaml_files)} YAML files in {playbooks_dir}")
    
    cleaned_count = 0
    error_count = 0
    
    for yaml_file in yaml_files:
        print(f"   Processing: {yaml_file.name}")
        
        try:
            was_cleaned = clean_yaml_file(yaml_file)
            if was_cleaned:
                cleaned_count += 1
                print(f"      ✅ Cleaned")
            else:
                print(f"      ℹ️  No changes needed")
        except Exception as e:
            error_count += 1
            print(f"      ❌ Error: {e}")
    
    print(f"\n📊 Results:")
    print(f"   ✅ Files cleaned: {cleaned_count}")
    print(f"   ℹ️  Files unchanged: {len(yaml_files) - cleaned_count - error_count}")
    print(f"   ❌ Errors: {error_count}")

def validate_cleaned_files(playbooks_dir: str = "./playbooks"):
    """Validate that cleaned files are valid YAML"""
    
    playbooks_path = Path(playbooks_dir)
    yaml_files = list(playbooks_path.glob("*.yml")) + list(playbooks_path.glob("*.yaml"))
    
    if not yaml_files:
        return
    
    print(f"\n🔍 Validating {len(yaml_files)} cleaned files...")
    
    valid_count = 0
    invalid_count = 0
    
    try:
        import yaml
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    content = f.read()
                
                # Parse YAML
                parsed = yaml.safe_load(content)
                
                if parsed:
                    valid_count += 1
                    print(f"   ✅ {yaml_file.name}")
                else:
                    invalid_count += 1
                    print(f"   ❌ {yaml_file.name} - parsed as None")
                    
            except yaml.YAMLError as e:
                invalid_count += 1
                print(f"   ❌ {yaml_file.name} - YAML error: {e}")
            except Exception as e:
                invalid_count += 1
                print(f"   ❌ {yaml_file.name} - Error: {e}")
        
        print(f"\n📈 Validation Results:")
        print(f"   ✅ Valid YAML files: {valid_count}")
        print(f"   ❌ Invalid YAML files: {invalid_count}")
        
    except ImportError:
        print("⚠️  PyYAML not available for validation")

def main():
    """Main cleanup function"""
    
    print("🧹 YAML File Cleanup Utility")
    print("=" * 40)
    print("This will clean markdown formatting from generated playbook files.")
    
    # Check if playbooks directory exists
    if not Path("./playbooks").exists():
        print("❌ No ./playbooks directory found")
        print("   Run this from the ansible_playbook_from_stig directory")
        return
    
    # Perform cleanup
    clean_playbook_directory("./playbooks")
    
    # Validate results
    validate_cleaned_files("./playbooks")
    
    print(f"\n🎉 Cleanup complete!")
    print("   Files have been cleaned of markdown formatting.")
    print("   You can now use the cleaned playbook files.")

if __name__ == "__main__":
    main()
