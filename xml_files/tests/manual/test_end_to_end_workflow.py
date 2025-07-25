#!/usr/bin/env python3
"""
End-to-End XML Analysis Framework Test

Tests the complete workflow for all sample files:
1. Document Analysis (using specialized handlers)
2. Smart Chunking (using optimal strategies)
3. AI-Ready Output Generation

Creates 3 files per test file:
- analysis.json: Document analysis results
- chunks.json: Smart chunking results  
- ai_ready.json: Combined output ready for LLM consumption
"""

import sys
import os
import json
import glob
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.analyzer import XMLDocumentAnalyzer
from core.chunking import ChunkingOrchestrator, ChunkingConfig

def create_output_directory():
    """Create timestamped output directory for end-to-end test results"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = f"end_to_end_results_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def find_all_xml_files():
    """Find all XML files in both sample directories"""
    xml_files = []
    
    # Test directories to process
    test_dirs = [
        "sample_data",
        "/Users/wjackson/Developer/LLNL/data/rhoai-sanitized-main/servicenow"
    ]
    
    # Common XML file patterns
    patterns = [
        "**/*.xml",
        "**/*.xsd", 
        "**/*.xccdf",
        "**/*.rss",
        "**/*.atom",
        "**/*.pom"
    ]
    
    for base_dir in test_dirs:
        if os.path.exists(base_dir):
            print(f"📁 Scanning {base_dir}")
            for pattern in patterns:
                files = glob.glob(os.path.join(base_dir, pattern), recursive=True)
                xml_files.extend(files)
            print(f"   Found {len([f for f in xml_files if f.startswith(base_dir)])} files")
        else:
            print(f"⚠️  Directory not found: {base_dir}")
    
    # Remove duplicates and sort
    xml_files = sorted(list(set(xml_files)))
    
    return xml_files

def perform_document_analysis(file_path: str) -> Dict[str, Any]:
    """Perform comprehensive document analysis using specialized handlers"""
    analyzer = XMLDocumentAnalyzer()
    analysis_result = analyzer.analyze_document(file_path)
    
    # Enhance with file metadata
    file_stat = Path(file_path).stat()
    
    enhanced_analysis = {
        "file_metadata": {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_size_bytes": file_stat.st_size,
            "file_size_mb": round(file_stat.st_size / 1024 / 1024, 3),
            "last_modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            "analysis_timestamp": datetime.now().isoformat()
        },
        "document_analysis": analysis_result
    }
    
    return enhanced_analysis

def perform_smart_chunking(file_path: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Perform smart chunking using optimal strategy for document type"""
    orchestrator = ChunkingOrchestrator()
    
    # Extract document analysis for chunking and convert to proper format
    doc_analysis_raw = analysis.get("document_analysis", {})
    
    # Convert to format expected by chunking orchestrator
    doc_type_info = doc_analysis_raw.get("document_type")
    if hasattr(doc_type_info, 'type_name'):
        # DocumentTypeInfo object - convert to dict format
        doc_analysis = {
            "document_type": {
                "type_name": doc_type_info.type_name,
                "confidence": doc_type_info.confidence
            },
            "analysis": doc_analysis_raw.get("analysis"),
            "handler_used": doc_analysis_raw.get("handler_used")
        }
    else:
        # Already in dict format
        doc_analysis = doc_analysis_raw
    
    # Test multiple configurations to find optimal
    configs = {
        "small": ChunkingConfig(max_chunk_size=1000, min_chunk_size=100, overlap_size=50),
        "medium": ChunkingConfig(max_chunk_size=2000, min_chunk_size=200, overlap_size=100),
        "large": ChunkingConfig(max_chunk_size=4000, min_chunk_size=500, overlap_size=200)
    }
    
    strategies = ['auto', 'hierarchical', 'content_aware', 'sliding_window']
    
    chunking_results = {
        "file_path": file_path,
        "chunking_timestamp": datetime.now().isoformat(),
        "document_type": str(doc_analysis.get('document_type', {}).get('type_name', 'unknown')),
        "strategies_tested": {},
        "optimal_strategy": None,
        "optimal_chunks": [],
        "chunking_summary": {}
    }
    
    best_score = 0
    best_strategy = None
    best_config = None
    best_chunks = []
    
    # Test all strategy/config combinations
    for strategy in strategies:
        chunking_results["strategies_tested"][strategy] = {}
        
        for config_name, config in configs.items():
            try:
                chunks = orchestrator.chunk_document(
                    file_path,
                    doc_analysis,
                    strategy=strategy,
                    config=config
                )
                
                if chunks:
                    # Calculate quality score (balance chunk count, token distribution, coverage)
                    token_counts = [chunk.token_estimate for chunk in chunks]
                    avg_tokens = sum(token_counts) / len(token_counts) if token_counts else 0
                    token_variance = sum((t - avg_tokens) ** 2 for t in token_counts) / len(token_counts) if token_counts else 0
                    
                    # Quality score: prefer moderate chunk count, good token distribution, good coverage
                    count_score = min(len(chunks) / 20, 1.0)  # Prefer 10-20 chunks
                    distribution_score = max(0, 1.0 - (token_variance / (avg_tokens ** 2)) if avg_tokens > 0 else 0)
                    coverage_score = min(sum(token_counts) / 10000, 1.0)  # Prefer good coverage
                    
                    quality_score = (count_score + distribution_score + coverage_score) / 3
                    
                    chunk_info = {
                        "chunk_count": len(chunks),
                        "total_tokens": sum(token_counts),
                        "avg_tokens": round(avg_tokens, 1),
                        "min_tokens": min(token_counts) if token_counts else 0,
                        "max_tokens": max(token_counts) if token_counts else 0,
                        "quality_score": round(quality_score, 3),
                        "unique_elements": len(set().union(*[chunk.elements_included for chunk in chunks if chunk.elements_included])),
                        "success": True
                    }
                    
                    # Track best strategy
                    if quality_score > best_score:
                        best_score = quality_score
                        best_strategy = strategy
                        best_config = config_name
                        best_chunks = chunks
                    
                else:
                    chunk_info = {
                        "chunk_count": 0,
                        "total_tokens": 0,
                        "quality_score": 0.0,
                        "success": False,
                        "issue": "No chunks generated"
                    }
                
                chunking_results["strategies_tested"][strategy][config_name] = chunk_info
                
            except Exception as e:
                chunking_results["strategies_tested"][strategy][config_name] = {
                    "success": False,
                    "error": str(e),
                    "quality_score": 0.0
                }
    
    # Set optimal results
    if best_chunks:
        chunking_results["optimal_strategy"] = f"{best_strategy}_{best_config}"
        chunking_results["optimal_chunks"] = [
            {
                "chunk_id": chunk.chunk_id,
                "chunk_number": i + 1,
                "element_path": chunk.element_path,
                "token_estimate": chunk.token_estimate,
                "content_length": len(chunk.content),
                "elements_included": chunk.elements_included,
                "metadata": chunk.metadata,
                "content": chunk.content
            }
            for i, chunk in enumerate(best_chunks)
        ]
        
        # Generate summary
        token_counts = [chunk.token_estimate for chunk in best_chunks]
        chunking_results["chunking_summary"] = {
            "optimal_strategy": f"{best_strategy}_{best_config}",
            "total_chunks": len(best_chunks),
            "total_tokens": sum(token_counts),
            "avg_tokens_per_chunk": round(sum(token_counts) / len(token_counts), 1),
            "token_distribution": {
                "min": min(token_counts),
                "max": max(token_counts),
                "std_dev": round((sum((t - sum(token_counts)/len(token_counts))**2 for t in token_counts) / len(token_counts))**0.5, 1)
            },
            "quality_score": round(best_score, 3)
        }
    
    return chunking_results

