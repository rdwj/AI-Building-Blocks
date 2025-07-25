# XML Analysis Framework

[![Tests](https://github.com/yourusername/xml-analysis-framework/workflows/Tests/badge.svg)](https://github.com/yourusername/xml-analysis-framework/actions)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive framework for analyzing XML documents with specialized handlers for different document types and AI/ML processing preparation. Features intelligent document detection, specialized analysis, and smart chunking strategies to make XML data AI-ready.

## 🚀 Quick Start

```bash
# Basic analysis
python examples/basic_analysis.py sample_data/test_files/small/ant/build.xml

# Enhanced analysis with all specialized handlers
python examples/enhanced_analysis.py sample_data/test_files/small/scap/security-report.xml

# Framework demonstration
python examples/framework_demo.py
```

## 🎯 Key Features

### 1. **28 Specialized XML Handlers**
Automatically detects and analyzes:
- **Security**: SCAP, SAML, SOAP Envelopes
- **Build Systems**: Maven POM, Ant Build, Ivy Dependencies
- **Configuration**: Log4j, Spring, Hibernate, Struts
- **Content**: RSS/Atom, DocBook, XHTML, SVG
- **Data**: GPX tracks, KML maps, GraphML networks, XLIFF translations
- **APIs**: WADL, WSDL service definitions
- **Enterprise**: Enterprise Java configurations

### 2. **Intelligent Document Detection**
- Confidence scoring for handler selection
- Namespace-aware XML parsing
- Extensible handler architecture
- Graceful fallback to generic analysis

### 3. **Smart Chunking Strategies**
- **Hierarchical**: Respects XML structure and semantic boundaries
- **Sliding Window**: Overlapping chunks for context preservation  
- **Content-Aware**: Groups similar content types together
- **Token-Aware**: LLM-optimized chunk sizing

### 4. **AI/ML Ready Output**
- Structured JSON with metadata
- Pre-identified AI use cases for each document type
- Quality metrics for data assessment
- LLM-optimized processing recommendations

## 📋 Supported Document Types (28 Handlers)

| Category | Handlers | Description |
|----------|----------|-------------|
| **Security** | SCAP, SAML, SOAP | Security reports, authentication, web services |
| **Build Systems** | Maven POM, Ant, Ivy | Project dependencies, build configurations |
| **Enterprise Config** | Spring, Hibernate, Struts, Log4j | Java enterprise framework configurations |
| **Content & Docs** | RSS, DocBook, XHTML, SVG | Web content, documentation, graphics |
| **Geospatial** | GPX, KML | GPS tracks, geographic data |
| **Data Exchange** | GraphML, XLIFF | Network data, translation workflows |
| **API Definitions** | WADL, WSDL | REST and SOAP service descriptions |
| **Generic** | XML Schema, Sitemap, Test Reports | Fallback and specialized formats |

## 🏗️ Professional Architecture

```
xml-analysis-framework/
├── README.md                    # Project overview
├── LICENSE                      # MIT license
├── requirements.txt            # Dependencies (Python stdlib only)
├── setup.py                    # Package installation
├── .gitignore                  # Git ignore patterns
├── .github/workflows/          # CI/CD pipelines
│
├── src/                        # Source code
│   ├── core/                   # Core framework
│   │   ├── analyzer.py         # Main analysis engine
│   │   ├── schema_analyzer.py  # XML schema analysis
│   │   └── chunking.py         # Chunking strategies
│   ├── handlers/              # 28 specialized handlers
│   └── utils/                 # Utility functions
│
├── tests/                      # Comprehensive test suite
│   ├── unit/                  # Handler unit tests (16 files)
│   ├── integration/           # Integration tests (11 files)
│   ├── comprehensive/         # Full system tests (4 files)
│   └── run_all_tests.py      # Master test runner
│
├── examples/                   # Usage examples
│   ├── basic_analysis.py      # Simple analysis
│   ├── enhanced_analysis.py   # Full featured analysis
│   └── framework_demo.py      # Complete demonstration
│
├── scripts/                    # Utility scripts
│   ├── collect_test_files.py  # Test data collection
│   └── debug/                 # Debug utilities
│
├── docs/                       # Documentation
│   ├── architecture/          # Design documents
│   ├── guides/                # User guides
│   └── api/                   # API documentation
│
├── sample_data/               # Test XML files (99+ examples)
│   ├── test_files/           # Real-world examples
│   └── test_files_synthetic/ # Generated test cases
│
└── artifacts/                 # Build artifacts, results
    ├── analysis_results/     # JSON analysis outputs
    └── reports/             # Generated reports
```

## 🔧 Installation

```bash
# Install from source
git clone <repository-url>
cd xml-analysis-framework
pip install -e .

# Or install development dependencies
pip install -e .[dev]
```

**No external dependencies required!** Uses only Python standard library (3.7+).

## 📖 Usage Examples

### Basic Analysis
```python
from src.core.schema_analyzer import XMLSchemaAnalyzer

analyzer = XMLSchemaAnalyzer()
schema = analyzer.analyze_file('document.xml')
print(analyzer.generate_llm_description(schema))
```

### Enhanced Analysis with Specialized Handlers
```python
from src.core.analyzer import XMLDocumentAnalyzer

analyzer = XMLDocumentAnalyzer()
result = analyzer.analyze_document('maven-project.xml')

print(f"Document Type: {result.document_type.type_name}")
print(f"Confidence: {result.document_type.confidence:.2f}")
print(f"AI Use Cases: {result.analysis.ai_use_cases}")
```

### Intelligent Chunking
```python
from src.core.chunking import ChunkingOrchestrator

orchestrator = ChunkingOrchestrator()
chunks = orchestrator.chunk_document(
    'large_document.xml',
    strategy='auto'  # Automatically selects best strategy
)

for chunk in chunks:
    print(f"Chunk {chunk.chunk_id}: ~{chunk.token_estimate} tokens")
```

## 🧪 Testing

Comprehensive test suite with **98% success rate** across 99+ XML sample files:

```bash
# Run all tests
cd tests && python run_all_tests.py

# Run specific test categories
python -m pytest unit/          # Unit tests
python -m pytest integration/   # Integration tests
python -m pytest comprehensive/ # Full system tests
```

## 🤖 AI Use Cases by Document Type

### Security Documents (SCAP, SAML, SOAP)
- Automated compliance monitoring and risk assessment
- Security posture classification and trend analysis
- Vulnerability prediction and remediation recommendations

### Build & Configuration (Maven, Ant, Spring, Log4j)
- Dependency vulnerability scanning and analysis
- Configuration optimization and security assessment
- Technical debt analysis and modernization planning

### Content & Documentation (RSS, DocBook, XHTML)
- Content categorization and sentiment analysis
- Automatic summarization and topic modeling
- Translation preparation and quality assessment

### Geospatial & Data (GPX, KML, GraphML, XLIFF)
- Route optimization and fitness analytics
- Geographic pattern analysis and visualization
- Network analysis and translation workflow optimization

## 🔬 Quality Metrics

- **28 specialized handlers** for comprehensive XML coverage
- **98% success rate** across diverse XML samples
- **0.015s average processing time** per document
- **Professional test suite** with 35+ test files organized by category
- **CI/CD integration** with GitHub Actions
- **Zero external dependencies** - pure Python stdlib

## 🚀 Extending the Framework

### Adding New Handlers
```python
from src.core.analyzer import XMLHandler, SpecializedAnalysis

class CustomHandler(XMLHandler):
    def can_handle(self, root, namespaces):
        return root.tag == 'custom-format', 1.0
    
    def analyze(self, root, file_path):
        return SpecializedAnalysis(
            document_type="Custom Format",
            key_findings={...},
            ai_use_cases=["Custom AI application"]
        )
```

### Custom Chunking Strategies
```python
from src.core.chunking import XMLChunkingStrategy

class CustomChunking(XMLChunkingStrategy):
    def chunk_document(self, file_path, analysis_result):
        # Custom chunking logic
        return chunks
```

## 📊 Sample Output

```json
{
  "success": true,
  "file_info": {
    "name": "spring-config.xml",
    "size_formatted": "2.1 KB"
  },
  "specialized_analysis": {
    "document_type": {
      "type_name": "Spring Configuration",
      "confidence": 0.95,
      "handler": "SpringConfigHandler"
    },
    "analysis": {
      "key_findings": {
        "bean_count": 12,
        "dependencies": 8,
        "security_features": ["authentication", "authorization"]
      },
      "ai_use_cases": [
        "Configuration optimization",
        "Dependency analysis",
        "Security assessment"
      ],
      "quality_metrics": {
        "overall": 0.87,
        "security": 0.92,
        "completeness": 0.85
      }
    }
  }
}
```

## 🤝 Contributing

Contributions welcome! Focus areas:
- New XML format handlers
- Enhanced chunking algorithms  
- Performance optimizations
- LLM integration examples

See [Contributing Guidelines](docs/guides/contributing.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Designed as part of the **AI Building Blocks** initiative
- Built for the modern AI/ML ecosystem
- Community-driven XML format support