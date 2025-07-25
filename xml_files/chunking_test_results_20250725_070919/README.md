# XML Chunking Test Results

**Generated:** 2025-07-25 07:09:21

**Files Tested:** 63

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Files | 63 |
| Document Types | 1 |
| Strategy Configs | 12 |
| Unique Errors | 0 |

## Strategy Performance

| Strategy | Success Rate | Avg Chunks/File | Zero Chunk Rate |
|----------|--------------|-----------------|------------------|
| auto_large | 100.0% | 21.1 | 0.0% |
| auto_medium | 100.0% | 16.1 | 0.0% |
| auto_small | 100.0% | 14.9 | 0.0% |
| content_aware_large | 100.0% | 211.5 | 0.0% |
| content_aware_medium | 100.0% | 211.7 | 0.0% |
| content_aware_small | 100.0% | 212.2 | 0.0% |
| hierarchical_large | 100.0% | 5.6 | 66.7% |
| hierarchical_medium | 100.0% | 5.6 | 66.7% |
| hierarchical_small | 100.0% | 5.7 | 66.7% |
| sliding_window_large | 100.0% | 21.1 | 0.0% |
| sliding_window_medium | 100.0% | 16.1 | 0.0% |
| sliding_window_small | 100.0% | 14.9 | 0.0% |

## Document Types

| Type | Files | Total Size |
|------|-------|------------|
| Generic XML | 63 | 1.2 MB |

## Recommendations

- Strategy 'hierarchical_small' produces zero chunks for 66.7% of files - needs investigation
- Strategy 'hierarchical_medium' produces zero chunks for 66.7% of files - needs investigation
- Strategy 'hierarchical_large' produces zero chunks for 66.7% of files - needs investigation

## Files

- `chunking_test_results.json` - Complete detailed results
- `test_summary.json` - Summary statistics and analysis
- `chunks/` - Individual chunk files for each test
