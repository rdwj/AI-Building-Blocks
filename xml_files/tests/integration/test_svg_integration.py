#!/usr/bin/env python3
"""
Test SVG handler integration with main analyzer
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def test_svg_integration():
    """Test SVG handler integration with main analyzer"""
    
    try:
        from core.analyzer import XMLDocumentAnalyzer
        print("✅ XMLDocumentAnalyzer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import XMLDocumentAnalyzer: {e}")
        return False
    
    # Test registry import
    try:
        from handlers import ALL_HANDLERS, SVGHandler
        print(f"✅ Handler registry imported successfully ({len(ALL_HANDLERS)} handlers)")
        
        # Check if SVGHandler is in the registry
        svg_handler_in_registry = any(h.__name__ == 'SVGHandler' for h in ALL_HANDLERS)
        print(f"✅ SVGHandler in registry: {svg_handler_in_registry}")
        
    except ImportError as e:
        print(f"❌ Failed to import handler registry: {e}")
        return False
    
    # Test with sample SVG file
    analyzer = XMLDocumentAnalyzer()
    test_file = "../../sample_data/test_files_synthetic/small/svg/icon.svg"
    
    if not Path(test_file).exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    print(f"\n🔍 Testing integration with {test_file}")
    
    try:
        result = analyzer.analyze_document(test_file)
        
        print(f"✅ Analysis completed successfully")
        print(f"  - Handler used: {result['handler_used']}")
        print(f"  - Document type: {result['document_type'].type_name}")
        print(f"  - Confidence: {result['confidence']:.1f}")
        print(f"  - Analysis type: {result['analysis'].document_type}")
        
        # Verify it's using the SVG handler
        if result['handler_used'] != 'SVGHandler':
            print(f"❌ Wrong handler used! Expected SVGHandler, got {result['handler_used']}")
            return False
        
        print("✅ SVG handler integration successful!")
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 SVG Handler Integration Test")
    print("=" * 50)
    
    success = test_svg_integration()
    
    if success:
        print("\n🎉 SVG handler integration test passed!")
        sys.exit(0)
    else:
        print("\n❌ SVG handler integration test failed!")
        sys.exit(1)