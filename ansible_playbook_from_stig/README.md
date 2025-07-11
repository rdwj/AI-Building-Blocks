# STIG to Ansible Playbook Generator

Automatically converts STIG (Security Technical Implementation Guide) findings into Ansible playbooks for security remediation.

## 🎯 Project Goals

1. **Parse STIG XML files** to extract security findings
2. **Identify specific violations** and their remediation requirements  
3. **Generate Ansible playbooks** using LLM to address each finding
4. **Automate security compliance** through infrastructure as code

## 🏗️ Architecture

```
STIG XML File → Parser → Findings Extractor → LLM → Ansible Playbooks
```

### Components

- **STIG Parser**: Enhanced XML analyzer for STIG-specific structure
- **Findings Extractor**: Identifies individual security findings/rules
- **LLM Interface**: Calls LLAMA model to generate remediation code  
- **Playbook Generator**: Structures output as valid Ansible playbooks

## 📁 Project Structure

```
ansible_playbook_from_stig/
├── tree.py                 # Project structure viewer
├── README.md               # This file
├── TODO.md                 # Development roadmap
├── requirements.txt        # Dependencies
├── generate_playbooks.py   # Main script
├── src/
│   ├── stig_parser.py      # STIG-specific XML parser
│   ├── findings_extractor.py  # Extract individual findings
│   ├── llm_interface.py    # LLM API integration
│   └── playbook_generator.py  # Ansible playbook creation
├── findings/               # Extracted findings (JSON)
├── playbooks/              # Generated Ansible playbooks
└── examples/               # Sample inputs/outputs
```

## 🚀 Usage (Planned)

```bash
# Generate playbooks from STIG file
python generate_playbooks.py ../xml_files/sample_data/node2.example.com-STIG-20250710162433.xml

# Generate playbooks for specific findings
python generate_playbooks.py stig_file.xml --finding-id RHEL-07-010010

# Batch process multiple STIG files
python generate_playbooks.py *.xml --output-dir ./playbooks
```

## 🔍 STIG Finding Structure

STIG files contain findings with:
- **Rule ID**: Unique identifier (e.g., RHEL-07-010010)
- **Severity**: Critical/High/Medium/Low
- **Title**: Brief description
- **Description**: Detailed explanation
- **Check Text**: How to verify compliance
- **Fix Text**: Manual remediation steps
- **References**: Related standards (CCI, NIST, etc.)

## 🤖 LLM Integration

Uses local LLAMA model (LLAMA_3_2_URL from .env) to:
1. Analyze finding descriptions and fix text
2. Generate appropriate Ansible tasks
3. Create complete playbooks with:
   - Proper task structure
   - Conditionals and handlers
   - Error handling
   - Documentation

## 📊 Example Output

Input: STIG finding about password complexity
Output: Ansible playbook with tasks to configure PAM, set password policies, etc.

## 🔗 Integration

Links with existing XML parser project at:
`../xml_files/` - Leverages enhanced XML analysis capabilities

## 📋 Status

🚧 **In Development** - See TODO.md for current roadmap

## 🛠️ Dependencies

- Python 3.7+
- requests (for LLM API calls)
- PyYAML (for Ansible playbook generation)
- Enhanced XML parser from ../xml_files/

## 🤝 Contributing

This is part of a larger AI building blocks framework for security automation.

---

**Next Steps**: See TODO.md for development priorities
