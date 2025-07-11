# TODO: STIG to Ansible Playbook Generator

## 🏃‍♂️ Phase 1: Core STIG Parsing (CURRENT)

### High Priority
- [ ] **Enhance XML Parser for STIG Structure**
  - [ ] Detect STIG document type in existing XML analyzer
  - [ ] Add STIG-specific element identification (rules, findings, checks)
  - [ ] Extract rule metadata (ID, severity, title, description)
  - [ ] Parse check text and fix text sections
  - [ ] Handle STIG result status (pass/fail/not_applicable)

- [ ] **STIG Findings Extractor**
  - [ ] Create `stig_parser.py` that extends base XML analyzer
  - [ ] Implement finding enumeration (iterate through all rules)
  - [ ] Extract finding details into structured format
  - [ ] Generate findings summary (counts by severity, status)
  - [ ] Output findings to JSON for LLM processing

### Medium Priority  
- [ ] **Basic LLM Integration**
  - [ ] Create `llm_interface.py` for LLAMA API calls
  - [ ] Load LLAMA_3_2_URL from .env file
  - [ ] Design prompts for Ansible task generation
  - [ ] Handle LLM response parsing and validation
  - [ ] Add error handling and retry logic

- [ ] **Proof of Concept Script**
  - [ ] Create `generate_playbooks.py` main script
  - [ ] Process single STIG file and extract one finding
  - [ ] Generate one Ansible task via LLM
  - [ ] Validate output as proper YAML
  - [ ] Save result to playbooks/ directory

## 🚀 Phase 2: LLM Playbook Generation

### High Priority
- [ ] **Playbook Structure Design**
  - [ ] Define Ansible playbook template structure
  - [ ] Create task categorization (file permissions, services, packages, etc.)
  - [ ] Design variable handling for different systems
  - [ ] Add metadata (finding ID, severity, description)

- [ ] **LLM Prompt Engineering** 
  - [ ] Design system prompt for Ansible expertise
  - [ ] Create finding-specific prompts with context
  - [ ] Include STIG fix text and check text in prompts
  - [ ] Add examples of good Ansible tasks for reference
  - [ ] Handle different finding types (config files, services, packages)

- [ ] **Batch Processing**
  - [ ] Process multiple findings from single STIG file
  - [ ] Generate separate playbook for each finding
  - [ ] Create master playbook that includes all findings
  - [ ] Add progress tracking and logging

### Medium Priority
- [ ] **Quality Assurance**
  - [ ] Validate generated YAML syntax
  - [ ] Check Ansible best practices compliance
  - [ ] Add task idempotency verification
  - [ ] Generate task documentation
  - [ ] Create test scenarios for validation

## 🔧 Phase 3: Advanced Features

### Enhancement Ideas
- [ ] **Smart Grouping**
  - [ ] Group related findings into single playbooks
  - [ ] Detect conflicting remediation tasks
  - [ ] Optimize task order and dependencies
  - [ ] Handle OS-specific variations

- [ ] **Integration Features**
  - [ ] CLI argument parsing for flexible usage
  - [ ] Configuration file for settings
  - [ ] Output format options (single file, multiple files, roles)
  - [ ] Integration with Ansible Galaxy structure

- [ ] **Validation & Testing**
  - [ ] Ansible syntax validation
  - [ ] Dry-run capability 
  - [ ] Integration with ansible-lint
  - [ ] Test playbook generation

## 📊 Technical Requirements

### XML Parser Enhancements Needed
1. **STIG Document Detection**
   ```python
   # Add to existing DocumentTypeDetector
   'STIG_RESULTS': {
       'root_elements': ['asset-report-collection', 'TestResult'],
       'namespaces': ['http://checklists.nist.gov/xccdf'],
       'description': 'STIG compliance scan results'
   }
   ```

2. **STIG Finding Structure**
   ```python
   @dataclass
   class STIGFinding:
       rule_id: str           # e.g., "RHEL-07-010010"
       severity: str          # Critical/High/Medium/Low  
       title: str             # Brief description
       description: str       # Detailed explanation
       check_text: str        # Verification steps
       fix_text: str          # Remediation instructions
       status: str            # pass/fail/not_applicable/not_reviewed
       references: List[str]  # CCI, NIST, etc.
   ```

3. **LLM Prompt Template**
   ```
   You are an expert Ansible developer. Generate an Ansible task to remediate this STIG finding:
   
   Rule ID: {rule_id}
   Title: {title}  
   Description: {description}
   Fix Text: {fix_text}
   
   Requirements:
   - Use proper Ansible task syntax
   - Make tasks idempotent
   - Add appropriate conditionals
   - Include error handling
   - Add descriptive names and comments
   ```

## 🎯 Immediate Next Steps

1. **Start with STIG Parser** - Enhance existing XML analyzer
2. **Extract One Finding** - Prove the concept works
3. **Generate One Playbook** - End-to-end test
4. **Iterate and Improve** - Add more findings types

## 🔗 Dependencies on Other Projects

- **XML Parser** (`../xml_files/`) - Need STIG detection capability
- **Environment** - LLAMA_3_2_URL must be configured
- **Testing** - Need sample STIG files for development

## 📈 Success Metrics

- [ ] Successfully parse STIG file and extract findings
- [ ] Generate valid Ansible YAML from LLM
- [ ] Process full STIG file (100+ findings) 
- [ ] Produce runnable playbooks that pass ansible-lint
- [ ] Demonstrate security compliance automation

---

**Priority**: Start with Phase 1 items to establish foundation, then move to LLM integration.
