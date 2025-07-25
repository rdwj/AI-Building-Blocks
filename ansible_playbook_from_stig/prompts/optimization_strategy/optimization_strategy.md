# Granite 3.3 8B Optimization Strategy

## 🎯 **Why This Two-Phase Approach Works**

### **Phase 1: Classification (Focused Decision)**
- 8B models excel at simple classification tasks
- Clear keyword-based decision making
- Single output reduces complexity
- Fast processing for 1,094 findings

### **Phase 2: Specialized Processing (Domain-Specific)**
- Each prompt is optimized for specific complexity type
- Smaller context window per specialized task
- Higher accuracy than generic "do everything" prompt
- Consistent JSON schema per category

## ⚡ **Performance Optimizations**

### **Batch Processing Strategy**
```python
# Process in batches of 10-20 findings
batch_size = 15
for i in range(0, len(unknown_findings), batch_size):
    batch = unknown_findings[i:i+batch_size]
    process_batch_async(batch)
```

### **Prompt Length Management**
- Keep fix_text under 2000 characters for 8B model
- Truncate very long shell scripts: `fix_text[:2000] + "..."`
- Focus on first few conditional statements

### **Context Window Optimization**
```python
def optimize_finding_for_8b(finding):
    return {
        'rule_id': finding['rule_id'],
        'title': finding['title'][:100],  # Truncate long titles
        'description': finding['description'][:300],  # Key info only
        'fix_text': finding['fix_text'][:2000]  # Most important part
    }
```

## 🛠 **Implementation Strategy**

### **Step 1: Classification Filter**
```python
# Filter your 1,094 unknown findings
shell_scripts = []
package_verifications = []
config_modifications = []
# ... etc

for finding in unknown_findings:
    classification = classify_finding(finding)
    category_map[classification].append(finding)
```

### **Step 2: Batch by Category**
```python
# Process each category with its specialized prompt
results = {}
for category, findings in category_map.items():
    results[category] = process_category_batch(findings, category)
```

### **Step 3: Quality Validation**
```python
def validate_output(result):
    required_fields = ['target_type', 'target_name', 'ansible_module']
    return all(field in result for field in required_fields)
```

## 🔧 **Model-Specific Tuning**

### **Temperature Settings**
- Classification: `temperature=0.1` (deterministic)
- Task Generation: `temperature=0.3` (some creativity)

### **Token Limits**
- Input: ~3000 tokens max for 8B model
- Output: ~1000 tokens max for complex JSON

### **Retry Strategy**
```python
def call_granite_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = call_granite_3_3_8b(prompt)
            if validate_json(result):
                return result
        except Exception as e:
            if attempt == max_retries - 1:
                return fallback_response()
    return None
```

## 📊 **Expected Results**

### **Processing Time Estimates**
- Classification: ~2 seconds per finding
- Specialized processing: ~5 seconds per finding  
- Total for 1,094 findings: ~2 hours
- **vs Manual work: ~200+ hours**

### **Quality Expectations**
- **Shell Scripts**: 85-90% accuracy (clear patterns)
- **Package Verification**: 80-85% accuracy (complex logic)
- **Config Modification**: 90-95% accuracy (well-defined)
- **Boot Configuration**: 75-80% accuracy (high complexity)
- **Multi-step**: 80-85% accuracy (good at sequencing)
- **Cron Jobs**: 95%+ accuracy (simple patterns)

### **Manual Review Required**
- ~15-20% of outputs will need human review
- Still saves 80%+ of manual effort
- Focus review on boot-critical and complex shell scripts

## 🚀 **Deployment Recommendations**

### **Development Environment**
1. Test with 10-20 findings first
2. Validate output quality manually
3. Adjust prompts based on failure patterns
4. Scale to full 1,094 findings

### **Production Pipeline**
```python
def production_pipeline():
    # 1. Load 1,094 unknown findings
    # 2. Classify all findings (fast)
    # 3. Process by category (parallel)
    # 4. Validate outputs
    # 5. Flag for manual review if needed
    # 6. Generate final Ansible playbooks
    pass
```

### **Quality Assurance**
- Spot-check 10% of outputs manually
- Test generated playbooks in sandbox environment
- Monitor for common failure patterns
- Iteratively improve prompts

## 💡 **Pro Tips for 8B Model**

### **Prompt Engineering**
- Use **specific examples** in prompts
- **Bold important instructions**
- Keep sentences short and clear
- Use **bullet points** for guidelines
- End with "Return only valid JSON"

### **Error Handling**
- Always validate JSON parsing
- Have fallback responses ready
- Log failures for prompt improvement
- Use classification confidence scoring

### **Continuous Improvement**
- Track which categories have high failure rates
- Collect failed cases for prompt refinement
- A/B test prompt variations
- Build feedback loop from manual review

## 🎯 **Success Metrics**

- **Speed**: 2 hours vs 200+ hours manual
- **Quality**: 80%+ accuracy requiring minimal review
- **Coverage**: Process all 1,094 complex findings
- **Cost**: ~$5-10 in inference costs vs weeks of human time

**Bottom Line: This approach gives you 80%+ automation of your most complex STIG findings while keeping costs low and quality high!**