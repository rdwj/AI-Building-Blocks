# TODO: STIG to Ansible Playbook Generator

## ✅ Phase 1: Core STIG Parsing (COMPLETED!)

### High Priority ✅ COMPLETED
- [x] **Enhance XML Parser for STIG Structure**
  - [x] Detect STIG document type in existing XML analyzer
  - [x] Add STIG-specific element identification (rules, findings, checks)
  - [x] Extract rule metadata (ID, severity, title, description)
  - [x] Parse check text and fix text sections
  - [x] Handle STIG result status (pass/fail/not_applicable)

- [x] **STIG Findings Extractor**
  - [x] Create `stig_parser_enhanced.py` that extends base XML analyzer
  - [x] Implement finding enumeration (iterate through all rules)
  - [x] Extract finding details into structured format
  - [x] Generate findings summary (counts by severity, status)
  - [x] Output findings to JSON for LLM processing

## ✅ Phase 2: Basic LLM Integration (COMPLETED!)

### Medium Priority ✅ COMPLETED
- [x] **Basic LLM Integration**
  - [x] Create `llm_interface.py` for LLAMA API calls
  - [x] Load LLAMA_3_2_URL from .env file
  - [x] Design prompts for Ansible task generation
  - [x] Handle LLM response parsing and validation
  - [x] Add error handling and retry logic

- [x] **Proof of Concept Script**
  - [x] Create `generate_playbooks.py` main script
  - [x] Process single STIG file and extract findings
  - [x] Generate Ansible tasks via LLM (batch processing implemented)
  - [x] Validate output as proper YAML
  - [x] Save results to playbooks/ directory

## 🚧 Phase 3: Multi-Step LLM Workflow (NEW APPROACH - CURRENT)

### High Priority 🔄 IN PROGRESS
- [ ] **Output Organization & Run Management**
  - [ ] Implement hierarchical output directory structure:
    ```
    playbooks/
    ├── [input_filename]/
    │   ├── [run_timestamp_id]/
    │   │   ├── individual_tasks/
    │   │   ├── master_playbook.yml
    │   │   ├── run_metadata.json
    │   │   └── workflow_log.txt
    │   └── latest -> [most_recent_run]/
    └── summary_report.html
    ```
  - [ ] Generate unique run IDs with timestamp (e.g., `20250711_143022_af7b3c`)
  - [ ] Create input file reference mapping (handle long filenames)
  - [ ] Implement run metadata tracking (start time, findings count, success rate)
  - [ ] Add "latest" symlink for easy access to most recent run
  - [ ] Create run comparison tools for tracking improvements over time

- [ ] **LangGraph Workflow Implementation**
  - [ ] Install and configure LangGraph for workflow orchestration
  - [ ] Design multi-step workflow graph:
    1. STIG Analysis Step → Extract remediation requirements
    2. Ansible Generation Step → Convert requirements to playbooks
    3. Validation Step → Verify playbook structure and syntax
    4. Integration Step → Combine into master playbook
  - [ ] Implement workflow state management
  - [ ] Add workflow progress tracking and logging

- [ ] **Prompt Engineering & Management**
  - [ ] Create `prompts/` directory for YAML-formatted prompts
  - [ ] Design Step 1 prompt: "Analyze STIG finding and extract remediation requirements"
    - Input: STIG finding JSON
    - Output: Structured remediation requirements (JSON/YAML)
    - Include examples of good analysis
  - [ ] Design Step 2 prompt: "Generate Ansible task from remediation requirements"
    - Input: Structured remediation requirements
    - Output: Valid Ansible YAML task
    - Include 3-5 example transformations covering different scenarios
  - [ ] Design Step 3 prompt: "Review and improve Ansible task quality"
    - Input: Generated Ansible task
    - Output: Improved task with better practices
  - [ ] Create prompt templates with variable substitution
  - [ ] Implement prompt versioning and testing

### Medium Priority
- [ ] **In-Context Learning Examples**
  - [ ] Create comprehensive example library covering:
    - Package management (install/remove)
    - File/directory operations (permissions, ownership)
    - Service management (enable/disable/restart)
    - Configuration file modifications (lineinfile, template)
    - Security settings (sysctl, mount options)
    - User/group management
  - [ ] Format examples as YAML for easy prompt inclusion
  - [ ] Create few-shot learning templates for different finding types
  - [ ] Implement dynamic example selection based on finding characteristics

