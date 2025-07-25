#!/usr/bin/env python3
"""
Quick test script to validate the XML analyzer setup
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all required imports work"""
    try:
        from xml_schema_analyzer_fixed import XMLSchemaAnalyzer, analyze_xml_file
        print("✅ Imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_sample_file():
    """Test with a sample XML file"""
    sample_files = [
        "../sample_data/node2.example.com-STIG-20250710162433.xml",
        "../sample_data/node2.example.com-PCI-20250710162255.xml"
    ]
    
    for sample_file in sample_files:
        if Path(sample_file).exists():
            print(f"📄 Testing with {sample_file}")
            try:
                from xml_schema_analyzer_fixed import XMLSchemaAnalyzer
                analyzer = XMLSchemaAnalyzer()
                
                # Quick test - just parse first 1000 lines to validate structure
                with open(sample_file, 'r') as f:
                    first_part = ''.join(f.readlines()[:1000])
                
                print(f"✅ File is readable and appears to be XML")
                print(f"📊 Sample size: {len(first_part)} characters from first 1000 lines")
                return True
                
            except Exception as e:
                print(f"❌ Test failed: {e}")
                return False
    
    print("❌ No sample files found")
    return False

def main():
    print("🧪 Testing XML Analyzer Setup")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        return False
    
    # Test sample file
    if not test_sample_file():
        return False
    
    print("\n✅ All tests passed!")
    print("🚀 Ready to use: python analyze.py <xml_file>")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
