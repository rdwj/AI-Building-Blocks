#!/usr/bin/env python3
"""
Test the correct XMLDocumentAnalyzer from core.analyzer
"""

import sys
import os

# Add src to path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_correct_analyzer():
    """Test the correct analyzer"""
    
    print("🧪 TESTING CORRECT XMLDocumentAnalyzer")
    print("=" * 50)
    
    # Test importing from core.analyzer
    try:
        from core.analyzer import XMLDocumentAnalyzer
        print("✅ Successfully imported XMLDocumentAnalyzer from core.analyzer")
        
        analyzer = XMLDocumentAnalyzer()
        print(f"📋 Handlers registered: {len(analyzer.handlers)}")
        
        # Show first few handlers
        print(f"\nFirst 10 handlers:")
        for i, handler in enumerate(analyzer.handlers[:10], 1):
            print(f"   {i:2d}. {handler.__class__.__name__}")
            
        if len(analyzer.handlers) > 10:
            print(f"   ... and {len(analyzer.handlers) - 10} more")
        
    except Exception as e:
        print(f"❌ Failed to import from core.analyzer: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test analyzing a file
    test_file = "sample_data/test_files/small/scap/ios-sample-1.1.xccdf.xml"
    if os.path.exists(test_file):
        print(f"\n🔍 Testing analysis with: {os.path.basename(test_file)}")
        
        try:
            result = analyzer.analyze_document(test_file)
            
            # Extract the document type info
            if hasattr(result, 'document_type'):
                doc_type = result.document_type
                handler_used = getattr(result, 'handler_used', 'unknown')
            else:
                doc_type = result.get('document_type', 'unknown')
                handler_used = result.get('handler_used', 'unknown')
            
            print(f"   📋 Document Type: {doc_type}")
            print(f"   🔧 Handler Used: {handler_used}")
            print(f"   ✅ Analysis successful")
            
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print(f"⚠️  Test file not found: {test_file}")
    
    return True

if __name__ == "__main__":
    success = test_correct_analyzer()
    if success:
        print(f"\n✅ CORRECT ANALYZER IS WORKING")
        print(f"💡 Need to update imports in test files to use: from core.analyzer import XMLDocumentAnalyzer")
    else:
        print(f"\n❌ ISSUES WITH CORRECT ANALYZER")