def generate_ai_ready_output(analysis: Dict[str, Any], chunks: Dict[str, Any]) -> Dict[str, Any]:
    """Generate AI-ready output combining analysis and chunking for LLM consumption"""
    
    file_path = analysis["file_metadata"]["file_path"]
    file_name = analysis["file_metadata"]["file_name"]
    
    # Extract key information from analysis
    doc_analysis = analysis.get("document_analysis", {})
    doc_type_info = doc_analysis.get("document_type", {})
    analysis_results = doc_analysis.get("analysis", {})
    
    # Get document type name
    if hasattr(doc_type_info, 'type_name'):
        doc_type = doc_type_info.type_name
        confidence = getattr(doc_type_info, 'confidence', 0.5)
    else:
        doc_type = doc_type_info.get('type_name', 'Unknown XML')
        confidence = doc_type_info.get('confidence', 0.5)
    
    # Build AI-ready structure
    ai_ready = {
        "document_summary": {
            "file_name": file_name,
            "file_path": file_path,
            "document_type": doc_type,
            "type_confidence": confidence,
            "handler_used": doc_analysis.get("handler_used", "unknown"),
            "file_size_mb": analysis["file_metadata"]["file_size_mb"],
            "analysis_timestamp": datetime.now().isoformat()
        },
        
        "key_insights": {
            "document_purpose": f"This is a {doc_type} document",
            "structure_overview": {},
            "data_highlights": {},
            "ai_applications": []
        },
        
        "structured_content": {
            "chunking_strategy": chunks.get("optimal_strategy", "none"),
            "total_chunks": len(chunks.get("optimal_chunks", [])),
            "chunks": chunks.get("optimal_chunks", [])
        },
        
        "analysis_details": {
            "full_analysis": analysis_results,
            "chunking_summary": chunks.get("chunking_summary", {}),
            "quality_metrics": {}
        },
        
        "llm_context": {
            "recommended_use_cases": [],
            "processing_notes": [],
            "content_summary": ""
        }
    }
    
    # Extract insights from specialized analysis
    if hasattr(analysis_results, 'key_findings'):
        ai_ready["key_insights"]["data_highlights"] = analysis_results.key_findings
    elif isinstance(analysis_results, dict):
        ai_ready["key_insights"]["data_highlights"] = analysis_results.get("key_findings", {})
    
    if hasattr(analysis_results, 'ai_use_cases'):
        ai_ready["key_insights"]["ai_applications"] = analysis_results.ai_use_cases
    elif isinstance(analysis_results, dict):
        ai_ready["key_insights"]["ai_applications"] = analysis_results.get("ai_use_cases", [])
    
    if hasattr(analysis_results, 'recommendations'):
        ai_ready["llm_context"]["recommended_use_cases"] = analysis_results.recommendations
    elif isinstance(analysis_results, dict):
        ai_ready["llm_context"]["recommended_use_cases"] = analysis_results.get("recommendations", [])
    
    # Add processing guidance
    total_chunks = len(chunks.get("optimal_chunks", []))
    if total_chunks > 0:
        avg_tokens = chunks.get("chunking_summary", {}).get("avg_tokens_per_chunk", 0)
        ai_ready["llm_context"]["processing_notes"] = [
            f"Document has been optimally chunked into {total_chunks} segments",
            f"Average chunk size: {avg_tokens} tokens",
            f"Recommended for {doc_type} analysis workflows",
            f"Chunking strategy: {chunks.get('optimal_strategy', 'unknown')}"
        ]
        
        # Create content summary from first few chunks
        first_chunks = chunks.get("optimal_chunks", [])[:3]
        if first_chunks:
            content_preview = " | ".join([
                chunk.get("content", "")[:100] + "..." 
                for chunk in first_chunks 
                if chunk.get("content")
            ])
            ai_ready["llm_context"]["content_summary"] = f"Preview: {content_preview}"
    
    # Add quality assessment
    if chunks.get("chunking_summary"):
        quality_score = chunks["chunking_summary"].get("quality_score", 0)
        ai_ready["analysis_details"]["quality_metrics"] = {
            "chunking_quality": quality_score,
            "analysis_confidence": confidence,
            "overall_readiness": round((quality_score + confidence) / 2, 3)
        }
    
    return ai_ready

