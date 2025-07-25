#!/usr/bin/env python3
"""
Test File Collection Helper

This script helps automate the collection of XML test files for the framework.
It creates the directory structure and provides utilities for downloading examples.
"""

import os
import sys
import urllib.request
import urllib.parse
from pathlib import Path
import hashlib
import json

class TestFileCollector:
    def __init__(self, base_dir="test_files"):
        self.base_dir = Path(base_dir)
        self.metadata_file = self.base_dir / "metadata.json"
        self.metadata = {}
        
    def setup_directories(self):
        """Create the recommended directory structure"""
        directories = [
            # Size-based directories
            "small/pom", "small/rss", "small/config", "small/spring", 
            "small/log4j", "small/svg", "small/sitemap",
            
            "medium/scap", "medium/docbook", "medium/wsdl", "medium/xsd",
            "medium/kml", "medium/dita", "medium/tei",
            
            "large/scap", "large/xbrl", "large/hl7", "large/docbook",
            
            # Special categories
            "edge_cases/malformed", "edge_cases/encodings", 
            "edge_cases/deeply_nested", "edge_cases/huge",
            
            "real_world/enterprise", "real_world/open_source", 
            "real_world/government", "real_world/academic"
        ]
        
        for dir_path in directories:
            full_path = self.base_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            
        print(f"✅ Created directory structure under {self.base_dir}/")
        
    def download_file(self, url, category, filename=None):
        """Download a file and save it in the appropriate category"""
        try:
            # Determine filename
            if not filename:
                filename = os.path.basename(urllib.parse.urlparse(url).path)
                if not filename:
                    filename = hashlib.md5(url.encode()).hexdigest()[:8] + ".xml"
            
            # Determine save path
            save_path = self.base_dir / category / filename
            
            # Download file
            print(f"📥 Downloading: {url}")
            urllib.request.urlretrieve(url, save_path)
            
            # Get file size
            file_size = save_path.stat().st_size
            
            # Save metadata
            self.metadata[str(save_path)] = {
                "url": url,
                "size": file_size,
                "category": category,
                "hash": self._calculate_hash(save_path)
            }
            
            print(f"✅ Saved to: {save_path} ({file_size:,} bytes)")
            return save_path
            
        except Exception as e:
            print(f"❌ Failed to download {url}: {e}")
            return None
    
    def _calculate_hash(self, filepath):
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def save_metadata(self):
        """Save metadata about collected files"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        print(f"💾 Saved metadata to {self.metadata_file}")
    
    def validate_xml(self, filepath):
        """Basic XML validation"""
        try:
            import xml.etree.ElementTree as ET
            ET.parse(filepath)
            return True
        except ET.ParseError as e:
            print(f"⚠️  Invalid XML in {filepath}: {e}")
            return False
    
    def generate_synthetic_examples(self):
        """Generate synthetic test files for various types"""
        
        # Small Maven POM
        pom_content = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example.test</groupId>
    <artifactId>test-artifact</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <packaging>jar</packaging>
    
    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
    </properties>
    
    <dependencies>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>4.13.2</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>"""
        
        self._save_synthetic("small/pom/synthetic_simple.xml", pom_content)
        
        # Simple RSS feed
        rss_content = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Test Feed</title>
        <link>http://example.com</link>
        <description>A test RSS feed</description>
        <item>
            <title>Test Article</title>
            <link>http://example.com/article1</link>
            <description>This is a test article</description>
            <pubDate>Wed, 23 Jul 2025 12:00:00 GMT</pubDate>
        </item>
    </channel>
</rss>"""
        
        self._save_synthetic("small/rss/synthetic_simple.xml", rss_content)
        
        print("✅ Generated synthetic examples")
    
    def _save_synthetic(self, path, content):
        """Save synthetic content"""
        full_path = self.base_dir / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        
        self.metadata[str(full_path)] = {
            "url": "synthetic",
            "size": len(content),
            "category": str(Path(path).parent),
            "hash": hashlib.sha256(content.encode()).hexdigest()
        }

def main():
    collector = TestFileCollector()
    
    print("🚀 XML Test File Collection Helper")
    print("==================================")
    
    # Setup directories
    collector.setup_directories()
    
    # Generate synthetic examples
    collector.generate_synthetic_examples()
    
    # Example: Download some public files
    # NOTE: These are examples - replace with actual URLs you find
    
    example_downloads = [
        # Example Maven POM from Spring Boot
        # ("https://raw.githubusercontent.com/spring-projects/spring-boot/main/pom.xml", "medium/pom"),
        
        # Add more examples here based on your searches
    ]
    
    for url, category in example_downloads:
        collector.download_file(url, category)
    
    # Save metadata
    collector.save_metadata()
    
    print("\n📋 Summary:")
    print(f"Total files collected: {len(collector.metadata)}")
    
    # Validate all XML files
    valid_count = 0
    for filepath in collector.metadata:
        if collector.validate_xml(filepath):
            valid_count += 1
    
    print(f"Valid XML files: {valid_count}/{len(collector.metadata)}")
    
    print("\n✅ Collection complete!")
    print(f"Files are in: {collector.base_dir}/")
    print(f"Metadata saved to: {collector.metadata_file}")

if __name__ == "__main__":
    main()
