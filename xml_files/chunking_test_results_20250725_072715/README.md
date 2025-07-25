# XML Chunking Test Results

**Generated:** 2025-07-25 07:27:18

**Files Tested:** 63

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Files | 63 |
| Document Types | 30 |
| Strategy Configs | 12 |
| Unique Errors | 0 |

## Strategy Performance

| Strategy | Success Rate | Avg Chunks/File | Zero Chunk Rate |
|----------|--------------|-----------------|------------------|
| auto_large | 100.0% | 20.1 | 6.3% |
| auto_medium | 100.0% | 16.9 | 6.3% |
| auto_small | 100.0% | 16.9 | 6.3% |
| content_aware_large | 100.0% | 211.5 | 0.0% |
| content_aware_medium | 100.0% | 211.7 | 0.0% |
| content_aware_small | 100.0% | 212.2 | 0.0% |
| hierarchical_large | 100.0% | 6.5 | 57.1% |
| hierarchical_medium | 100.0% | 6.5 | 57.1% |
| hierarchical_small | 100.0% | 6.6 | 57.1% |
| sliding_window_large | 100.0% | 21.1 | 0.0% |
| sliding_window_medium | 100.0% | 16.1 | 0.0% |
| sliding_window_small | 100.0% | 14.9 | 0.0% |

## Document Types

| Type | Files | Total Size |
|------|-------|------------|
| Apache Ant Build | 5 | 0.2 MB |
| DocBook Documentation | 4 | 0.0 MB |
| Generic XML (ClinicalDocument) | 5 | 0.3 MB |
| Generic XML (PMML) | 3 | 0.0 MB |
| Generic XML (TEI) | 5 | 0.1 MB |
| Generic XML (package) | 1 | 0.0 MB |
| Generic XML (xbrl) | 1 | 0.0 MB |
| Hibernate Configuration | 1 | 0.0 MB |
| Hibernate Mapping | 3 | 0.0 MB |
| Ivy Module Descriptor | 2 | 0.0 MB |
| Ivy Settings | 1 | 0.0 MB |
| Log4j Configuration | 4 | 0.0 MB |
| Maven POM | 1 | 0.0 MB |
| RSS Feed | 1 | 0.0 MB |
| SAML 2.0 Assertion | 1 | 0.0 MB |
| SAML 2.0 Authentication Request | 1 | 0.0 MB |
| SAML 2.0 Logout Request | 1 | 0.0 MB |
| SAML 2.0 Response | 1 | 0.0 MB |
| SCAP Security Report | 1 | 0.0 MB |
| SCAP/XCCDF Document | 3 | 0.0 MB |
| SOAP 1.1 Fault | 1 | 0.0 MB |
| SOAP 1.1 Request | 1 | 0.0 MB |
| SOAP 1.1 Response | 1 | 0.0 MB |
| SOAP 1.2 Request | 1 | 0.0 MB |
| Spring Configuration | 1 | 0.0 MB |
| Struts Configuration | 3 | 0.0 MB |
| WADL API Description | 1 | 0.0 MB |
| XML Schema Definition | 5 | 0.5 MB |
| XML Sitemap | 3 | 0.0 MB |
| XML Sitemap Index | 1 | 0.0 MB |

## Recommendations

- Strategy 'hierarchical_small' produces zero chunks for 57.1% of files - needs investigation
- Strategy 'hierarchical_medium' produces zero chunks for 57.1% of files - needs investigation
- Strategy 'hierarchical_large' produces zero chunks for 57.1% of files - needs investigation

## Files

- `chunking_test_results.json` - Complete detailed results
- `test_summary.json` - Summary statistics and analysis
- `chunks/` - Individual chunk files for each test
