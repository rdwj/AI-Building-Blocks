# Granite 3.3 8B Instruct Prompts for Complex STIG Processing

## 1. CLASSIFICATION PROMPT (First Step)
classification_prompt = """You are analyzing a STIG security finding to classify its complexity type.

STIG Finding:
Rule ID: {rule_id}
Title: {title}
Description: {description}
Fix Text: {fix_text}

Classify this finding into ONE category:

1. SHELL_SCRIPT - Complex shell scripts with conditionals, loops, or multiple commands
2. PACKAGE_VERIFICATION - RPM verification, package integrity checks, reinstallation logic
3. CONFIG_MODIFICATION - Complex file configuration changes (AIDE, PAM, etc.)
4. BOOT_CONFIGURATION - GRUB, kernel parameters, boot-critical changes
5. MULTI_STEP_PROCESS - Sequential tasks that must be done in specific order
6. CRON_SCHEDULING - Cron job creation with complex timing or piping
7. UNKNOWN - Cannot be classified into above categories

Look for these keywords:
- Shell scripts: "if", "then", "for", "grep", "sed", "awk"
- Package verification: "rpm -Va", "reinstall", "verify", "package integrity"
- Config modification: "aide.conf", "pam", configuration file editing
- Boot: "grub", "dracut", "initramfs", "fips", "kernel"
- Multi-step: "After", "Next", "Then", sequential instructions
- Cron: "crontab", "cron", scheduled execution

Respond with only the category name (e.g., "SHELL_SCRIPT").
"""

## 2. SHELL SCRIPT PROMPT
shell_script_prompt = """You are converting a STIG shell script remediation to Ansible tasks.

STIG Finding:
Rule ID: {rule_id}
Title: {title}
Fix Text: {fix_text}

Analyze the shell script and convert to Ansible tasks. Break complex scripts into logical steps.

JSON Schema:
{{
  "target_type": "shell_script_remediation",
  "target_name": "descriptive_name",
  "ansible_module": "block",
  "ansible_params": {{
    "tasks": [
      {{
        "name": "Task description",
        "module_name": {{"param": "value"}},
        "when": "condition (optional)"
      }}
    ]
  }},
  "requires_reboot": false
}}

Guidelines:
- Use 'lineinfile' for single line changes
- Use 'blockinfile' for multi-line additions
- Use 'command' only when necessary
- Add 'when' conditions for conditional logic
- Use 'file' module for file operations
- Set requires_reboot=true for system-critical changes

Example shell script: if test -e /etc/config; then sed -i 's/old/new/' /etc/config; fi
Example output:
{{
  "target_type": "shell_script_remediation", 
  "target_name": "config_file_update",
  "ansible_module": "lineinfile",
  "ansible_params": {{
    "path": "/etc/config",
    "regexp": "old",
    "line": "new"
  }},
  "requires_reboot": false
}}

Return only valid JSON.
"""

## 3. PACKAGE VERIFICATION PROMPT  
package_verification_prompt = """You are converting STIG package verification logic to Ansible tasks.

STIG Finding:
Rule ID: {rule_id}
Title: {title}
Fix Text: {fix_text}

This involves RPM package verification and potential reinstallation. Convert to Ansible.

JSON Schema:
{{
  "target_type": "package_verification",
  "target_name": "package_integrity_check", 
  "ansible_module": "script",
  "ansible_params": {{
    "cmd": "verification_script.sh",
    "creates": "/var/log/package_verification.log"
  }},
  "script_content": "#!/bin/bash\\n# Script content here"
}}

Guidelines:
- Package verification requires custom scripts due to complexity
- Use 'script' module to run verification logic
- Log results to /var/log/ for auditing
- Handle package reinstallation within script
- Use 'creates' parameter to avoid repeated runs

Look for these patterns:
- "rpm -Va" = RPM verification
- "yum reinstall" = Package reinstallation  
- Hash verification = File integrity checking
- Permission restoration = File permission fixes

Return only valid JSON.
"""

## 4. CONFIG MODIFICATION PROMPT
config_modification_prompt = """You are converting complex STIG configuration changes to Ansible tasks.

STIG Finding:
Rule ID: {rule_id}
Title: {title}
Description: {description}
Fix Text: {fix_text}

This involves complex configuration file modifications. Convert to Ansible.

JSON Schema:
{{
  "target_type": "config_modification",
  "target_name": "config_file_path_or_name",
  "ansible_module": "appropriate_module",
  "ansible_params": {{
    "path": "/etc/config/file",
    "additional_params": "as_needed"
  }},
  "backup_required": true
}}

Module Selection:
- Simple line changes: "lineinfile" 
- Multi-line blocks: "blockinfile"
- Pattern replacement: "replace"
- Complex parsing: "template" with jinja2
- AIDE config: "replace" with regex

Common Config Files:
- /etc/aide.conf = AIDE configuration
- /etc/pam.d/* = PAM authentication
- /etc/sysconfig/* = System configuration
- /etc/security/* = Security settings

Always set backup_required=true for critical configs.

Return only valid JSON.
"""

