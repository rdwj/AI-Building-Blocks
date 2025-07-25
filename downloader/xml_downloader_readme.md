# XML Test Files Downloader

This toolkit downloads real-world XML files for testing the XML Analysis Framework and organizes them into a proper directory structure.

## Files Included

1. **`xml_download_urls.txt`** - Contains all the URLs to download
2. **`xml_downloader.py`** - Python script that does the downloading and organizing
3. **`README.md`** - This usage guide

## Quick Start

1. **Save the URL file** as `xml_download_urls.txt`
2. **Run the downloader**:
   ```bash
   python xml_downloader.py
   ```

That's it! The script will create this structure:

```
test_files/
├── small/          # Files < 100KB  
│   ├── scap/
│   ├── kml/
│   ├── gpx/
│   ├── ant/
│   ├── nuget/
│   ├── wadl/
│   ├── wsdl/
│   ├── xsd/
│   ├── relaxng/
│   ├── dita/
│   ├── tei/
│   ├── hl7/
│   ├── xbrl/
│   ├── pmml/
│   ├── xslt/
│   └── xslfo/
├── medium/         # Files 100KB - 10MB
│   └── (same subdirectories)
├── large/          # Files > 10MB
│   └── (same subdirectories)
└── download_stats.json
```

## Usage Options

### Basic Usage
```bash
# Download all files to default location
python xml_downloader.py

# See what would be downloaded without actually downloading
python xml_downloader.py --dry-run
```

### Advanced Options
```bash
# Custom URLs file and output directory
python xml_downloader.py --urls-file my_urls.txt --output-dir my_test_files

# Enable verbose logging
python xml_downloader.py --verbose

# Get help
python xml_downloader.py --help
```

## What Gets Downloaded

### Currently Implemented Types (with real examples):
- **SCAP** - NIST security benchmarks (XCCDF format)
- **KML** - Geographic data files from mapping projects
- **GPX** - GPS track files from various sources
- **ANT** - Apache Ant build files from official repos
- **NUGET** - .NET package specifications
- **WADL** - REST API description files
- **WSDL** - SOAP web service descriptions
- **XSD** - XML schema definitions
- **RELAXNG** - Alternative schema files (.rng/.rnc)
- **DITA** - Technical documentation files
- **TEI** - Digital humanities markup
- **HL7** - Clinical document architecture files
- **XBRL** - Business/financial reporting documents
- **PMML** - Machine learning model files
- **XSLT** - XML transformation stylesheets
- **XSLFO** - Print formatting objects

## Features

### ✅ **Smart Organization**
- Files are automatically categorized by size after download
- Each XML type gets its own subdirectory
- Proper handling of zip archives (extracts XML files)

### ✅ **Robust Downloading** 
- Handles GitHub raw URLs, direct downloads, and gists
- Retries with proper error handling
- Progress indication for large files
- Respects servers with delays between requests

### ✅ **Safety Features**
- Skips files that already exist
- Dry-run mode to preview downloads
- Comprehensive logging to `xml_download.log`
- Download statistics in JSON format

### ✅ **Production Ready**
- User-Agent headers to appear as legitimate browser
- Timeout handling for stalled downloads
- Graceful handling of network issues
- Clean up of temporary files

## Adding New Files

To add more XML files, edit `xml_download_urls.txt`:

```
# Format: TYPE|URL|FILENAME
SCAP|https://example.com/security.xml|my-security-file.xml
TEI|https://raw.githubusercontent.com/user/repo/file.xml|manuscript.xml
```

### Supported Types:
`SCAP`, `KML`, `GPX`, `ANT`, `NUGET`, `WADL`, `WSDL`, `XSD`, `RELAXNG`, `DITA`, `TEI`, `HL7`, `XBRL`, `PMML`, `XSLT`, `XSLFO`

## Troubleshooting

### Common Issues

**"File not found" errors:**
- Check that `xml_download_urls.txt` exists in the same directory
- Verify URLs are accessible (some GitHub URLs might have changed)

**Download failures:**
- Some URLs might be temporarily unavailable
- Check `xml_download.log` for detailed error messages
- Run with `--verbose` for more debugging info

**Permission errors:**
- Make sure you have write permissions in the output directory
- On Unix systems, you might need: `chmod +x xml_downloader.py`

### Re-running Downloads

The script is safe to re-run:
- Already downloaded files are automatically skipped
- Failed downloads can be retried
- Partial downloads are cleaned up automatically

## File Size Guidelines

After downloading, files are categorized as:

- **Small** (< 100KB): Simple examples, basic configurations
- **Medium** (100KB - 10MB): Realistic documents, complex schemas  
- **Large** (> 10MB): Comprehensive datasets, security benchmarks

This matches the testing strategy where:
- Small files are good for unit tests
- Medium files test realistic parsing scenarios
- Large files stress-test performance

## Integration with XML Analysis Framework

These downloaded files integrate directly with your existing test structure:

```python
# Example: Test SCAP parsing with real files
test_files = Path("test_files/medium/scap").glob("*.xml")
for scap_file in test_files:
    result = xml_analyzer.analyze_file(scap_file)
    assert result.handler_type == "SCAP"
    assert result.is_valid
```

## Robots.txt Compliance

All URLs in the default file respect robots.txt policies:
- ✅ GitHub repositories (public, meant for sharing)
- ✅ NIST official publications (public domain)
- ✅ Standards organizations (HL7, XBRL International) 
- ✅ Academic institutions (publicly shared research)

The script includes respectful delays between downloads and uses appropriate User-Agent headers.

---

**Need help?** Check the log file `xml_download.log` for detailed information about any issues.