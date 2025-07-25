#!/usr/bin/env python3
"""
Configuration settings for STIG to Ansible Playbook Generator
Adjust these values based on your GPU capacity and performance requirements
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GPU and Performance Settings
# Adjust MAX_CONCURRENT_REQUESTS based on your GPU capacity:
# - 1: Small GPU (< 8GB VRAM) or limited resources
# - 3-5: Medium GPU (8-16GB VRAM) 
# - 10+: Large GPU (16GB+ VRAM) or powerful hardware
MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', '1'))

# Processing limits
MAX_FINDINGS_PER_RUN = int(os.getenv('MAX_FINDINGS_PER_RUN', '50'))  # Use existing setting

# Batch processing settings
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '5'))
INTER_BATCH_DELAY = float(os.getenv('INTER_BATCH_DELAY', '1.0'))

# LLM Settings
LLM_TIMEOUT = int(os.getenv('LLM_REQUEST_TIMEOUT', '30'))  # Use existing LLM_REQUEST_TIMEOUT
LLM_MAX_RETRIES = int(os.getenv('LLM_MAX_RETRIES', '3'))
LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.3'))

# Workflow Settings
ENABLE_STEP_4_DOCUMENTATION = os.getenv('ENABLE_STEP_4_DOCUMENTATION', 'true').lower() == 'true'
ENABLE_DEBUG_OUTPUT = os.getenv('ENABLE_DEBUG_OUTPUT', 'false').lower() == 'true'

# Output Settings
OUTPUT_BASE_DIR = os.getenv('OUTPUT_DIR', './playbooks')  # Use existing OUTPUT_DIR from .env
PRESERVE_FAILED_OUTPUTS = os.getenv('PRESERVE_FAILED_OUTPUTS', 'true').lower() == 'true'

def get_config_summary():
    """Get a summary of current configuration"""
    return {
        'performance': {
            'max_concurrent_requests': MAX_CONCURRENT_REQUESTS,
            'max_findings_per_run': MAX_FINDINGS_PER_RUN,
            'batch_size': BATCH_SIZE,
            'inter_batch_delay': INTER_BATCH_DELAY
        },
        'llm': {
            'timeout': LLM_TIMEOUT,
            'max_retries': LLM_MAX_RETRIES,
            'temperature': LLM_TEMPERATURE
        },
        'workflow': {
            'enable_documentation': ENABLE_STEP_4_DOCUMENTATION,
            'enable_debug': ENABLE_DEBUG_OUTPUT
        },
        'output': {
            'base_directory': OUTPUT_BASE_DIR,
            'preserve_failed_outputs': PRESERVE_FAILED_OUTPUTS
        }
    }

def print_config():
    """Print current configuration to console"""
    config = get_config_summary()
    
    print("🔧 Current Configuration:")
    print("=" * 40)
    
    print("\n📊 Performance Settings:")
    print(f"  Max Concurrent Requests: {config['performance']['max_concurrent_requests']}")
    print(f"  Max Findings Per Run: {config['performance']['max_findings_per_run']}")
    print(f"  Batch Size: {config['performance']['batch_size']}")
    print(f"  Inter-batch Delay: {config['performance']['inter_batch_delay']}s")
    
    print("\n🤖 LLM Settings:")
    print(f"  Timeout: {config['llm']['timeout']}s")
    print(f"  Max Retries: {config['llm']['max_retries']}")
    print(f"  Temperature: {config['llm']['temperature']}")
    
    print("\n⚙️  Workflow Settings:")
    print(f"  Documentation Step: {'Enabled' if config['workflow']['enable_documentation'] else 'Disabled'}")
    print(f"  Debug Output: {'Enabled' if config['workflow']['enable_debug'] else 'Disabled'}")
    
    print("\n📁 Output Settings:")
    print(f"  Base Directory: {config['output']['base_directory']}")
    print(f"  Preserve Failed Outputs: {'Yes' if config['output']['preserve_failed_outputs'] else 'No'}")
    
    print("\n💡 To change settings, modify your .env file or set environment variables:")
    print("   export MAX_CONCURRENT_REQUESTS=3")
    print("   export BATCH_SIZE=10")
    print("   export INTER_BATCH_DELAY=0.5")

if __name__ == "__main__":
    print_config()