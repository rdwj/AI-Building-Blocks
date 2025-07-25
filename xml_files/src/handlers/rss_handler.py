#!/usr/bin/env python3
"""
RSS/Atom Feed Handler

Analyzes RSS and Atom feed documents for content syndication,
news aggregation, and content distribution systems.
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Tuple
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer import XMLHandler, DocumentTypeInfo, SpecializedAnalysis


class RSSHandler(XMLHandler):
    """Handler for RSS feed documents"""
    
    def can_handle(self, root: ET.Element, namespaces: Dict[str, str]) -> Tuple[bool, float]:
        if root.tag == 'rss' or root.tag.endswith('}rss'):
            return True, 1.0
        if root.tag == 'feed':  # Atom feeds
            return True, 0.9
        return False, 0.0
    
    def detect_type(self, root: ET.Element, namespaces: Dict[str, str]) -> DocumentTypeInfo:
        version = root.get('version', '2.0')
        feed_type = 'RSS' if root.tag.endswith('rss') else 'Atom'
        
        return DocumentTypeInfo(
            type_name=f"{feed_type} Feed",
            confidence=1.0,
            version=version,
            metadata={
                "standard": feed_type,
                "category": "content_syndication"
            }
        )
    
    def analyze(self, root: ET.Element, file_path: str) -> SpecializedAnalysis:
        channel = root.find('.//channel') or root
        items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
        
        findings = {
            'total_items': len(items),
            'has_descriptions': sum(1 for item in items if item.find('.//description') is not None),
            'has_dates': sum(1 for item in items if item.find('.//pubDate') is not None),
            'categories': self._extract_categories(items)
        }
        
        recommendations = [
            "Use for content aggregation and analysis",
            "Extract for trend analysis and topic modeling",
            "Monitor for content updates and changes"
        ]
        
        ai_use_cases = [
            "Content categorization and tagging",
            "Trend detection and analysis",
            "Sentiment analysis on articles",
            "Topic modeling and clustering",
            "Content recommendation systems"
        ]
        
        return SpecializedAnalysis(
            document_type="RSS/Atom Feed",
            key_findings=findings,
            recommendations=recommendations,
            data_inventory={'articles': len(items), 'categories': len(findings['categories'])},
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_key_data(root),
            quality_metrics=self._calculate_feed_quality(root, items)
        )
    
    def extract_key_data(self, root: ET.Element) -> Dict[str, Any]:
        items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
        
        return {
            'feed_metadata': self._extract_feed_metadata(root),
            'items': [self._extract_item_data(item) for item in items[:10]]  # First 10 items
        }
    
    def _extract_categories(self, items) -> List[str]:
        categories = set()
        for item in items:
            for cat in item.findall('.//category'):
                if cat.text:
                    categories.add(cat.text)
        return list(categories)
    
    def _extract_feed_metadata(self, root: ET.Element) -> Dict[str, Any]:
        channel = root.find('.//channel') or root
        return {
            'title': getattr(channel.find('.//title'), 'text', None),
            'description': getattr(channel.find('.//description'), 'text', None),
            'link': getattr(channel.find('.//link'), 'text', None)
        }
    
    def _extract_item_data(self, item: ET.Element) -> Dict[str, Any]:
        return {
            'title': getattr(item.find('.//title'), 'text', None),
            'description': getattr(item.find('.//description'), 'text', None),
            'pubDate': getattr(item.find('.//pubDate'), 'text', None),
            'link': getattr(item.find('.//link'), 'text', None)
        }
    
    def _calculate_feed_quality(self, root: ET.Element, items: List[ET.Element]) -> Dict[str, float]:
        total = len(items)
        if total == 0:
            return {"completeness": 0.0, "consistency": 0.0, "data_density": 0.0}
        
        with_desc = sum(1 for item in items if item.find('.//description') is not None)
        with_date = sum(1 for item in items if item.find('.//pubDate') is not None)
        
        return {
            "completeness": (with_desc + with_date) / (2 * total),
            "consistency": 1.0 if with_desc == total else with_desc / total,
            "data_density": 0.8  # Typical for RSS feeds
        }