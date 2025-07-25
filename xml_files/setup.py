#!/usr/bin/env python3
"""
Setup script for XML Analysis Framework
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="xml-analysis-framework",
    version="1.0.0",
    author="AI Building Blocks",
    author_email="contact@example.com",
    description="Comprehensive framework for analyzing XML documents with AI/ML processing support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/xml-analysis-framework",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: XML",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        # Only using Python standard library - no external dependencies
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=3.0",
            "sphinx_rtd_theme>=0.5",
        ],
    },
    entry_points={
        "console_scripts": [
            "xml-analyze=src.examples.basic_analysis:main",
            "xml-analyze-enhanced=src.examples.enhanced_analysis:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)