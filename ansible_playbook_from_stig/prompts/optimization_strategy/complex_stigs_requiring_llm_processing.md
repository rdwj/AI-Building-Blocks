# Complex STIG Findings Requiring LLM Processing

Based on your data showing **1,094 "unknown" targets** out of 1,529 total findings, here are realistic examples of STIG findings that need LLM analysis:

## 🔍 **Example 1: Audit Rules (Content-Based Configuration)**

### **Finding Data:**
```json
{
  "rule_id": "xccdf_org.ssgproject.content_rule_audit_rules_unsuccessful_file_modification",
  "title": "Record Unsuccessful Access Attempts to Files - open",
  "description": "At a minimum, the audit system should collect unauthorized file accesses for all users and root. Add the following to /etc/audit/rules.d/audit.rules...",
  "fix_text": "Add the following rules to /etc/audit/rules.d/audit.rules: -a always,exit -F arch=b64 -S open -F exit=-EACCES -F auid>=1000 -F auid!=4294967295 -k access",
  "target_info": {
    "target_type": "unknown",
    "ansible_module": "debug"
  }
}
```

### **Why It Needs LLM:**
- **Complex rule parsing**: Need to extract specific audit rule syntax
- **Architecture detection**: Rules differ for b32 vs b64
- **Multiple rule variations**: Different patterns for different syscalls
- **Content injection**: Not just file ownership, but specific content to add

### **LLM Would Extract:**
```json
{
  "target_type": "audit_rule",
  "target_name": "/etc/audit/rules.d/audit.rules",
  "ansible_module": "lineinfile",
  "ansible_params": {
    "path": "/etc/audit/rules.d/audit.rules",
    "line": "-a always,exit -F arch=b64 -S open -F exit=-EACCES -F auid>=1000 -F auid!=4294967295 -k access",
    "create": true
  }
}
```

## 🔍 **Example 2: GRUB Configuration (Multi-Step Process)**

### **Finding Data:**
```json
{
  "rule_id": "xccdf_org.ssgproject.content_rule_grub2_password",
  "title": "Set Boot Loader Password",
  "description": "The grub2 boot loader should have a superuser account and password protection enabled to protect boot-time settings...",
  "fix_text": "Configure the system to encrypt the boot password. Generate an encrypted password hash: grub2-setpassword. Then add or modify the following line in /etc/grub.d/40_custom...",
  "target_info": {
    "target_type": "unknown",
    "ansible_module": "debug"
  }
}
```

### **Why It Needs LLM:**
- **Multi-step process**: Generate password hash THEN modify config
- **Command execution**: Need to run `grub2-setpassword`
- **Complex file modification**: Multiple files involved
- **Conditional logic**: Different steps for UEFI vs BIOS

### **LLM Would Extract:**
```json
{
  "target_type": "grub_configuration",
  "target_name": "grub2_password",
  "ansible_module": "shell",
  "multi_step": true,
  "ansible_params": {
    "cmd": "grub2-setpassword && grub2-mkconfig -o /boot/grub2/grub.cfg"
  }
}
```

## 🔍 **Example 3: PAM Configuration (Content-Based)**

### **Finding Data:**
```json
{
  "rule_id": "xccdf_org.ssgproject.content_rule_accounts_password_pam_retry",
  "title": "Set Password Retry Prompts Permitted Per-Session",
  "description": "To configure the number of retry prompts that are permitted per-session, modify the content of the pam_pwquality line in /etc/pam.d/system-auth...",
  "fix_text": "Edit the /etc/pam.d/system-auth file to include the argument retry=3 after pam_pwquality.so, such as: password requisite pam_pwquality.so retry=3",
  "target_info": {
    "target_type": "unknown",
    "ansible_module": "debug"
  }
}
```

### **Why It Needs LLM:**
- **Line modification**: Not adding a line, but modifying existing
- **Parameter extraction**: Need to extract `retry=3` from description
- **PAM syntax understanding**: Complex PAM module configuration
- **Multiple file targets**: Could be system-auth, password-auth, etc.

### **LLM Would Extract:**
```json
{
  "target_type": "pam_configuration",
  "target_name": "/etc/pam.d/system-auth",
  "ansible_module": "pamd",
  "ansible_params": {
    "name": "system-auth",
    "type": "password",
    "control": "requisite", 
    "module_path": "pam_pwquality.so",
    "module_arguments": "retry=3",
    "state": "args_present"
  }
}
```

