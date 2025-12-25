# ai-governance-controls

**Translate AI governance requirements into auditable, testable controls.**

A practical toolkit demonstrating how to operationalize AI governance frameworks (NIST AI RMF, EU AI Act) into machine-readable control catalogs with automated compliance evaluation.

[![Try It Live](https://img.shields.io/badge/Try%20It%20Live-Visit%20Site-blue?style=for-the-badge)](https://delschlangen.github.io/ai-governance-controls)

> **[Use the interactive evaluator →](https://delschlangen.github.io/ai-governance-controls)** — No installation required. Paste your system profile JSON and get instant compliance results in your browser.

## Why This Exists

Policy documents don't protect anyone—implemented controls do. This repo bridges the gap between governance frameworks sitting in PDFs and operational compliance that can be tested, measured, and reported. Built from experience translating complex risk requirements into actionable product capabilities.

## Quick Start

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/ai-governance-controls.git
cd ai-governance-controls

# Install dependency
pip install pyyaml

# Run the unified CLI
python src/main.py --help

# Or run individual tools
python src/validate_controls.py
python src/evaluate_profile.py
python src/risk_tier.py
```

## Features

### Unified CLI (`main.py`)

The toolkit provides a unified command-line interface for all operations:

```bash
# Validate the control catalog
python src/main.py validate

# Evaluate a system against controls
python src/main.py evaluate -p my_system.json

# Classify under EU AI Act risk tiers
python src/main.py classify -p my_system.json

# Generate a new system profile template
python src/main.py init -o new_system.json

# Generate comprehensive compliance report
python src/main.py report -p my_system.json -o report.json
```

### Multiple Output Formats

All tools support multiple output formats for different use cases:

```bash
# Table output (default) - human readable
python src/evaluate_profile.py -p system.json

# JSON output - for programmatic integration
python src/evaluate_profile.py -p system.json -f json

# Markdown output - for documentation
python src/evaluate_profile.py -p system.json -f markdown -o report.md
```

### Batch Evaluation

Evaluate multiple systems at once:

```bash
# Evaluate all JSON profiles in a directory
python src/evaluate_profile.py --batch ./profiles/
```

### Severity Filtering

Focus on what matters most:

```bash
# Only show high-severity controls
python src/evaluate_profile.py --severity high

# Only show failed controls
python src/evaluate_profile.py --failed-only

# Combine filters
python src/evaluate_profile.py --severity high --failed-only
```

## What You Get

### 1. Control Catalog (`controls/controls.yaml`)

15 governance controls covering:
- System accountability & ownership
- Data governance & provenance
- Model documentation & change control
- Bias testing & fairness evaluation
- Human oversight mechanisms
- Incident response & monitoring

Each control includes:
- Unique ID and requirement statement
- Evidence path for automated checking
- Severity rating (low/medium/high/critical)
- NIST AI RMF mapping
- EU AI Act article reference

### 2. Automated Evaluator (`src/evaluate_profile.py`)

Pass a system profile JSON → get a compliance report:

```
================================================================================
AI GOVERNANCE CONTROL EVALUATION REPORT
================================================================================
System: Acme Risk Triage
Evaluated: 2024-12-25 10:30:00
Controls Evaluated: 15
================================================================================

| ID | Control | Severity | Result |
|------|---------|----------|--------|
| GOV-01 | System owner assigned | high | PASS |
| GOV-06 | Vendor due diligence | medium | FAIL |
| GOV-13 | Bias and fairness testing | high | PASS |
```

**New: Remediation Guidance**

Failed controls now include specific remediation steps:

```
### GOV-06: Vendor due diligence
- **Severity:** medium
- **Requirement:** Vendors have documented security + privacy review.

**Remediation Steps:**
  1. Create vendor assessment questionnaire covering security and AI ethics
  2. Review vendor's SOC 2, ISO 27001, or equivalent certifications
  3. Document data processing agreements and liability terms
  4. Conduct annual vendor risk reassessment

**Required Artifacts:** Vendor assessment template, Security questionnaire responses, DPA agreements
```

### 3. EU AI Act Risk Classifier (`src/risk_tier.py`)

Classifies systems into risk tiers (Unacceptable → High → Limited → Minimal) based on use case indicators, with compliance gap analysis for high-risk systems.

```bash
# Get risk classification
python src/risk_tier.py -p my_system.json

# Output as JSON
python src/risk_tier.py -p my_system.json -f json
```

### 4. Profile Template Generator

Bootstrap new system profiles quickly:

```bash
# Generate a template
python src/main.py init -o new_system.json

# With field guide
python src/main.py init -o new_system.json --verbose
```

### 5. Framework Mapping (`controls/nist_ai_rmf_mapping.md`)

Shows how each control maps to:
- NIST AI RMF functions (GOVERN, MAP, MEASURE, MANAGE)
- EU AI Act articles

## CLI Reference

### evaluate_profile.py

```
usage: evaluate_profile.py [-h] [-p PROFILE] [-c CONTROLS] [-o OUTPUT]
                          [-f {table,markdown,json}]
                          [--severity {low,medium,high,critical}]
                          [--failed-only] [--batch DIR] [-q]

Options:
  -p, --profile PATH    Path to system profile JSON
  -c, --controls PATH   Path to controls YAML
  -o, --output PATH     Output file path
  -f, --format FORMAT   Output format: table, markdown, json
  --severity LEVEL      Filter by minimum severity
  --failed-only         Only show failed controls
  --batch DIR           Evaluate all JSON profiles in directory
  -q, --quiet           Suppress console output
```

### validate_controls.py

```
usage: validate_controls.py [-h] [-c CONTROLS] [-f {table,json}] [-q] [--strict]

Options:
  -c, --controls PATH   Path to controls YAML
  -f, --format FORMAT   Output format: table, json
  -q, --quiet           Only output errors
  --strict              Treat warnings as errors
```

### risk_tier.py

```
usage: risk_tier.py [-h] [-p PROFILE] [-f {table,json}] [-o OUTPUT] [-q]

Options:
  -p, --profile PATH    Path to system profile JSON
  -f, --format FORMAT   Output format: table, json
  -o, --output PATH     Output file path
  -q, --quiet           Minimal output
```

## Integration Examples

### CI/CD Pipeline

```yaml
# .github/workflows/compliance.yml
name: AI Governance Check
on: [push]
jobs:
  compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install pyyaml
      - name: Validate controls
        run: python src/validate_controls.py --strict
      - name: Evaluate compliance
        run: python src/evaluate_profile.py -p system_profile.json -f json -o report.json
      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: compliance-report
          path: report.json
```

### JSON Integration

```python
import subprocess
import json

# Run evaluation and capture JSON output
result = subprocess.run(
    ["python", "src/evaluate_profile.py", "-p", "my_system.json", "-f", "json"],
    capture_output=True,
    text=True
)

report = json.loads(result.stdout)

# Check if compliant
if report["summary"]["pass_rate"] >= 80:
    print("System meets compliance threshold")
else:
    print(f"Compliance gaps found: {report['summary']['failed']} controls failed")
    for ctrl in report["failed_controls"]:
        print(f"  - {ctrl['id']}: {ctrl['title']}")
```

### Batch Processing

```bash
# Evaluate all systems in a directory
python src/evaluate_profile.py --batch ./profiles/ -f json > batch_results.json
```

## Project Structure

```
ai-governance-controls/
├── controls/
│   ├── controls.yaml          # Control catalog (15 controls)
│   └── nist_ai_rmf_mapping.md # Framework crosswalk
├── src/
│   ├── main.py                # Unified CLI entry point
│   ├── validate_controls.py   # Schema validator
│   ├── evaluate_profile.py    # Compliance evaluator
│   ├── risk_tier.py           # EU AI Act classifier
│   └── sample_system_profile.json
├── examples/
│   └── report.md              # Sample evaluation output
├── README.md
└── LICENSE
```

## Extending the Catalog

Add new controls to `controls.yaml`:

```yaml
- id: GOV-16
  title: Explainability documentation
  requirement: High-stakes decisions include explanation of key factors.
  evidence: system_profile.explainability
  severity: high
  nist_ai_rmf: ["MEASURE 2.8", "MANAGE 3.1"]
  eu_ai_act_article: "Art. 13 - Transparency"
```

Then add the corresponding field to your system profile JSON and update the `REMEDIATION_GUIDANCE` dictionary in `evaluate_profile.py` with specific remediation steps.

## Exit Codes

All tools use consistent exit codes for scripting:

| Code | Meaning |
|------|---------|
| 0 | Success / all checks passed |
| 1 | Failures detected (high-severity control failures, validation errors) |
| 2 | Unacceptable risk tier (EU AI Act prohibited use) |

## Next Steps

- [ ] Map to ISO 42001 (AI Management System)
- [ ] GitHub Actions CI for control validation
- [ ] Generate executive-ready PDF reports
- [ ] Add evidence attachment support (links to artifacts)
- [ ] Web dashboard for multi-system tracking

## Live Demo

Use this tool directly in your browser: **https://delschlangen.github.io/ai-governance-controls**

No installation or dependencies required. Simply:
1. Paste your system profile JSON (or load the sample)
2. Click "Evaluate Compliance"
3. View pass/fail results, risk tier classification, and remediation guidance

## Related Frameworks

- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [EU AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)
- [ISO/IEC 42001:2023](https://www.iso.org/standard/81230.html)

## License

MIT License - See [LICENSE](LICENSE)

---

*Built by Del Schlangen | [LinkedIn](https://linkedin.com/in/del-s-759557175/)*
