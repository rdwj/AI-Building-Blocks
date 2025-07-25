---
# Ansible Playbook Generated from STIG Finding
# Rule: xccdf_org.ssgproject.content_rule_file_groupowner_sshd_config
# Title: Verify Group Who Owns SSH Server config file
# Severity: medium
# Compliance: CCE-82902-8

- name: "STIG Remediation: SSH Server Configuration File Security"
  hosts: rhel7_servers
  become: yes
  gather_facts: no
  
  tasks:
    - name: "CCE-82902-8: Verify Group Who Owns SSH Server config file"
      ansible.builtin.file:
        path: "/etc/ssh/sshd_config"
        group: "root"
        recurse: false
      register: sshd_config_group_result
      
    - name: "Display remediation result"
      ansible.builtin.debug:
        msg: |
          SSH configuration file group ownership remediated:
          - File: /etc/ssh/sshd_config  
          - Group: root
          - Changed: {{ sshd_config_group_result.changed }}
          
    - name: "Restart SSH service if config was modified"
      ansible.builtin.systemd:
        name: sshd
        state: restarted
      when: sshd_config_group_result.changed
      
  tags:
    - stig
    - security
    - ssh
    - file_permissions
    - cce-82902-8