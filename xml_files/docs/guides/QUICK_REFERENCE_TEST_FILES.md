# Quick Reference: Finding XML Test Files

## 🎯 Most Effective Searches

### GitHub Direct File Search
```
# Maven POMs
https://github.com/search?q=filename:pom.xml+size:>1000

# Spring configs  
https://github.com/search?q=filename:applicationContext.xml

# Log4j configs
https://github.com/search?q=filename:log4j2.xml+language:XML

# WSDL files
https://github.com/search?q=extension:wsdl+size:>1000
```

### Google Advanced Searches
```
# Large SCAP files
"asset-report-collection" filetype:xml site:github.com size:>1mb

# Real sitemap examples
sitemap.xml -site:sitemaps.org -inurl:schema

# Production Maven POMs
pom.xml "springframework" site:raw.githubusercontent.com

# DocBook examples
"<book" "docbook" filetype:xml -inurl:w3.org
```

## 🏆 Best Sources by Type

### Configuration Files
- **Spring**: Search Spring Boot starter projects
- **Maven**: Apache projects, Spring projects
- **Log4j**: Any enterprise Java project

### Standards-Based
- **SCAP/STIG**: DoD Cyber Exchange, NIST
- **XBRL**: SEC EDGAR database
- **HL7**: HL7.org examples section

### Web/API
- **WSDL**: Government services (.gov sites)
- **Sitemap**: Any major website + /sitemap.xml
- **RSS**: News sites, blogs, podcasts

## 💡 Pro Tips

1. **Use raw GitHub URLs**:
   - Change `github.com` to `raw.githubusercontent.com`
   - Direct download without HTML wrapper

2. **Filter by size**:
   - GitHub: `size:>1000` (in bytes)
   - Google: Add "MB" or "KB" to search

3. **Find test directories**:
   - `path:/test/ extension:xml`
   - `path:/sample/ extension:xml`
   - `path:/example/ extension:xml`

4. **Exclude docs/specs**:
   - `-site:w3.org`
   - `-inurl:specification`
   - `-inurl:schema`

## 🔗 Direct Links to Examples

### Always Available
- Maven: https://repo1.maven.org/maven2/ (browse any project)
- Spring: https://start.spring.io/ (generate then export)
- WordPress: Any WordPress site + /sitemap.xml

### Public Datasets
- Government: https://www.data.gov (search for XML)
- Academic: https://datadryad.org (search by format)
- GIS: https://www.openstreetmap.org (export KML)

## ⚡ Quick Collection Script

```bash
# Download a file quickly
curl -O https://raw.githubusercontent.com/[user]/[repo]/[branch]/[file.xml]

# Download all XML from a repo
git clone --depth 1 [repo-url]
find . -name "*.xml" -type f -exec cp {} ./collected/ \;

# Validate all collected files
for f in *.xml; do xmllint --noout "$f" 2>/dev/null && echo "✓ $f" || echo "✗ $f"; done
```
