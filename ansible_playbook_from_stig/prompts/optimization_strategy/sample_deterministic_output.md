---
# STIG Compliance Remediation Playbook
# Generated automatically on 2025-01-12 15:45:30
# DO NOT EDIT MANUALLY - Regenerate from STIG targets

- name: STIG Compliance Remediation Playbook
  hosts: all
  become: true
  gather_facts: true
  vars:
    stig_remediation_date: '2025-01-12T15:45:30'
    total_remediations: 435
    
  tasks:
    - name: Display STIG remediation information
      debug:
        msg:
          - Starting STIG compliance remediation
          - 'Total remediations: {{ total_remediations }}'
          - 'Generated on: {{ stig_remediation_date }}'
      tags: [info]

    # === PACKAGES REMOVE ===
    - name: "=== Packages Remove ==="
      debug:
        msg: Starting packages remove remediation
      tags: [packages_remove, info]

    - name: 'CCE-86562-6: Package "prelink" Must not be Installed'
      yum:
        name: prelink
        state: absent
      tags: [stig, security, packages_remove, severity_medium, packages, cce_86562_6]

    - name: Remove the GDM Package Group
      yum:
        name: gdm
        state: absent
      tags: [stig, security, packages_remove, severity_medium, packages]

    - name: Remove the X Windows Package Group
      yum:
        name: xorg-x11-server-common
        state: absent
      tags: [stig, security, packages_remove, severity_medium, packages, cce_27218_7]

    # === PACKAGES INSTALL ===
    - name: "=== Packages Install ==="
      debug:
        msg: Starting packages install remediation
      tags: [packages_install, info]

    - name: 'CCE-27096-7: Install AIDE'
      yum:
        name: aide
        state: present
      tags: [stig, security, packages_install, severity_medium, packages, cce_27096_7]

    - name: 'CCE-80358-5: Install the dracut-fips Package'
      yum:
        name: dracut-fips
        state: present
      tags: [stig, security, packages_install, severity_medium, packages, cce_80358_5]

    - name: 'CCE-81042-4: Ensure the audit Subsystem is Installed'
      yum:
        name: audit
        state: present
      tags: [stig, security, packages_install, severity_medium, packages, cce_81042_4]

    # === SERVICES ===
    - name: "=== Services ==="
      debug:
        msg: Starting services remediation
      tags: [services, info]

    - name: Enable nails Service
      systemd:
        name: nails
        state: started
        enabled: true
      tags: [stig, security, services, severity_medium, services, cce_80128_2]

    - name: 'CCE-80363-5: Enable the SSSD Service'
      systemd:
        name: sssd
        state: started
        enabled: true
      tags: [stig, security, services, severity_medium, services, cce_80363_5]

    - name: 'CCE-27407-6: Enable auditd Service'
      systemd:
        name: auditd
        state: started
        enabled: true
      tags: [stig, security, services, severity_medium, services, cce_27407_6]

    # === FILE OWNERSHIP ===
    - name: "=== File Ownership ==="
      debug:
        msg: Starting file ownership remediation
      tags: [file_ownership, info]

    - name: 'CCE-82902-8: Verify Group Who Owns SSH Server config file'
      file:
        path: /etc/ssh/sshd_config
        group: root
        recurse: false
      register: file_ownership_etc_ssh_sshd_config_result
      notify: [restart sshd]
      tags: [stig, security, file_ownership, severity_medium, file_security, cce_82902_8]

    - name: 'CCE-82899-6: Verify Owner on SSH Server config file'
      file:
        path: /etc/ssh/sshd_config
        owner: root
        recurse: false
      register: file_ownership_etc_ssh_sshd_config_result2
      notify: [restart sshd]
      tags: [stig, security, file_ownership, severity_medium, file_security, cce_82899_6]

    # === FILE PERMISSIONS ===
    - name: "=== File Permissions ==="
      debug:
        msg: Starting file permissions remediation
      tags: [file_permissions, info]

    - name: 'CCE-82895-4: Verify Permissions on SSH Server config file'
      file:
        path: /etc/ssh/sshd_config
        mode: '600'
      register: file_permission_etc_ssh_sshd_config_result
      notify: [restart sshd]
      tags: [stig, security, file_permissions, severity_medium, file_security, cce_82895_4]

    - name: 'CCE-88763-8: Audit Configuration Files Permissions are 640 or More Restrictive'
      file:
        path: /etc/audit/configuration
        mode: '640'
      register: file_permission_etc_audit_configuration_result
      notify: [restart auditd]
      tags: [stig, security, file_permissions, severity_medium, file_security, cce_88763_8]

    # === SYSCTL ===
    - name: "=== Sysctl ==="
      debug:
        msg: Starting sysctl remediation
      tags: [sysctl, info]

    - name: Configure kernel parameter for network security
      sysctl:
        name: net.ipv4.ip_forward
        value: '0'
        state: present
        reload: true
      tags: [stig, security, sysctl, severity_medium, kernel_parameters]

    # === MOUNTS ===
    - name: "=== Mounts ==="
      debug:
        msg: Starting mounts remediation
      tags: [mounts, info]

    - name: 'CCE-86889-3: Ensure tmp.mount Unit Us Enabled'
      mount:
        path: /tmp
        opts: defaults
        state: mounted
      tags: [stig, security, mounts, severity_low, cce_86889_3]

  handlers:
    - name: restart sshd
      systemd:
        name: sshd
        state: restarted
      listen: restart sshd

    - name: restart auditd
      systemd:
        name: auditd
        state: restarted
      listen: restart auditd