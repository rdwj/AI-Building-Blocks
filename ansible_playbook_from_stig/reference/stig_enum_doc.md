# Comprehensive STIG Action Types for All Platforms

## Complete JSON Schema

```json
{
  "type": "object",
  "properties": {
    "action_type": {
      "type": "string",
      "enum": [
        "install_package",
        "remove_package",
        "update_package",
        "configure_file",
        "create_file",
        "remove_file",
        "set_permission",
        "configure_service",
        "enable_service",
        "disable_service",
        "start_service",
        "stop_service",
        "configure_user",
        "create_user",
        "remove_user",
        "configure_group",
        "create_group",
        "remove_group",
        "configure_audit",
        "configure_logging",
        "configure_ssh",
        "configure_pam",
        "configure_selinux",
        "configure_apparmor",
        "configure_firewall",
        "configure_network",
        "configure_mount",
        "configure_grub",
        "configure_sysctl",
        "configure_cron",
        "configure_limits",
        "configure_password_policy",
        "configure_login_banner",
        "configure_sudo",
        "configure_tcp_wrappers",
        "configure_kernel_module",
        "configure_certificate",
        "configure_encryption",
        "configure_registry",
        "configure_gpo",
        "configure_user_rights",
        "configure_security_policy",
        "configure_web_server",
        "configure_database",
        "configure_dns",
        "configure_mail_server",
        "configure_ftp_server",
        "configure_ldap",
        "configure_active_directory",
        "configure_cloud_storage",
        "configure_cloud_network",
        "configure_cloud_iam",
        "configure_container",
        "configure_kubernetes",
        "configure_virtualization",
        "configure_backup",
        "configure_monitoring",
        "configure_antivirus",
        "configure_patch_management",
        "configure_vulnerability_scanner",
        "configure_intrusion_detection",
        "execute_command",
        "verify_configuration",
        "verify_compliance",
        "other"
      ]
    }
  },
  "required": ["action_type"]
}
```

## Action Type Categories and Definitions

### Package Management

* **`install_package`** - Install required security software
* **`remove_package`** - Remove prohibited or vulnerable packages
* **`update_package`** - Update packages to secure versions

### File Operations

* **`configure_file`** - Modify configuration files (most common)
* **`create_file`** - Create required files (banners, policies, etc.)
* **`remove_file`** - Delete prohibited or insecure files
* **`set_permission`** - Set file/directory permissions and ownership

### Service Management

* **`configure_service`** - Modify service configuration
* **`enable_service`** - Enable required services
* **`disable_service`** - Disable prohibited services
* **`start_service`** - Start required services
* **`stop_service`** - Stop insecure services

### User and Group Management

* **`configure_user`** - Modify user account properties
* **`create_user`** - Create required system accounts
* **`remove_user`** - Remove prohibited accounts
* **`configure_group`** - Modify group properties
* **`create_group`** - Create required groups
* **`remove_group`** - Remove unnecessary groups

### Security Subsystems

* **`configure_audit`** - Audit daemon rules and configuration
* **`configure_logging`** - System logging configuration
* **`configure_ssh`** - SSH daemon and client hardening
* **`configure_pam`** - Pluggable Authentication Modules
* **`configure_selinux`** - SELinux policies and booleans
* **`configure_apparmor`** - AppArmor profile configuration

### Network Security

* **`configure_firewall`** - Firewall rules and policies
* **`configure_network`** - Network interface and protocol settings
* **`configure_tcp_wrappers`** - hosts.allow/hosts.deny configuration

### System Configuration

* **`configure_mount`** - Filesystem mount options
* **`configure_grub`** - Bootloader security settings
* **`configure_sysctl`** - Kernel parameters
* **`configure_cron`** - Scheduled task management
* **`configure_limits`** - System resource limits
* **`configure_kernel_module`** - Load/blacklist kernel modules

### Authentication and Access Control

* **`configure_password_policy`** - Password complexity requirements
* **`configure_login_banner`** - Login warning messages
* **`configure_sudo`** - Sudo access and restrictions

### Cryptography

* **`configure_certificate`** - SSL/TLS certificate management
* **`configure_encryption`** - Encryption settings and policies

### Windows-Specific

* **`configure_registry`** - Windows registry modifications
* **`configure_gpo`** - Group Policy settings
* **`configure_user_rights`** - User rights assignments
* **`configure_security_policy`** - Local security policies

### Application Services

* **`configure_web_server`** - Apache, Nginx, IIS hardening
* **`configure_database`** - Database security settings
* **`configure_dns`** - DNS server configuration
* **`configure_mail_server`** - Email server security
* **`configure_ftp_server`** - FTP/SFTP server settings
* **`configure_ldap`** - LDAP directory services
* **`configure_active_directory`** - Active Directory settings

### Cloud Platforms

* **`configure_cloud_storage`** - S3, Azure Storage, GCS settings
* **`configure_cloud_network`** - VPC, security groups, firewalls
* **`configure_cloud_iam`** - Cloud identity and access management

### Modern Infrastructure

* **`configure_container`** - Docker container security
* **`configure_kubernetes`** - Kubernetes cluster hardening
* **`configure_virtualization`** - VMware, Hyper-V settings

### Security Tools

* **`configure_backup`** - Backup system configuration
* **`configure_monitoring`** - Security monitoring setup
* **`configure_antivirus`** - Antivirus/anti-malware settings
* **`configure_patch_management`** - Patch management systems
* **`configure_vulnerability_scanner`** - Vulnerability scanning tools
* **`configure_intrusion_detection`** - IDS/IPS configuration

### Execution and Verification

* **`execute_command`** - Run commands for complex configurations
* **`verify_configuration`** - Validate system settings
* **`verify_compliance`** - Check compliance status

### Fallback

* **`other`** - Actions not fitting other categories

## Platform Coverage

This taxonomy covers STIGs for:

### Operating Systems

* Windows (Server 2016/2019/2022, Windows 10/11)
* Linux (RHEL, Ubuntu, SUSE, Amazon Linux)
* macOS
* VMware ESXi
* Cisco IOS
* Network device operating systems

### Applications

* Web servers (Apache, Nginx, IIS)
* Databases (Oracle, SQL Server, MySQL, PostgreSQL)
* Mail servers (Exchange, Postfix)
* DNS servers (BIND, Windows DNS)
* FTP servers
* Directory services (Active Directory, OpenLDAP)

### Cloud Platforms

* AWS services
* Microsoft Azure
* Google Cloud Platform
* Cloud security configurations

### Infrastructure

* Docker containers
* Kubernetes
* VMware vSphere
* Network devices (Cisco, Juniper, etc.)

## Expected Coverage

With these  **64 action types** , you should be able to categorize **95-98%** of all DISA STIG findings across:

* ✅ All major operating systems
* ✅ Network infrastructure devices
* ✅ Database systems
* ✅ Web and application servers
* ✅ Cloud platforms and services
* ✅ Container and virtualization platforms
* ✅ Security tools and appliances

The remaining 2-5% would fall into **`other`** for truly unique or complex multi-step procedures that don't fit standard patterns.
