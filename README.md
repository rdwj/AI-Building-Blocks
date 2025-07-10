# AI Building Blocks

A collection of reusable components for AI/ML infrastructure on OpenShift.

## 🎯 Purpose

This monorepo provides production-ready building blocks for deploying AI/ML workloads on OpenShift. Each component is designed to be:
- **Self-contained**: Deploy and use independently
- **Composable**: Combine blocks for complete solutions
- **Cloud-native**: Built for Kubernetes/OpenShift
- **Production-ready**: Includes monitoring, scaling, and security considerations

## 📦 Available Building Blocks

### 1. PGVector - Vector Database for AI
A PostgreSQL-based vector database for similarity search and RAG applications.

- **[pgvector-openshift](pgvector/pgvector-openshift/)** - Deploy PostgreSQL with PGVector extension on OpenShift
- **[pgvector-rag-utils](pgvector/pgvector-rag-utils/)** - Python utilities and pipelines for RAG applications

**Use Cases**: Semantic search, RAG systems, embedding storage, similarity matching

### 2. [Coming Soon] LLM Serving
Deploy and serve Large Language Models on OpenShift.

### 3. [Coming Soon] Embedding Services
High-performance embedding generation services.

### 4. [Coming Soon] Document Processing
Intelligent document parsing and chunking for AI applications.

## 🚀 Quick Start

Each building block contains its own documentation, but here's the typical workflow:

1. **Choose your building blocks** based on your use case
2. **Deploy infrastructure components** (e.g., pgvector-openshift)
3. **Use application utilities** (e.g., pgvector-rag-utils)
4. **Combine blocks** to create complete AI solutions

### Example: RAG System
```bash
# 1. Deploy vector database
cd pgvector/pgvector-openshift
./scripts/deploy-and-test.sh

# 2. Set up RAG utilities
cd ../pgvector-rag-utils
pip install -r requirements.txt
./setup.sh

# 3. Start building!
python example_usage.py
```

## 📋 Prerequisites

- OpenShift 4.x cluster
- `oc` CLI tool installed and configured
- Python 3.8+ (for application components)
- Appropriate cluster permissions

## 📚 Repository Structure

```
AI-Building-Blocks/
├── pgvector/                    # Vector database building block
│   ├── pgvector-openshift/      # Deployment component
│   └── pgvector-rag-utils/      # Application utilities
├── llm-serving/                 # (Coming soon)
├── embedding-services/          # (Coming soon)
└── doc-processing/              # (Coming soon)
```

## 🤝 Contributing

Contributions are welcome! Each building block should:
- Include comprehensive documentation
- Provide deployment automation
- Include example usage
- Follow cloud-native best practices

## 📧 Contact

- **Repository**: https://github.com/rdwj/AI-Building-Blocks
- **Maintainer**: Wes Jackson (wjackson@redhat.com)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the OpenShift AI community
- Inspired by cloud-native best practices
- Designed for real-world AI/ML workloads

---

*Building the future of AI infrastructure, one block at a time.* 🏗️
