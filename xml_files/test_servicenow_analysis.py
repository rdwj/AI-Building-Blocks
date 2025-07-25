#!/usr/bin/env python3
"""
Test ServiceNow XML Handler and save raw analysis output
"""

import sys
import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime

# Add src to path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from handlers.servicenow_handler import ServiceNowHandler

def test_servicenow_analysis():
    """Test ServiceNow handler and save complete analysis to file"""
    
    # Initialize the ServiceNow handler
    handler = ServiceNowHandler()
    
    # Path to ServiceNow ticket (you can change this to test different tickets)
    ticket_file = "/Users/wjackson/Developer/LLNL/data/rhoai-sanitized-main/servicenow/incident_1217.xml"
    
    print(f"🎫 Testing ServiceNow Handler")
    print(f"File: {os.path.basename(ticket_file)}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Parse the XML
        tree = ET.parse(ticket_file)
        root = tree.getroot()
        namespaces = {}
        
        # Collect all analysis results
        analysis_results = {
            "test_info": {
                "file_analyzed": ticket_file,
                "file_basename": os.path.basename(ticket_file),
                "analysis_timestamp": datetime.now().isoformat(),
                "handler_class": "ServiceNowHandler"
            }
        }
        
        print("Step 1: Testing can_handle()...")
        can_handle, confidence = handler.can_handle(root, namespaces)
        analysis_results["can_handle"] = {
            "result": can_handle,
            "confidence": confidence
        }
        print(f"   Can handle: {can_handle}, Confidence: {confidence:.2%}")
        
        print("Step 2: Testing detect_type()...")
        type_info = handler.detect_type(root, namespaces)
        analysis_results["detect_type"] = {
            "type_name": type_info.type_name,
            "confidence": type_info.confidence,
            "version": type_info.version,
            "schema_uri": type_info.schema_uri,
            "metadata": type_info.metadata
        }
        print(f"   Type: {type_info.type_name}, Confidence: {type_info.confidence:.2%}")
        
        print("Step 3: Testing extract_key_data()...")
        key_data = handler.extract_key_data(root)
        analysis_results["extract_key_data"] = key_data
        print(f"   Extracted {len(key_data)} data categories")
        
        print("Step 4: Running full analyze()...")
        full_analysis = handler.analyze(root, ticket_file)
        
        # Convert SpecializedAnalysis to dict for JSON serialization
        analysis_results["full_analysis"] = {
            "document_type": full_analysis.document_type,
            "key_findings": full_analysis.key_findings,
            "recommendations": full_analysis.recommendations,
            "data_inventory": full_analysis.data_inventory,
            "ai_use_cases": full_analysis.ai_use_cases,
            "structured_data": full_analysis.structured_data,
            "quality_metrics": full_analysis.quality_metrics
        }
        print(f"   Analysis complete with {len(full_analysis.key_findings)} key findings")
        
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"servicenow_analysis_{os.path.splitext(os.path.basename(ticket_file))[0]}_{timestamp}.json"
        
        # Save to file
        print(f"\nStep 5: Saving raw analysis to file...")
        with open(output_file, 'w') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        
        print(f"✅ Analysis saved to: {output_file}")
        print(f"📊 File size: {os.path.getsize(output_file):,} bytes")
        
        # Print summary to console
        print(f"\n📋 ANALYSIS SUMMARY")
        print("-" * 30)
        print(f"Document Type: {full_analysis.document_type}")
        print(f"Key Findings: {len(full_analysis.key_findings)} categories")
        print(f"Recommendations: {len(full_analysis.recommendations)} items")
        print(f"AI Use Cases: {len(full_analysis.ai_use_cases)} identified")
        print(f"Data Inventory: {len(full_analysis.data_inventory)} data types")
        print(f"Quality Metrics: {len(full_analysis.quality_metrics)} metrics")
        
        # Show some key stats
        if 'journal_analysis' in full_analysis.key_findings:
            journal = full_analysis.key_findings['journal_analysis']
            print(f"Conversation Entries: {journal.get('total_entries', 'N/A')}")
        
        if 'attachment_analysis' in full_analysis.key_findings:
            attachments = full_analysis.key_findings['attachment_analysis']
            print(f"Attachments: {attachments.get('total_attachments', 'N/A')}")
        
        print(f"\n🔍 To examine the complete raw analysis:")
        print(f"   cat {output_file}")
        print(f"   or")
        print(f"   python -m json.tool {output_file}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_multiple_tickets():
    """Analyze multiple ServiceNow tickets for comparison"""
    
    tickets = [
        "/Users/wjackson/Developer/LLNL/data/rhoai-sanitized-main/servicenow/incident_1028.xml",
        "/Users/wjackson/Developer/LLNL/data/rhoai-sanitized-main/servicenow/incident_1109.xml",
        "/Users/wjackson/Developer/LLNL/data/rhoai-sanitized-main/servicenow/incident_1217.xml"
    ]
    
    print(f"\n🎫 BATCH ANALYSIS")
    print("=" * 50)
    
    results = []
    
    for ticket in tickets:
        if os.path.exists(ticket):
            print(f"\nProcessing: {os.path.basename(ticket)}")
            
            # Temporarily modify the global ticket file
            global ticket_file
            original_ticket = ticket_file if 'ticket_file' in globals() else None
            ticket_file = ticket
            
            # Run analysis
            output_file = test_servicenow_analysis()
            if output_file:
                results.append(output_file)
            
            # Restore original
            if original_ticket:
                ticket_file = original_ticket
        else:
            print(f"⚠️  Ticket not found: {os.path.basename(ticket)}")
    
    if results:
        print(f"\n✅ Generated {len(results)} analysis files:")
        for result in results:
            print(f"   - {result}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--batch":
        analyze_multiple_tickets()
    else:
        test_servicenow_analysis()