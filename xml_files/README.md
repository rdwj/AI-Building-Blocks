# XML Document Analyzer

A simple tool for analyzing XML documents and preparing them for LLM processing.

## Quick Start

```bash
python analyze.py sample_data/node2.example.com-STIG-20250710162433.xml
```

## What It Does

- **Analyzes XML structure**: Elements, attributes, namespaces, hierarchy
- **Detects document type**: SCAP, XCCDF, OVAL, etc.
- **Generates statistics**: Element counts, depths, relationships  
- **Creates LLM-ready summary**: Structured description for AI processing
- **Saves results**: JSON output for programmatic use

## Usage

```bash
python analyze.py <xml_file>
```

### Examples

```bash
# Analyze STIG compliance report
python analyze.py sample_data/node2.example.com-STIG-20250710162433.xml

# Analyze PCI compliance report  
python analyze.py sample_data/node2.example.com-PCI-20250710162255.xml

# Analyze any XML file
python analyze.py /path/to/your/file.xml
```

## Output

The tool provides:

1. **Console output**: Human-readable analysis summary
2. **JSON file**: Machine-readable results (`filename_analysis.json`)

### Sample Output

```
📄 Analyzing: node2.example.com-STIG-20250710162433.xml
📊 Size: 31.5 MB
⏳ Processing...
✅ Analysis Complete!
============================================================
📄 File: node2.example.com-STIG-20250710162433.xml
📊 Size: 31.5 MB

📋 Document Structure:
   Root Element: asset-report-collection
   Total Elements: 125,347
   Unique Elements: 89
   Max Depth: 12
   Namespaces: 15

⏱️  Processed in 2.34 seconds

🔍 Detailed Analysis:
----------------------------------------
XML Document Schema Analysis

Document Type: asset-report-collection
Total Elements: 125,347
Maximum Depth: 12
...
```

## Files

- `analyze.py` - Main script
- `src/` - Core analysis modules
- `sample_data/` - Example XML files
- `requirements.txt` - Dependencies (none required)

## Advanced Usage

For programmatic access:

```python
import sys
sys.path.append('src')
from xml_schema_analyzer import XMLSchemaAnalyzer

analyzer = XMLSchemaAnalyzer()
schema = analyzer.analyze_file('your_file.xml')
description = analyzer.generate_llm_description(schema)
```

## Supported Document Types

- **SCAP**: Security Content Automation Protocol
- **XCCDF**: Extensible Configuration Checklist Description Format
- **OVAL**: Open Vulnerability and Assessment Language
- **STIG**: Security Technical Implementation Guides
- **Generic XML**: Any well-formed XML document

## Requirements

- Python 3.7+
- No external dependencies (uses standard library only)

## File Structure

```
xml_files/
├── analyze.py              # Main script
├── src/
│   ├── xml_schema_analyzer.py
│   ├── xml_document_analysis_framework.py
│   ├── xml_framework_demo_script.py
│   └── agent_integration.py
├── sample_data/
│   ├── node2.example.com-STIG-20250710162433.xml
│   └── node2.example.com-PCI-20250710162255.xml
└── requirements.txt
```
