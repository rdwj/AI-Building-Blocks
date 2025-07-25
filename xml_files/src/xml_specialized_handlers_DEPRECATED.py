#!/usr/bin/env python3
"""
DEPRECATED: xml_specialized_handlers.py

This file has been deprecated and moved to core/analyzer.py

The XMLDocumentAnalyzer class and all related functionality
has been moved to src/core/analyzer.py which uses the centralized
handler registry from src/handlers/__init__.py

Please update your imports:
OLD: from core.analyzer import XMLDocumentAnalyzer
NEW: from core.analyzer import XMLDocumentAnalyzer

This file is kept for reference only and will be removed in a future version.
"""

# Re-export from the correct location for backward compatibility
import warnings

def deprecated_import_warning():
    warnings.warn(
        "xml_specialized_handlers is deprecated. Use 'from core.analyzer import XMLDocumentAnalyzer' instead.",
        DeprecationWarning,
        stacklevel=3
    )

# Backward compatibility exports
try:
    deprecated_import_warning()
    from core.analyzer import (
        DocumentTypeInfo,
        SpecializedAnalysis, 
        XMLHandler,
        XMLDocumentAnalyzer
    )
except ImportError:
    # Fallback if core.analyzer is not available
    pass