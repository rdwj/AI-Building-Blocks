#!/usr/bin/env python3
"""
Universal File Downloader

Downloads test files from various sources and organizes them into
a proper directory structure for testing document processing systems.

Supports: PDF, Office docs, data formats, programming languages, 
archives, images, web formats, and many more.

Usage:
    python file_downloader.py [--urls-file urls.txt] [--output-dir test_files] [--dry-run]
"""

import os
import sys
import argparse
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
import zipfile
import time
from typing import List, Tuple, Dict
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('file_download.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DocumentDownloader:
    """Downloads and organizes test files of various document types."""
    
    # Size thresholds in bytes
    SMALL_THRESHOLD = 100 * 1024      # 100KB
    MEDIUM_THRESHOLD = 10 * 1024 * 1024  # 10MB
    
    # Comprehensive directory mapping for document types
    TYPE_DIRS = {
        # === TEXT & DOCUMENT FORMATS ===
        'PDF': 'pdf',
        'RTF': 'rtf',           # Rich Text Format
        'TXT': 'txt',           # Plain text
        'LOG': 'logs',          # System/application logs
        
        # === OFFICE & PRODUCTIVITY ===
        'DOCX': 'office/docx',
        'DOC': 'office/doc',    # Legacy Word format
        'XLSX': 'office/xlsx', 
        'XLS': 'office/xls',
        'PPTX': 'office/pptx',
        'PPT': 'office/ppt',
        
        # OpenDocument formats
        'ODT': 'office/odt',    # OpenDocument Text
        'ODS': 'office/ods',    # OpenDocument Spreadsheet  
        'ODP': 'office/odp',    # OpenDocument Presentation
        
        # === DATA EXCHANGE FORMATS ===
        'JSON': 'data/json',
        'YAML': 'data/yaml',
        'TOML': 'data/toml',
        'CSV': 'data/csv',
        'TSV': 'data/tsv',      # Tab-separated values
        'JSONL': 'data/jsonl',  # JSON Lines / NDJSON
        'PARQUET': 'data/parquet', # Columnar data format
        
        # === WEB FORMATS ===
        'HTML': 'web/html',
        'CSS': 'web/css',
        'JS': 'web/javascript',
        'RSS': 'web/rss',       # RSS feeds (XML-based)
        'ATOM': 'web/atom',     # Atom feeds (XML-based)
        'SITEMAP': 'web/sitemap', # XML sitemaps
        
        # === PROGRAMMING LANGUAGES ===
        'PYTHON': 'code/python',
        'JAVA': 'code/java',
        'CPP': 'code/cpp',
        'CSHARP': 'code/csharp',
        'GO': 'code/go',
        'RUST': 'code/rust',
        'R': 'code/r',
        'SQL': 'code/sql',
        'SHELL': 'code/shell',  # Bash/shell scripts
        
        # === CONFIG & BUILD FILES ===
        'INI': 'config/ini',
        'CONF': 'config/conf',
        'ENV': 'config/env',
        'MAKEFILE': 'config/makefile',
        'DOCKERFILE': 'config/dockerfile',
        'PACKAGE_JSON': 'config/package-json',
        'REQUIREMENTS': 'config/requirements',
        'GRADLE': 'config/gradle',
        'MAVEN_POM': 'config/maven-pom',
        
        # === MARKUP & DOCUMENTATION ===
        'MARKDOWN': 'markup/markdown',
        'ASCIIDOC': 'markup/asciidoc',
        'RESTRUCTURED': 'markup/rst',  # reStructuredText
        'LATEX': 'markup/latex',
        'BIBTEX': 'markup/bibtex',
        
        # === ARCHIVE FORMATS ===
        'ZIP': 'archives/zip',
        'TAR': 'archives/tar',
        'GZ': 'archives/gzip',
        'RAR': 'archives/rar',
        'SEVEN_Z': 'archives/7z',
        
        # === IMAGE FORMATS (for metadata testing) ===
        'JPEG': 'images/jpeg',
        'PNG': 'images/png',
        'GIF': 'images/gif',
        'TIFF': 'images/tiff',
        'SVG': 'images/svg',    # Actually XML-based
        'WEBP': 'images/webp',
        
        # === E-BOOK & PUBLISHING ===
        'EPUB': 'ebooks/epub',  # E-book format (ZIP-based)
        'MOBI': 'ebooks/mobi',  # Kindle format
        'FB2': 'ebooks/fb2',    # FictionBook (XML-based)
        
        # === SCIENTIFIC & SPECIALIZED ===
        'NETCDF': 'scientific/netcdf',  # Scientific data
        'HDF5': 'scientific/hdf5',      # Hierarchical data
        'FITS': 'scientific/fits',      # Astronomy data
        'MATLAB': 'scientific/matlab',  # .mat files
        
        # === CALENDAR & CONTACTS ===
        'ICS': 'calendar/ics',    # iCalendar format
        'VCF': 'contacts/vcf',    # vCard format
        
        # === MULTIMEDIA (for metadata) ===
        'MP3': 'media/mp3',      # Audio metadata
        'MP4': 'media/mp4',      # Video metadata
        'FLAC': 'media/flac',    # Lossless audio
        
        # === XML SUBTYPES ===
        'XML_SCAP': 'xml/scap',
        'XML_KML': 'xml/kml',
        'XML_GPX': 'xml/gpx',
        'XML_ANT': 'xml/ant',
        'XML_NUGET': 'xml/nuget',
        'XML_WADL': 'xml/wadl',
        'XML_WSDL': 'xml/wsdl',
        'XML_XSD': 'xml/xsd',
        'XML_RELAXNG': 'xml/relaxng',
        'XML_DITA': 'xml/dita',
        'XML_TEI': 'xml/tei',
        'XML_HL7': 'xml/hl7',
        'XML_XBRL': 'xml/xbrl',
        'XML_PMML': 'xml/pmml',
        'XML_XSLT': 'xml/xslt',
        'XML_XSLFO': 'xml/xslfo'
    }
    
    # File extensions for different document types (for zip extraction)
    EXTENSION_MAP = {
        'PDF': ['.pdf'],
        'RTF': ['.rtf'],
        'TXT': ['.txt', '.text'],
        'LOG': ['.log'],
        
        # Office formats
        'DOCX': ['.docx'], 'DOC': ['.doc'],
        'XLSX': ['.xlsx'], 'XLS': ['.xls'],
        'PPTX': ['.pptx'], 'PPT': ['.ppt'],
        'ODT': ['.odt'], 'ODS': ['.ods'], 'ODP': ['.odp'],
        
        # Data formats
        'JSON': ['.json'], 'YAML': ['.yaml', '.yml'], 'TOML': ['.toml'],
        'CSV': ['.csv'], 'TSV': ['.tsv'], 'JSONL': ['.jsonl', '.ndjson'],
        'PARQUET': ['.parquet'],
        
        # Web formats
        'HTML': ['.html', '.htm'], 'CSS': ['.css'], 'JS': ['.js'],
        'RSS': ['.rss', '.xml'], 'ATOM': ['.atom', '.xml'],
        'SITEMAP': ['.xml'],
        
        # Programming languages
        'PYTHON': ['.py', '.pyx', '.pyi'], 'JAVA': ['.java'],
        'CPP': ['.cpp', '.cc', '.cxx', '.c', '.h', '.hpp'],
        'CSHARP': ['.cs'], 'GO': ['.go'], 'RUST': ['.rs'],
        'R': ['.r', '.R'], 'SQL': ['.sql'], 'SHELL': ['.sh', '.bash'],
        
        # Config files
        'INI': ['.ini'], 'CONF': ['.conf', '.config'],
        'ENV': ['.env'], 'DOCKERFILE': ['dockerfile', 'Dockerfile'],
        'PACKAGE_JSON': ['.json'], 'REQUIREMENTS': ['.txt'],
        'GRADLE': ['.gradle'], 'MAVEN_POM': ['.xml'],
        
        # Markup
        'MARKDOWN': ['.md', '.markdown'], 'ASCIIDOC': ['.adoc', '.asciidoc'],
        'RESTRUCTURED': ['.rst'], 'LATEX': ['.tex', '.latex'],
        'BIBTEX': ['.bib'],
        
        # Archives
        'ZIP': ['.zip'], 'TAR': ['.tar'], 'GZ': ['.gz', '.gzip'],
        'RAR': ['.rar'], 'SEVEN_Z': ['.7z'],
        
        # Images
        'JPEG': ['.jpg', '.jpeg'], 'PNG': ['.png'], 'GIF': ['.gif'],
        'TIFF': ['.tiff', '.tif'], 'SVG': ['.svg'], 'WEBP': ['.webp'],
        
        # E-books
        'EPUB': ['.epub'], 'MOBI': ['.mobi'], 'FB2': ['.fb2'],
        
        # Scientific
        'NETCDF': ['.nc'], 'HDF5': ['.h5', '.hdf5'],
        'FITS': ['.fits'], 'MATLAB': ['.mat'],
        
        # Calendar/Contacts
        'ICS': ['.ics'], 'VCF': ['.vcf'],
        
        # Media
        'MP3': ['.mp3'], 'MP4': ['.mp4'], 'FLAC': ['.flac'],
        
        # XML types
        'XML_SCAP': ['.xml'], 'XML_KML': ['.kml'], 'XML_GPX': ['.gpx'],
        'XML_ANT': ['.xml'], 'XML_NUGET': ['.xml'], 'XML_WADL': ['.xml'],
        'XML_WSDL': ['.wsdl'], 'XML_XSD': ['.xsd'], 'XML_RELAXNG': ['.rng', '.rnc'],
        'XML_DITA': ['.xml'], 'XML_TEI': ['.xml'], 'XML_HL7': ['.xml'],
        'XML_XBRL': ['.xml'], 'XML_PMML': ['.xml'], 'XML_XSLT': ['.xsl', '.xslt'],
        'XML_XSLFO': ['.xsl']
    }
    
    def __init__(self, output_dir: str = "test_files", dry_run: bool = False):
        self.output_dir = Path(output_dir)
        self.dry_run = dry_run
        self.download_stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'sizes': {'small': 0, 'medium': 0, 'large': 0}
        }
        
        # Create base directory structure
        self.create_directory_structure()
    
    def create_directory_structure(self):
        """Create the base directory structure."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create directory structure in {self.output_dir}")
            return
            
        for size_category in ['small', 'medium', 'large']:
            for doc_type, type_dir in self.TYPE_DIRS.items():
                dir_path = self.output_dir / size_category / type_dir
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Created directory: {dir_path}")
    
    def parse_urls_file(self, urls_file: str) -> List[Tuple[str, str, str]]:
        """Parse the URLs file and return list of (type, url, filename) tuples."""
        urls = []
        
        try:
            with open(urls_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse TYPE|URL|FILENAME format
                    parts = line.split('|')
                    if len(parts) != 3:
                        logger.warning(f"Line {line_num}: Invalid format, expected TYPE|URL|FILENAME")
                        continue
                    
                    doc_type, url, filename = [part.strip() for part in parts]
                    
                    if doc_type not in self.TYPE_DIRS:
                        logger.warning(f"Line {line_num}: Unknown document type '{doc_type}'")
                        continue
                    
                    urls.append((doc_type, url, filename))
                    
        except FileNotFoundError:
            logger.error(f"URLs file not found: {urls_file}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error reading URLs file: {e}")
            sys.exit(1)
        
        logger.info(f"Parsed {len(urls)} URLs from {urls_file}")
        return urls
    
    def download_file(self, url: str, temp_path: Path) -> bool:
        """Download a file to a temporary location."""
        try:
            # Add headers to appear as a regular browser
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Python Document Downloader)',
                    'Accept': '*/*'
                }
            )
            
            logger.info(f"Downloading: {url}")
            
            with urllib.request.urlopen(req, timeout=30) as response:
                with open(temp_path, 'wb') as f:
                    # Download in chunks to show progress for large files
                    chunk_size = 8192
                    total_size = response.headers.get('Content-Length')
                    
                    if total_size:
                        total_size = int(total_size)
                        downloaded = 0
                        
                        while chunk := response.read(chunk_size):
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if total_size > 1024 * 1024:  # Show progress for files > 1MB
                                percent = (downloaded / total_size) * 100
                                print(f"\rProgress: {percent:.1f}%", end='', flush=True)
                        
                        if total_size > 1024 * 1024:
                            print()  # New line after progress
                    else:
                        f.write(response.read())
            
            return True
            
        except urllib.error.HTTPError as e:
            logger.error(f"HTTP Error {e.code}: {url}")
            return False
        except urllib.error.URLError as e:
            logger.error(f"URL Error: {e.reason}: {url}")
            return False
        except Exception as e:
            logger.error(f"Download error for {url}: {e}")
            return False
    
    def get_file_size_category(self, file_path: Path) -> str:
        """Determine size category based on file size."""
        try:
            size = file_path.stat().st_size
            
            if size < self.SMALL_THRESHOLD:
                return 'small'
            elif size < self.MEDIUM_THRESHOLD:
                return 'medium'
            else:
                return 'large'
                
        except Exception:
            return 'small'  # Default to small if can't determine size
    
    def get_target_extensions(self, doc_type: str) -> List[str]:
        """Get the target file extensions for a document type."""
        return self.EXTENSION_MAP.get(doc_type, [])
    
    def handle_zip_file(self, zip_path: Path, doc_type: str) -> List[Path]:
        """Extract zip file and return paths to extracted files."""
        extracted_files = []
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Get target extensions for this document type
                target_extensions = self.get_target_extensions(doc_type)
                
                # If no specific extensions, extract common document files
                if not target_extensions:
                    target_extensions = ['.txt', '.md', '.json', '.xml', '.csv', '.py', '.html']
                
                # Get list of relevant files in the zip
                target_files = [f for f in zip_ref.namelist() 
                              if any(f.lower().endswith(ext) for ext in target_extensions)]
                
                if not target_files:
                    logger.warning(f"No relevant files found in {zip_path}")
                    return extracted_files
                
                # Extract to a temporary directory
                extract_dir = zip_path.parent / f"{zip_path.stem}_extracted"
                extract_dir.mkdir(exist_ok=True)
                
                for target_file in target_files[:5]:  # Limit to first 5 files to avoid spam
                    try:
                        zip_ref.extract(target_file, extract_dir)
                        extracted_path = extract_dir / target_file
                        
                        if extracted_path.is_file():
                            extracted_files.append(extracted_path)
                            logger.info(f"Extracted: {target_file}")
                            
                    except Exception as e:
                        logger.warning(f"Failed to extract {target_file}: {e}")
                
        except Exception as e:
            logger.error(f"Failed to process zip file {zip_path}: {e}")
        
        return extracted_files
    
    def move_to_final_location(self, temp_path: Path, doc_type: str, filename: str) -> bool:
        """Move file from temp location to final categorized location."""
        try:
            # Determine size category
            size_category = self.get_file_size_category(temp_path)
            
            # Create final path
            type_dir = self.TYPE_DIRS[doc_type]
            final_path = self.output_dir / size_category / type_dir / filename
            
            # Ensure directory exists
            final_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file
            temp_path.rename(final_path)
            
            # Log file info
            size_kb = temp_path.stat().st_size / 1024 if temp_path.exists() else final_path.stat().st_size / 1024
            logger.info(f"Saved: {final_path} ({size_kb:.1f} KB, {size_category})")
            
            # Update stats
            self.download_stats['sizes'][size_category] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to move {temp_path} to final location: {e}")
            return False
    
    def download_and_organize(self, urls_list: List[Tuple[str, str, str]]):
        """Download and organize all files."""
        self.download_stats['total'] = len(urls_list)
        temp_dir = self.output_dir / 'temp'
        temp_dir.mkdir(exist_ok=True)
        
        for i, (doc_type, url, filename) in enumerate(urls_list, 1):
            logger.info(f"\n=== Processing {i}/{len(urls_list)}: {filename} ===")
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would download {url} -> {filename}")
                continue
            
            temp_path = temp_dir / f"temp_{i}_{filename}"
            
            # Check if final file already exists
            for size_cat in ['small', 'medium', 'large']:
                final_path = self.output_dir / size_cat / self.TYPE_DIRS[doc_type] / filename
                if final_path.exists():
                    logger.info(f"File already exists: {final_path}")
                    self.download_stats['skipped'] += 1
                    break
            else:
                # Download file
                if self.download_file(url, temp_path):
                    # Handle zip files
                    if filename.lower().endswith('.zip'):
                        extracted_files = self.handle_zip_file(temp_path, doc_type)
                        
                        if extracted_files:
                            # Move extracted files
                            for j, extracted_path in enumerate(extracted_files):
                                extract_filename = f"{Path(filename).stem}_{j+1}_{extracted_path.name}"
                                if self.move_to_final_location(extracted_path, doc_type, extract_filename):
                                    self.download_stats['success'] += 1
                                else:
                                    self.download_stats['failed'] += 1
                        
                        # Clean up zip file
                        temp_path.unlink(missing_ok=True)
                    else:
                        # Move regular file
                        if self.move_to_final_location(temp_path, doc_type, filename):
                            self.download_stats['success'] += 1
                        else:
                            self.download_stats['failed'] += 1
                else:
                    self.download_stats['failed'] += 1
                    # Clean up failed download
                    temp_path.unlink(missing_ok=True)
            
            # Small delay to be respectful to servers
            time.sleep(0.5)
        
        # Clean up temp directory
        try:
            temp_dir.rmdir()
        except OSError:
            pass  # Directory not empty or other issue
    
    def print_summary(self):
        """Print download summary."""
        print("\n" + "="*60)
        print("DOWNLOAD SUMMARY")
        print("="*60)
        print(f"Total files processed: {self.download_stats['total']}")
        print(f"Successfully downloaded: {self.download_stats['success']}")
        print(f"Failed downloads: {self.download_stats['failed']}")
        print(f"Skipped (already exist): {self.download_stats['skipped']}")
        print()
        print("Files by size category:")
        for size_cat, count in self.download_stats['sizes'].items():
            print(f"  {size_cat.capitalize()}: {count}")
        print()
        print(f"Files organized in: {self.output_dir.absolute()}")
        
        # Save stats to JSON
        stats_file = self.output_dir / 'download_stats.json'
        try:
            with open(stats_file, 'w') as f:
                json.dump(self.download_stats, f, indent=2)
            print(f"Stats saved to: {stats_file}")
        except Exception as e:
            logger.warning(f"Could not save stats: {e}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Download test files and organize them by type and size"
    )
    parser.add_argument(
        '--urls-file', 
        default='download_urls.txt',
        help='File containing URLs to download (default: download_urls.txt)'
    )
    parser.add_argument(
        '--output-dir',
        default='test_files',
        help='Output directory for downloaded files (default: test_files)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually downloading'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create downloader
    downloader = DocumentDownloader(args.output_dir, args.dry_run)
    
    # Parse URLs file
    urls_list = downloader.parse_urls_file(args.urls_file)
    
    if not urls_list:
        logger.error("No valid URLs found to download")
        sys.exit(1)
    
    # Download and organize files
    try:
        downloader.download_and_organize(urls_list)
    except KeyboardInterrupt:
        logger.info("\nDownload interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    
    # Print summary
    downloader.print_summary()


if __name__ == '__main__':
    main()