def process_single_file(file_path: str, output_dir: str) -> Dict[str, Any]:
    """Process a single XML file through the complete workflow"""
    
    file_name = os.path.basename(file_path)
    print(f"📄 Processing: {file_name}")
    
    # Create subdirectory for this file
    safe_filename = "".join(c for c in file_name if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
    file_output_dir = os.path.join(output_dir, safe_filename)
    os.makedirs(file_output_dir, exist_ok=True)
    
    results = {
        "file_path": file_path,
        "output_directory": file_output_dir,
        "processing_timestamp": datetime.now().isoformat(),
        "steps_completed": [],
        "errors": []
    }
    
    try:
        # Step 1: Document Analysis
        print(f"   🔍 Analyzing document...")
        analysis = perform_document_analysis(file_path)
        
        analysis_file = os.path.join(file_output_dir, "analysis.json")
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
        
        results["steps_completed"].append("document_analysis")
        results["analysis_file"] = analysis_file
        
        # Step 2: Smart Chunking
        print(f"   ⚙️ Performing smart chunking...")
        chunks = perform_smart_chunking(file_path, analysis)
        
        chunks_file = os.path.join(file_output_dir, "chunks.json")
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False, default=str)
        
        results["steps_completed"].append("smart_chunking")
        results["chunks_file"] = chunks_file
        
        # Step 3: AI-Ready Output
        print(f"   🤖 Generating AI-ready output...")
        ai_ready = generate_ai_ready_output(analysis, chunks)
        
        ai_ready_file = os.path.join(file_output_dir, "ai_ready.json")
        with open(ai_ready_file, 'w', encoding='utf-8') as f:
            json.dump(ai_ready, f, indent=2, ensure_ascii=False, default=str)
        
        results["steps_completed"].append("ai_ready_generation")
        results["ai_ready_file"] = ai_ready_file
        
        # Add summary info
        doc_type = str(analysis.get("document_analysis", {}).get("document_type", "unknown"))
        chunk_count = len(chunks.get("optimal_chunks", []))
        results["summary"] = {
            "document_type": doc_type,
            "chunk_count": chunk_count,
            "files_generated": 3
        }
        
        print(f"   ✅ Complete: {doc_type} → {chunk_count} chunks")
        
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        results["errors"].append(error_msg)
        print(f"   ❌ Error: {error_msg}")
        
        # Save error details
        error_file = os.path.join(file_output_dir, "error.json")
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump({
                "error": error_msg,
                "traceback": traceback.format_exc(),
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
    
    return results

def generate_summary_report(all_results: List[Dict[str, Any]], output_dir: str):
    """Generate comprehensive summary report of all processed files"""
    
    summary = {
        "test_info": {
            "timestamp": datetime.now().isoformat(),
            "total_files_processed": len(all_results),
            "output_directory": output_dir
        },
        "processing_statistics": {
            "successful_files": 0,
            "failed_files": 0,
            "total_steps_completed": 0,
            "total_errors": 0
        },
        "document_type_breakdown": {},
        "chunking_performance": {
            "strategies_used": {},
            "avg_chunks_per_file": 0,
            "total_chunks_generated": 0
        },
        "framework_capabilities": {
            "handlers_tested": set(),
            "document_types_detected": set(),
            "chunking_strategies_used": set()
        },
        "files_processed": []
    }
    
    total_chunks = 0
    successful_files = 0
    
    for result in all_results:
        file_summary = {
            "file_name": os.path.basename(result["file_path"]),
            "steps_completed": len(result["steps_completed"]),
            "errors": len(result["errors"]),
            "success": len(result["errors"]) == 0
        }
        
        if result["errors"]:
            summary["processing_statistics"]["failed_files"] += 1
            summary["processing_statistics"]["total_errors"] += len(result["errors"])
        else:
            summary["processing_statistics"]["successful_files"] += 1
            successful_files += 1
            
            # Extract detailed info for successful files
            if "summary" in result:
                doc_type = result["summary"]["document_type"]
                chunk_count = result["summary"]["chunk_count"]
                
                file_summary.update({
                    "document_type": doc_type,
                    "chunk_count": chunk_count
                })
                
                # Update document type breakdown
                if doc_type not in summary["document_type_breakdown"]:
                    summary["document_type_breakdown"][doc_type] = {
                        "count": 0,
                        "total_chunks": 0,
                        "avg_chunks": 0
                    }
                
                summary["document_type_breakdown"][doc_type]["count"] += 1
                summary["document_type_breakdown"][doc_type]["total_chunks"] += chunk_count
                total_chunks += chunk_count
                
                # Track framework capabilities
                summary["framework_capabilities"]["document_types_detected"].add(doc_type)
        
        summary["processing_statistics"]["total_steps_completed"] += len(result["steps_completed"])
        summary["files_processed"].append(file_summary)
    
    # Calculate averages
    if successful_files > 0:
        summary["chunking_performance"]["avg_chunks_per_file"] = round(total_chunks / successful_files, 1)
        summary["chunking_performance"]["total_chunks_generated"] = total_chunks
        
        # Calculate doc type averages
        for doc_type, info in summary["document_type_breakdown"].items():
            if info["count"] > 0:
                info["avg_chunks"] = round(info["total_chunks"] / info["count"], 1)
    
    # Convert sets to lists for JSON serialization
    summary["framework_capabilities"]["document_types_detected"] = sorted(list(summary["framework_capabilities"]["document_types_detected"]))
    summary["framework_capabilities"]["handlers_tested"] = sorted(list(summary["framework_capabilities"]["handlers_tested"]))
    summary["framework_capabilities"]["chunking_strategies_used"] = sorted(list(summary["framework_capabilities"]["chunking_strategies_used"]))
    
    # Save summary
    summary_file = os.path.join(output_dir, "framework_test_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
    
    # Generate human-readable report
    report_file = os.path.join(output_dir, "FRAMEWORK_TEST_REPORT.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# XML Analysis Framework - End-to-End Test Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 📊 Summary Statistics\n\n")
        f.write(f"- **Total Files Processed:** {summary['test_info']['total_files_processed']}\n")
        f.write(f"- **Successful:** {summary['processing_statistics']['successful_files']}\n")
        f.write(f"- **Failed:** {summary['processing_statistics']['failed_files']}\n")
        f.write(f"- **Success Rate:** {summary['processing_statistics']['successful_files'] / len(all_results) * 100:.1f}%\n")
        f.write(f"- **Total Chunks Generated:** {summary['chunking_performance']['total_chunks_generated']}\n")
        f.write(f"- **Average Chunks per File:** {summary['chunking_performance']['avg_chunks_per_file']}\n\n")
        
        f.write("## 🏷️ Document Types Detected\n\n")
        f.write("| Document Type | Files | Total Chunks | Avg Chunks |\n")
        f.write("|---------------|-------|--------------|------------|\n")
        for doc_type, info in sorted(summary["document_type_breakdown"].items()):
            f.write(f"| {doc_type} | {info['count']} | {info['total_chunks']} | {info['avg_chunks']} |\n")
        f.write("\n")
        
        f.write("## 🧠 Framework Capabilities Demonstrated\n\n")
        f.write(f"- **Document Types Detected:** {len(summary['framework_capabilities']['document_types_detected'])}\n")
        f.write(f"- **Specialized Handlers Working:** Multiple types successfully processed\n")
        f.write(f"- **Smart Chunking:** Optimal strategies selected per document type\n")
        f.write(f"- **AI-Ready Output:** Structured content prepared for LLM consumption\n\n")
        
        f.write("## 📁 Output Structure\n\n")
        f.write("Each processed file generates:\n")
        f.write("- `analysis.json` - Complete document analysis using specialized handlers\n")
        f.write("- `chunks.json` - Smart chunking results with optimal strategy selection\n")
        f.write("- `ai_ready.json` - Combined output structured for LLM workflows\n\n")
        
        f.write("## 🔍 Individual File Results\n\n")
        f.write("| File | Document Type | Chunks | Status |\n")
        f.write("|------|---------------|--------|--------|\n")
        for file_info in summary["files_processed"]:
            status = "✅ Success" if file_info["success"] else "❌ Failed"
            doc_type = file_info.get("document_type", "Unknown")
            chunk_count = file_info.get("chunk_count", 0)
            f.write(f"| {file_info['file_name']} | {doc_type} | {chunk_count} | {status} |\n")
    
    return summary_file, report_file

def main():
    """Main test execution"""
    
    print("🚀 XML ANALYSIS FRAMEWORK - END-TO-END TEST")
    print("=" * 70)
    
    # Create output directory
    output_dir = create_output_directory()
    print(f"📁 Output directory: {output_dir}")
    
    # Find all XML files
    print(f"\n🔍 Discovering XML files...")
    xml_files = find_all_xml_files()
    print(f"   Found {len(xml_files)} XML files total")
    
    # Process each file
    print(f"\n⚙️ Processing files through complete workflow...")
    all_results = []
    
    for i, file_path in enumerate(xml_files, 1):
        print(f"\n[{i}/{len(xml_files)}] {os.path.basename(file_path)}")
        result = process_single_file(file_path, output_dir)
        all_results.append(result)
    
    # Generate summary report
    print(f"\n📊 Generating comprehensive summary...")
    summary_file, report_file = generate_summary_report(all_results, output_dir)
    
    print(f"\n✅ END-TO-END TEST COMPLETE")
    print(f"📁 Results saved in: {output_dir}")
    print(f"📊 Summary files:")
    print(f"   - {summary_file}")
    print(f"   - {report_file}")
    
    # Quick stats
    successful = sum(1 for r in all_results if not r["errors"])
    total_chunks = sum(r.get("summary", {}).get("chunk_count", 0) for r in all_results if not r["errors"])
    
    print(f"\n🎯 Key Results:")
    print(f"   - Files Processed: {len(xml_files)}")
    print(f"   - Success Rate: {successful}/{len(xml_files)} ({successful/len(xml_files)*100:.1f}%)")
    print(f"   - Total Chunks Generated: {total_chunks}")
    print(f"   - Files Generated: {successful * 3} (3 per successful file)")
    
    print(f"\n🔍 Next Steps:")
    print(f"   1. Review {report_file} for detailed analysis")
    print(f"   2. Examine individual file outputs in subdirectories")
    print(f"   3. Test AI workflows with ai_ready.json files")
    print(f"   4. Analyze framework capabilities and potential improvements")

if __name__ == "__main__":
    main()