- [ ] **Workflow State Management**
  - [ ] Design state schema for workflow tracking
  - [ ] Implement persistence for long-running workflows
  - [ ] Add resume capability for interrupted workflows
  - [ ] Create workflow visualization and debugging tools

## 🚀 Phase 4: Advanced Multi-Step Features

### Enhancement Ideas
- [ ] **Smart Requirement Analysis**
  - [ ] Classify STIG findings by remediation type (package, config, service, etc.)
  - [ ] Extract specific parameters (package names, file paths, configuration values)
  - [ ] Identify dependencies between findings
  - [ ] Generate prerequisite checks

- [ ] **Advanced Playbook Generation**
  - [ ] Generate playbooks with proper error handling
  - [ ] Add pre-task validation checks
  - [ ] Include rollback tasks for safety
  - [ ] Generate handlers for service restarts
  - [ ] Create variables files for customization

- [ ] **Quality Assurance Pipeline**
  - [ ] Implement ansible-lint integration
  - [ ] Add syntax validation at each step
  - [ ] Generate test scenarios for playbooks
  - [ ] Create idempotency verification tests
  - [ ] Add security best practices checking

## 📊 Technical Architecture (NEW)

### LangGraph Workflow Design
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  STIG Finding   │───▶│  Requirement    │───▶│  Ansible Task   │
│  Analysis       │    │  Extraction     │    │  Generation     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Understanding   │    │ Requirements    │    │ Valid Ansible   │
│ + Context       │    │ JSON/YAML       │    │ YAML Task       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Prompt Structure (YAML Format)
```yaml
# prompts/analyze_finding.yaml
name: "analyze_stig_finding"
version: "1.0"
description: "Extract remediation requirements from STIG finding"
template: |
  You are a security compliance expert. Analyze this STIG finding and extract specific remediation requirements.
  
  STIG Finding:
  {finding_data}
  
  Examples:
  {examples}
  
  Output structured requirements as JSON:
  {output_schema}
```

### Multi-Step Benefits
1. **Better Results**: Each step focused on one specific task
2. **Easier Debugging**: Can inspect intermediate outputs
3. **Maintainable Prompts**: YAML format, version controlled
4. **Flexible Workflow**: Can modify steps independently
5. **Example Management**: Easy to update and test examples

## 🔗 Dependencies & Integration

### New Dependencies
- [ ] **LangGraph**: Workflow orchestration
- [ ] **LangChain**: LLM abstraction and tooling
- [ ] **Prompt Management**: YAML parsing, template engine
- [ ] **State Management**: Workflow persistence

### Updated Architecture
- [ ] **Modular Design**: Separate modules for each workflow step
- [ ] **Configuration Management**: YAML-based configuration
- [ ] **Logging & Monitoring**: Detailed workflow tracking
- [ ] **Testing Framework**: Unit tests for each workflow step

## 📈 Success Metrics (UPDATED)

### Phase 3 Goals
- [ ] Multi-step workflow generates higher quality Ansible tasks
- [ ] Improved task specificity and accuracy
- [ ] Better error handling and edge case coverage
- [ ] Maintainable prompt engineering process
- [ ] Faster iteration on prompt improvements

### Quality Improvements Expected
- [ ] More specific and actionable Ansible tasks
- [ ] Better handling of complex STIG requirements
- [ ] Reduced repetition and improved task efficiency
- [ ] Enhanced security best practices in generated tasks
- [ ] Better OS-specific and context-aware adaptations

---

## 🏗️ IMPLEMENTATION PLAN (NEXT CHAT)

### Immediate Next Steps
1. **Set up LangGraph environment** and basic workflow structure
2. **Create prompts/ directory** with initial YAML prompt templates
3. **Implement Step 1**: STIG finding analysis with examples
4. **Implement Step 2**: Requirement-to-Ansible transformation
5. **Test workflow** with existing STIG findings
6. **Iterate on prompts** based on output quality

### Current Status: READY FOR PHASE 3 IMPLEMENTATION
- ✅ **Phase 1 & 2 Complete**: Working STIG parser and basic LLM integration
- ✅ **Foundation Solid**: Can extract 3,058 findings and generate basic tasks
- 🚀 **Next**: Multi-step workflow for dramatically improved task quality

**Priority**: Implement LangGraph multi-step workflow to achieve production-quality Ansible playbook generation.
