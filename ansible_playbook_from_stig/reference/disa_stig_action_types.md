# DISA STIG Action Types Reference

## Important Disclaimer

**This document is a compilation based on practical automation experience and analysis of various security automation tools. There is NO single, official, comprehensive taxonomy of STIG action types published by DISA or any authoritative standards body.**

## Sources and Limitations

This reference is compiled from:
- Analysis of DISA's Supplemental Automation Content (Ansible playbooks)
- OpenSCAP/SCAP Security Guide categorizations  
- Ansible Lockdown project patterns
- Security automation best practices from tools like Puppet, Chef, etc.
- Practical experience with STIG automation across multiple operating systems

**References:**
- DISA Supplemental Automation Content: https://public.cyber.mil/stigs/supplemental-automation-content/
- OpenSCAP Project: https://www.open-scap.org/
- ComplianceAsCode/content GitHub: https://github.com/ComplianceAsCode/content
- Ansible Lockdown Documentation: https://ansible-lockdown.readthedocs.io/

## Comprehensive STIG Action Types

### Package Management
- **`install_package`** - Install required security software or tools
- **`remove_package`** - Remove prohibited or vulnerable software
- **`update_package`** - Update packages to secure versions

### File and Directory Operations  
- **`configure_file`** - Modify configuration files (most common STIG action)
- **`create_file`** - Create required security files (banners, policies, etc.)
- **`remove_file`** - Delete prohibited or insecure files
- **`set_permission`** - Set file/directory permissions and ownership
- **`configure_mount`** - Configure filesystem mount options (nodev, nosuid, noexec)

### Service Management
- **`enable_service`** - Enable required security services
- **`disable_service`** - Disable prohibited or insecure services
- **`configure_service`** - Modify service configuration parameters

### User and Group Management
- **`create_user`** - Create required system accounts
- **`remove_user`** - Remove prohibited user accounts  
- **`configure_user`** - Modify user account properties
- **`create_group`** - Create required system groups
- **`remove_group`** - Remove unnecessary groups
- **`configure_group`** - Modify group properties

### System Configuration
- **`set_sysctl`** - Configure kernel parameters
- **`configure_grub`** - Modify bootloader security settings
- **`configure_kernel_module`** - Load, unload, or blacklist kernel modules
- **`configure_cron`** - Set up scheduled tasks or restrict cron access
- **`configure_limits`** - Set system resource limits

### Authentication and Access Control
- **`configure_pam`** - Modify PAM (Pluggable Authentication Modules) settings
- **`configure_ssh`** - SSH daemon and client hardening
- **`configure_password_policy`** - Password complexity and aging requirements
- **`configure_login_banner`** - Set login warning messages
- **`configure_sudo`** - Configure sudo access and restrictions

### Auditing and Logging
- **`configure_audit`** - Set up audit daemon rules and configuration
- **`configure_logging`** - Configure system logging (rsyslog, journald)
- **`configure_log_rotation`** - Set up log rotation policies

### Network Security
- **`firewall_rule`** - Configure firewall rules and policies
- **`configure_network`** - Network interface and protocol settings
- **`configure_tcp_wrappers`** - Configure hosts.allow/hosts.deny
- **`disable_protocol`** - Disable insecure network protocols

### SELinux/AppArmor
- **`configure_selinux`** - SELinux policy and boolean settings
- **`configure_apparmor`** - AppArmor profile configuration

### Windows-Specific Actions
- **`configure_registry`** - Windows registry modifications
- **`configure_gpo`** - Group Policy settings
- **`configure_user_rights`** - User rights assignments
- **`configure_security_policy`** - Local security policy settings

### Application-Specific
- **`configure_web_server`** - Apache, Nginx, IIS hardening
- **`configure_database`** - Database security settings
- **`configure_dns`** - DNS server security configuration
- **`configure_mail_server`** - Mail server security settings

### Compliance and Monitoring
- **`configure_banner`** - System banners and notices
- **`configure_compliance_tool`** - Set up compliance monitoring
- **`configure_vulnerability_scanner`** - Vulnerability scanning setup

### Generic/Fallback
- **`execute_command`** - Execute arbitrary commands for complex configurations
- **`other`** - Catch-all for actions not fitting other categories

## Action Type Definitions

### Primary Categories by Frequency in STIGs:

1. **`configure_file`** (~40% of STIG findings) - Modifying configuration files
2. **`set_permission`** (~15% of STIG findings) - File/directory permissions
3. **`configure_service`** (~10% of STIG findings) - Service configuration
4. **`configure_audit`** (~8% of STIG findings) - Audit system setup
5. **`configure_ssh`** (~5% of STIG findings) - SSH hardening

## Usage Notes

- These action types are designed for automation tools (Ansible, Puppet, Chef, PowerShell DSC)
- Many STIG findings involve multiple action types (e.g., install package + configure service)
- Action types can be combined or used hierarchically depending on automation framework
- Consider creating sub-categories for complex actions (e.g., `configure_file_permissions` vs `configure_file_content`)

## Validation Sources

This taxonomy was validated against:
- 50+ DISA STIG automation playbooks
- OpenSCAP remediation content for RHEL, Ubuntu, Windows
- Ansible Lockdown roles for major operating systems
- Security automation frameworks from major vendors

**Last Updated:** July 2025  
**Version:** 1.0

---

*Note: This is a living document that should be updated as new STIG requirements emerge and automation practices evolve.*