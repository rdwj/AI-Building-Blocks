# Additional SCAP Information Available for Extraction

### From XCCDF Rule Definitions:
- **Full Rule Description**: Detailed explanations of what the rule checks
- **Rationale**: Why this security control is important
- **Fix Text**: Detailed remediation instructions
- **Platform Applicability**: Which systems this applies to
- **Remediation Type**: How to fix (configuration, restrict, etc.)
- **Complexity**: Implementation difficulty level

### From XCCDF Rule Elements:
```xml
<xccdf:Rule id="xccdf_org.ssgproject.content_rule_file_groupowner_cron_hourly">
  <xccdf:title>Verify Group Ownership of Cron Hourly Scripts</xccdf:title>
  <xccdf:description>
    <xccdf:p>Files in /etc/cron.hourly/ should be group-owned by root...</xccdf:p>
  </xccdf:description>
  <xccdf:rationale>
    <xccdf:p>Service configuration files should be group-owned by root...</xccdf:p>
  </xccdf:rationale>
  <xccdf:fix system="urn:xccdf:fix:commands">
    chgrp root /etc/cron.hourly/*
  </xccdf:fix>
  <xccdf:fixtext fixref="F-xyz">
    Change group ownership of cron hourly scripts to root...
  </xccdf:fixtext>
  <xccdf:reference href="...">CIS Controls</xccdf:reference>
  <xccdf:ident system="http://cyber.mil">CCI-000366</xccdf:ident>
</xccdf:Rule>
```

### Additional Compliance Mapping:
- **CCI Numbers**: Control Correlation Identifiers
- **NIST References**: SP 800-53 control mappings  
- **CIS Controls**: Center for Internet Security mappings
- **DISA STIG**: Security Technical Implementation Guide IDs
- **PCI DSS**: Payment Card Industry mappings

## For Target Extraction Specifically

### What Your Examples Tell Us:
From `file_groupowner_cron_hourly`, `file_owner_cron_d`, etc., these rules clearly indicate:

- **Target Type**: `file_ownership` or `directory_ownership`
- **Target Path**: `/etc/cron.hourly/`, `/etc/cron.d/`, `/etc/cron.daily/`, etc.
- **Expected Ownership**: `root:root` (owner:group)
- **Action Context**: Change group ownership to root

### Better Target Schema:
```json
{
  "target_type": "file_ownership",
  "target_path": "/etc/cron.hourly/*", 
  "ownership_type": "group",
  "expected_owner": "root",
  "current_status": "fail",
  "ansible_module": "file",
  "ansible_params": {
    "path": "/etc/cron.hourly",
    "group": "root",
    "recurse": true
  }
}
```

## TestResult vs Rule Definition Data

Your extracted findings appear to come from **TestResult** sections, which contain:
- Rule execution results
- Pass/Fail status
- Scan metadata

But you should ALSO extract from **Rule Definition** sections for:
- Detailed descriptions
- Fix instructions  
- Compliance mappings
- Rationales

## Recommended Enhanced Extraction

Extract from BOTH sections and merge:
1. **TestResult data**: Status, severity, scan results
2. **Rule Definition data**: Descriptions, fix text, compliance mappings

This will give you complete information needed for Ansible playbook generation.