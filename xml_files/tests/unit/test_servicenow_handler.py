#!/usr/bin/env python3
"""
Unit tests for ServiceNow XML Handler

Tests the ServiceNowHandler's ability to process ServiceNow export files
containing incidents, problems, changes, and related data.
"""

import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.handlers.servicenow_handler import ServiceNowHandler


class TestServiceNowHandler(unittest.TestCase):
    """Test cases for ServiceNowHandler"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.handler = ServiceNowHandler()
        
        # Create a sample ServiceNow XML structure
        self.sample_xml = """<?xml version="1.0" ?>
<unload>
  <incident action="INSERT_OR_UPDATE">
    <number>INC0001234</number>
    <sys_id>abc123def456</sys_id>
    <opened_at>2023-04-18 19:06:09</opened_at>
    <closed_at>2023-12-21 20:00:02</closed_at>
    <resolved_at>2023-12-14 19:52:00</resolved_at>
    <state>7</state>
    <u_state_text>Closed</u_state_text>
    <priority>4</priority>
    <impact>3</impact>
    <urgency>3</urgency>
    <category>software</category>
    <subcategory/>
    <short_description>X-window session errors</short_description>
    <description>Daily x-window session errors out, works for a day or so, but consistently fails.</description>
    <assignment_group display_value="IT Support Group">UUID2</assignment_group>
    <assigned_to display_value="John Smith">UUID5</assigned_to>
    <caller_id display_value="Jane Doe">UUID6</caller_id>
    <requested_for display_value="Jane Doe">UUID6</requested_for>
    <opened_by display_value="John Smith">UUID5</opened_by>
    <resolved_by display_value="John Smith">UUID5</resolved_by>
    <closed_by display_value="John Smith">UUID5</closed_by>
    <close_code>Solved</close_code>
    <close_notes>Issue resolved</close_notes>
    <made_sla>true</made_sla>
    <u_sla_percentage>857.26</u_sla_percentage>
    <u_breach_time>2023-05-16 19:06:09</u_breach_time>
    <reassignment_count>2</reassignment_count>
    <reopen_count>0</reopen_count>
    <u_escalation_level>4_sla_breached</u_escalation_level>
    <u_custom_field>Custom value</u_custom_field>
  </incident>
  <sys_journal_field action="INSERT_OR_UPDATE">
    <element>comments</element>
    <element_id>abc123def456</element_id>
    <name>incident</name>
    <sys_created_by>john.smith</sys_created_by>
    <sys_created_on>2023-12-14 19:52:00</sys_created_on>
    <sys_id>journal123</sys_id>
    <value>Thank you for contacting the LC hotline.</value>
  </sys_journal_field>
  <sys_journal_field action="INSERT_OR_UPDATE">
    <element>work_notes</element>
    <element_id>abc123def456</element_id>
    <name>incident</name>
    <sys_created_by>john.smith</sys_created_by>
    <sys_created_on>2023-04-18 19:06:09</sys_created_on>
    <sys_id>journal456</sys_id>
    <value>This Incident was raised on behalf of Jane Doe</value>
  </sys_journal_field>
  <sys_attachment action="INSERT_OR_UPDATE">
    <file_name>screenshot.png</file_name>
    <content_type>image/png</content_type>
    <size_bytes>2193</size_bytes>
    <sys_created_by>jane.doe</sys_created_by>
    <sys_created_on>2023-05-05 23:15:01</sys_created_on>
    <sys_id>attach123</sys_id>
  </sys_attachment>
