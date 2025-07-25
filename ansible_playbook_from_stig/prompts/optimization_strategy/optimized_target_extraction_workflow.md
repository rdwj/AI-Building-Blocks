# Optimized Target Extraction Workflow

## Phase 1: Automatic Processing (No LLM Needed)
Filter and use targets where `target_type != "unknown"`:

```python
# Load the ansible targets JSON
with open('findings/your_file_ansible_targets.json') as f:
    data = json.load(f)

# Separate automatically extracted vs manual review needed
automatic_targets = []
manual_review = []

for target in data['targets']:
    if target['target_type'] != 'unknown':
        automatic_targets.append(target)
    else:
        manual_review.append(target)

print(f"✅ Ready for direct Ansible use: {len(automatic_targets)}")
print(f"🤔 Need LLM review: {len(manual_review)}")
```

## Phase 2: LLM Processing (Only for Unknowns)
Only send the `manual_review` items to your LLM with this focused prompt:

```
Analyze these STIG findings that couldn't be automatically parsed:

{manual_review_findings}

For each finding, extract:
1. target_type (file_ownership, package, service, sysctl, mount, etc.)
2. target_name (specific file path, package name, etc.) 
3. ansible_module (file, yum, systemd, sysctl, etc.)
4. ansible_params (ready-to-use parameters)

Only process the ones marked as "unknown" - ignore the rest.
```

## Phase 3: Merge Results
Combine automatic + LLM-processed targets for complete playbook generation.

## Quality Check Statistics

From your targets JSON, check the `metadata.total_actionable` vs total findings:

```python
# Example output analysis:
{
  "metadata": {
    "total_actionable": 85,  # Ready for Ansible
    "total_findings": 100    # Total findings
  }
}

# This means:
# - 85% automatically extracted (no LLM needed)
# - 15% need manual review with LLM
```

## Cost/Time Savings

**Before (everything through LLM):**
- 100 findings × LLM cost = High cost
- Sequential processing = Slow

**After (hybrid approach):**
- 85 findings × $0 = Free (automatic)
- 15 findings × LLM cost = Low cost  
- Parallel processing = Fast

## Implementation Example

```python
def process_stig_targets(targets_file):
    with open(targets_file) as f:
        data = json.load(f)
    
    ready_targets = [t for t in data['targets'] 
                    if t['target_type'] != 'unknown']
    
    unknown_targets = [t for t in data['targets'] 
                      if t['target_type'] == 'unknown']
    
    print(f"🚀 Ready for Ansible: {len(ready_targets)}")
    print(f"🔍 Need LLM review: {len(unknown_targets)}")
    
    # Generate Ansible tasks for ready targets
    ansible_tasks = []
    for target in ready_targets:
        task = {
            'name': f"Fix {target['rule_id']}",
            target['ansible_module']: target['ansible_params']
        }
        ansible_tasks.append(task)
    
    return ansible_tasks, unknown_targets
```

**Bottom line: You can skip the LLM for 80-90% of your findings and only use it for the complex/unknown cases!**