## 5. BOOT CONFIGURATION PROMPT
boot_configuration_prompt = """You are converting STIG boot/kernel configuration to Ansible tasks.

STIG Finding:
Rule ID: {rule_id}
Title: {title}
Fix Text: {fix_text}

This involves boot-critical changes. Convert to Ansible with proper sequencing.

JSON Schema:
{{
  "target_type": "boot_configuration",
  "target_name": "boot_modification_name",
  "ansible_module": "block", 
  "ansible_params": {{
    "tasks": [
      {{
        "name": "Step description",
        "module": {{"param": "value"}}
      }}
    ]
  }},
  "requires_reboot": true,
  "critical_warning": "Boot configuration change - test in non-production first"
}}

Boot Sequence:
1. Install required packages first
2. Modify configuration files
3. Rebuild initramfs/grub as needed
4. Reboot required

Common Boot Tasks:
- GRUB_CMDLINE_LINUX modifications
- dracut/initramfs rebuilds  
- FIPS mode enablement
- Kernel parameter changes

Always set requires_reboot=true and include critical_warning.

Return only valid JSON.
"""

## 6. MULTI-STEP PROCESS PROMPT
multi_step_prompt = """You are converting a STIG multi-step process to Ansible tasks.

STIG Finding:
Rule ID: {rule_id}
Title: {title}
Description: {description}
Fix Text: {fix_text}

This requires multiple sequential steps. Convert to Ansible with proper ordering.

JSON Schema:
{{
  "target_type": "multi_step_process",
  "target_name": "process_name",
  "ansible_module": "block",
  "ansible_params": {{
    "tasks": [
      {{
        "name": "Step 1: Description", 
        "module": {{"param": "value"}},
        "register": "step1_result"
      }},
      {{
        "name": "Step 2: Description",
        "module": {{"param": "value"}},
        "when": "step1_result is succeeded"
      }}
    ]
  }},
  "dependencies": ["step1 must complete before step2"]
}}

Guidelines:
- Use 'register' to capture step results
- Use 'when' conditions to ensure proper sequencing  
- Include error handling between steps
- Document dependencies clearly
- Consider rollback procedures

Keywords indicating steps: "After", "Next", "Then", "Following", numbered steps

Return only valid JSON.
"""

## 7. CRON SCHEDULING PROMPT
cron_scheduling_prompt = """You are converting STIG cron job configuration to Ansible tasks.

STIG Finding:
Rule ID: {rule_id}
Title: {title}
Fix Text: {fix_text}

This involves creating scheduled tasks. Convert to Ansible.

JSON Schema:
{{
  "target_type": "cron_scheduling",
  "target_name": "cron_job_name",
  "ansible_module": "cron",
  "ansible_params": {{
    "name": "Job description",
    "minute": "05",
    "hour": "4", 
    "day": "*",
    "month": "*", 
    "weekday": "*",
    "job": "command to run",
    "user": "root"
  }},
  "notification_required": false
}}

Cron Time Patterns:
- "05 4 * * *" = Daily at 4:05 AM
- "05 4 * * 0" = Weekly on Sunday at 4:05 AM  
- "0 * * * *" = Hourly

Email Notification:
- If fix_text contains "mail" or "email": set notification_required=true
- Add email piping to job command

Common STIG Cron Jobs:
- AIDE integrity checks
- Log rotation
- Security scans

Return only valid JSON.
"""

## 8. FALLBACK PROMPT FOR UNKNOWN CASES
fallback_prompt = """You are analyzing a complex STIG finding that doesn't fit standard patterns.

STIG Finding:
Rule ID: {rule_id}
Title: {title}
Description: {description}
Fix Text: {fix_text}

Analyze the intent and create the best possible Ansible automation.

JSON Schema:
{{
  "target_type": "custom_remediation",
  "target_name": "descriptive_name",
  "ansible_module": "best_fit_module",
  "ansible_params": {{
    "appropriate": "parameters"
  }},
  "manual_review_required": true,
  "complexity_notes": "Why this is complex"
}}

Approach:
1. Identify the core security objective
2. Choose the most appropriate Ansible module
3. Extract key parameters from fix_text
4. Note any aspects requiring manual review
5. Explain complexity in complexity_notes

Prefer these modules:
- "lineinfile" for single line changes
- "file" for permission/ownership
- "systemd" for service management
- "command" as last resort

Always set manual_review_required=true for fallback cases.

Return only valid JSON.
"""

## USAGE EXAMPLE:
def process_complex_finding(finding_data):
    """
    Process a complex STIG finding using Granite 3.3 8B
    """
    
    # Step 1: Classify the finding
    classification = call_granite_3_3_8b(
        classification_prompt.format(**finding_data)
    )
    
    # Step 2: Use appropriate specialized prompt
    prompt_map = {
        "SHELL_SCRIPT": shell_script_prompt,
        "PACKAGE_VERIFICATION": package_verification_prompt, 
        "CONFIG_MODIFICATION": config_modification_prompt,
        "BOOT_CONFIGURATION": boot_configuration_prompt,
        "MULTI_STEP_PROCESS": multi_step_prompt,
        "CRON_SCHEDULING": cron_scheduling_prompt,
        "UNKNOWN": fallback_prompt
    }
    
    selected_prompt = prompt_map.get(classification, fallback_prompt)
    
    # Step 3: Generate Ansible tasks
    result = call_granite_3_3_8b(
        selected_prompt.format(**finding_data)
    )
    
    return json.loads(result)

## BATCH PROCESSING EXAMPLE:
def process_unknown_findings_batch(unknown_findings):
    """
    Process all unknown findings from your data
    """
    results = []
    
    for finding in unknown_findings:
        try:
            result = process_complex_finding(finding)
            result['original_rule_id'] = finding['rule_id']
            results.append(result)
        except Exception as e:
            print(f"Error processing {finding['rule_id']}: {e}")
            # Log failed finding for manual review
            
    return results