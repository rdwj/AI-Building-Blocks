#!/usr/bin/env python3
"""
STIG to Ansible Playbook Generator - Main Script

Usage: python generate_playbooks.py <stig_file.xml>
"""

import sys
import os
from pathlib import Path

# Add the XML parser project to path
xml_parser_path = Path(__file__).parent.parent / "xml_files" / "src"
sys.path.append(str(xml_parser_path))

def main():
    """Main entry point for STIG playbook generation"""
    
    print("🔧 STIG to Ansible Playbook Generator")
    print("=" * 50)
    
    if len(sys.argv) != 2:
        print("Usage: python generate_playbooks.py <stig_file.xml>")
        print("\nExample:")
        print("  python generate_playbooks.py ../xml_files/sample_data/node2.example.com-STIG-20250710162433.xml")
        sys.exit(1)
    
    stig_file = sys.argv[1]
    
    if not Path(stig_file).exists():
        print(f"❌ Error: File not found: {stig_file}")
        sys.exit(1)
    
    print(f"📄 Processing STIG file: {Path(stig_file).name}")
    print("⚠️  This is a placeholder - implementation needed!")
    print("\n📋 TODO:")
    print("  1. Parse STIG XML file")
    print("  2. Extract findings/rules")  
    print("  3. Generate Ansible playbooks via LLM")
    print("  4. Save playbooks to ./playbooks/")
    
    print(f"\n🔗 See TODO.md for development roadmap")

if __name__ == "__main__":
    main()
