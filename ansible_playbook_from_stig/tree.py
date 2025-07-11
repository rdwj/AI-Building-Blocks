#!/usr/bin/env python3
"""
Generate project tree structure
"""

import os
from pathlib import Path

def print_tree(directory, prefix="", max_depth=3, current_depth=0):
    """Print directory tree structure"""
    if current_depth >= max_depth:
        return
    
    directory = Path(directory)
    items = sorted(directory.iterdir(), key=lambda x: (x.is_file(), x.name))
    
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        
        # Print current item
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{item.name}")
        
        # Recurse into directories
        if item.is_dir() and not item.name.startswith('.'):
            extension = "    " if is_last else "│   "
            print_tree(item, prefix + extension, max_depth, current_depth + 1)

if __name__ == "__main__":
    print("STIG to Ansible Playbook Generator")
    print("=" * 50)
    current_dir = Path(__file__).parent
    print(f"Project structure for: {current_dir}")
    print()
    print_tree(current_dir)