## 🔍 **Example 4: Network Configuration (Complex Logic)**

### **Finding Data:**
```json
{
  "rule_id": "xccdf_org.ssgproject.content_rule_sysctl_net_ipv4_conf_all_accept_redirects",
  "title": "Disable Accepting ICMP Redirects for All IPv4 Interfaces",
  "description": "For each interface on the system, run: sysctl net.ipv4.conf.[interface].accept_redirects or verify with: grep net.ipv4.conf.all.accept_redirects /etc/sysctl.conf",
  "fix_text": "Add or update the following line in /etc/sysctl.conf: net.ipv4.conf.all.accept_redirects = 0. Run sysctl -p to apply immediately.",
  "target_info": {
    "target_type": "sysctl",
    "target_name": "net.ipv4.conf.all.accept_redirects",
    "ansible_params": {
      "name": "net.ipv4.conf.all.accept_redirects",
      "value": "1"  // ❌ WRONG VALUE EXTRACTED!
    }
  }
}
```

### **Why Original Parser Failed:**
- **Value extraction**: Deterministic parser defaulted to "1" instead of reading "0" from fix_text
- **Multiple interfaces**: Rule mentions "for each interface" - needs iteration
- **Immediate application**: Needs `sysctl -p` after modification

### **LLM Would Extract:**
```json
{
  "target_type": "sysctl",
  "target_name": "net.ipv4.conf.all.accept_redirects", 
  "ansible_module": "sysctl",
  "ansible_params": {
    "name": "net.ipv4.conf.all.accept_redirects",
    "value": "0",
    "state": "present",
    "reload": true,
    "sysctl_file": "/etc/sysctl.conf"
  }
}
```

## 🔍 **Example 5: Firewall Rules (Complex Syntax)**

### **Finding Data:**
```json
{
  "rule_id": "xccdf_org.ssgproject.content_rule_firewalld_loopback_traffic_trusted",
  "title": "Configure Firewall to Allow Local Loopback Traffic",
  "description": "Configure the firewall to allow loopback traffic. Run: firewall-cmd --permanent --add-rich-rule='rule family=\"ipv4\" source address=\"127.0.0.1\" accept'",
  "fix_text": "Run the following commands: firewall-cmd --permanent --add-rich-rule='rule family=\"ipv4\" source address=\"127.0.0.1\" accept' && firewall-cmd --reload",
  "target_info": {
    "target_type": "unknown",
    "ansible_module": "debug"
  }
}
```

### **Why It Needs LLM:**
- **Complex firewall syntax**: Rich rules with embedded quotes
- **Command chaining**: Multiple firewall-cmd commands
- **XML escaping**: Need to handle quotes properly in YAML
- **State management**: Permanent + reload pattern

### **LLM Would Extract:**
```json
{
  "target_type": "firewall_rule",
  "target_name": "loopback_traffic",
  "ansible_module": "firewalld",
  "ansible_params": {
    "rich_rule": "rule family=\"ipv4\" source address=\"127.0.0.1\" accept",
    "permanent": true,
    "state": "enabled",
    "immediate": true
  }
}
```

## 📊 **Summary: When You Need LLM**

| Pattern | Deterministic Can Handle | Needs LLM |
|---------|-------------------------|-----------|
| `package_*` | ✅ Perfect | ❌ No |
| `service_*` | ✅ Perfect | ❌ No |
| `file_owner_*` | ✅ Perfect | ❌ No |
| `sysctl_*` | ⚠️ Basic values | ✅ Complex values |
| `audit_rules_*` | ❌ No | ✅ Always |
| `grub2_*` | ❌ No | ✅ Always |
| `accounts_password_*` | ❌ No | ✅ Always |
| `firewalld_*` | ❌ No | ✅ Always |
| Content modification | ❌ No | ✅ Always |
| Multi-step processes | ❌ No | ✅ Always |

**Your 1,094 "unknown" targets likely include:**
- ~300 audit rules (complex syscall patterns)
- ~200 PAM/password configurations 
- ~150 GRUB/boot configurations
- ~100 firewall rules
- ~200 content-based file modifications
- ~144 miscellaneous complex configurations

These genuinely need LLM processing to understand the intent and extract proper Ansible parameters!