</unload>"""
        
        self.root = ET.fromstring(self.sample_xml)
        self.namespaces = {}
    
    def test_can_handle(self):
        """Test document type detection"""
        can_handle, confidence = self.handler.can_handle(self.root, self.namespaces)
        
        self.assertTrue(can_handle)
        self.assertGreater(confidence, 0.7)
    
    def test_detect_type(self):
        """Test ServiceNow type detection"""
        type_info = self.handler.detect_type(self.root, self.namespaces)
        
        self.assertEqual(type_info.type_name, "ServiceNow Incident")
        self.assertGreater(type_info.confidence, 0.9)
        self.assertEqual(type_info.metadata['primary_record_type'], 'incident')
        self.assertTrue(type_info.metadata['has_journal_entries'])
        self.assertTrue(type_info.metadata['has_attachments'])
    
    def test_extract_key_data(self):
        """Test key data extraction"""
        data = self.handler.extract_key_data(self.root)
        
        # Test ticket info extraction
        self.assertIn('ticket_info', data)
        ticket_info = data['ticket_info']
        self.assertEqual(ticket_info['number'], 'INC0001234')
        self.assertEqual(ticket_info['sys_id'], 'abc123def456')
        self.assertEqual(ticket_info['state'], '7')
        self.assertEqual(ticket_info['state_text'], 'Closed')
        
        # Test conversation thread extraction
        self.assertIn('conversation_thread', data)
        thread = data['conversation_thread']
        self.assertEqual(len(thread), 2)  # One comment, one work note
        
        # Test attachment extraction
        self.assertIn('attachments', data)
        attachments = data['attachments']
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0]['file_name'], 'screenshot.png')
        
        # Test timeline extraction
        self.assertIn('timeline', data)
        timeline = data['timeline']
        self.assertGreater(len(timeline), 0)
        
        # Test people extraction
        self.assertIn('people_involved', data)
        people = data['people_involved']
        self.assertIn('Jane Doe', people['requesters'])
        self.assertIn('John Smith', people['assignees'])
    
    def test_analyze(self):
        """Test comprehensive analysis"""
        analysis = self.handler.analyze(self.root, 'test.xml')
        
        # Check findings
        self.assertIn('record_type', analysis.key_findings)
        self.assertEqual(analysis.key_findings['record_type'], 'incident')
        self.assertEqual(analysis.key_findings['priority'], '4')
        self.assertEqual(analysis.key_findings['close_code'], 'Solved')
        
        # Check journal analysis
        self.assertIn('journal_analysis', analysis.key_findings)
        journal = analysis.key_findings['journal_analysis']
        self.assertEqual(journal['total_entries'], 2)
        self.assertEqual(journal['comments_count'], 1)
        self.assertEqual(journal['work_notes_count'], 1)
        
        # Check attachment analysis
        self.assertIn('attachment_analysis', analysis.key_findings)
        attachments = analysis.key_findings['attachment_analysis']
        self.assertEqual(attachments['total_attachments'], 1)
        self.assertIn('image/png', attachments['attachment_types'])
        
        # Check SLA metrics
        self.assertIn('sla_metrics', analysis.key_findings)
        sla = analysis.key_findings['sla_metrics']
        self.assertTrue(sla['made_sla'])
        self.assertEqual(sla['sla_percentage'], '857.26')
        
        # Check workflow analysis
        self.assertIn('workflow_analysis', analysis.key_findings)
        workflow = analysis.key_findings['workflow_analysis']
        self.assertEqual(workflow['reassignment_count'], '2')
        self.assertEqual(workflow['reopen_count'], '0')
        
        # Check recommendations
        self.assertIsInstance(analysis.recommendations, list)
        self.assertGreater(len(analysis.recommendations), 0)
        
        # Check AI use cases
        self.assertIsInstance(analysis.ai_use_cases, list)
        self.assertGreater(len(analysis.ai_use_cases), 5)
    
    def test_custom_fields_extraction(self):
        """Test extraction of custom fields (u_ prefix)"""
        incident = self.root.find('.//incident')
        custom_fields = self.handler._extract_custom_fields(incident)
        
        self.assertIn('u_state_text', custom_fields)
        self.assertIn('u_sla_percentage', custom_fields)
        self.assertIn('u_custom_field', custom_fields)
        self.assertEqual(custom_fields['u_custom_field'], 'Custom value')
    
    def test_minimal_servicenow_xml(self):
        """Test handling of minimal ServiceNow XML"""
        minimal_xml = """<?xml version="1.0" ?>
<unload>
  <incident action="INSERT_OR_UPDATE">
    <number>INC0001234</number>
    <short_description>Test incident</short_description>
    <state>1</state>
  </incident>
</unload>"""
        
        root = ET.fromstring(minimal_xml)
        can_handle, confidence = self.handler.can_handle(root, {})
        
        self.assertTrue(can_handle)
        self.assertGreater(confidence, 0.5)
        
        # Should still analyze without errors
        analysis = self.handler.analyze(root, 'minimal.xml')
        self.assertIsNotNone(analysis)
    
    def test_problem_record_type(self):
        """Test handling of problem records"""
        problem_xml = """<?xml version="1.0" ?>
<unload>
  <problem action="INSERT_OR_UPDATE">
    <number>PRB0001234</number>
    <short_description>Test problem</short_description>
    <state>1</state>
  </problem>
</unload>"""
        
        root = ET.fromstring(problem_xml)
        type_info = self.handler.detect_type(root, {})
        
        self.assertEqual(type_info.type_name, "ServiceNow Problem")
        self.assertEqual(type_info.metadata['primary_record_type'], 'problem')
    
    def test_quality_metrics(self):
        """Test quality metrics calculation"""
        metrics = self.handler._calculate_quality_metrics(self.root)
        
        self.assertIn('completeness', metrics)
        self.assertIn('consistency', metrics)
        self.assertIn('richness', metrics)
        
        # With our sample data, should have good completeness
        self.assertGreater(metrics['completeness'], 0.8)
        self.assertGreater(metrics['consistency'], 0.5)
        self.assertGreater(metrics['richness'], 0.1)


if __name__ == '__main__':
    unittest.main()