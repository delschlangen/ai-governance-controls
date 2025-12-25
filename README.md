# ai-governance-controls

**Translate AI governance requirements into auditable, testable controls.**

A practical toolkit demonstrating how to operationalize AI governance frameworks (NIST AI RMF, EU AI Act) into machine-readable control catalogs with automated compliance evaluation.

## Why This Exists

Policy documents don't protect anyone—implemented controls do. This repo bridges the gap between governance frameworks sitting in PDFs and operational compliance that can be tested, measured, and reported. Built from experience translating complex risk requirements into actionable product capabilities.

## Quick Start

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/ai-governance-controls.git
cd ai-governance-controls

# Install dependency
pip install pyyaml

# Validate the control catalog
python src/validate_controls.py

# Evaluate a system against controls
python src/evaluate_profile.py

# Classify system under EU AI Act risk tiers
python src/risk_tier.py
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
- Severity rating
- NIST AI RMF mapping
- EU AI Act article reference

### 2. Automated Evaluator (`src/evaluate_profile.py`)
Pass a system profile JSON → get a compliance report:

| ID | Control | Severity | Result |
|------|---------|----------|--------|
| GOV-01 | System owner assigned | high | ✅ PASS |
| GOV-06 | Vendor due diligence | medium | ❌ FAIL |
| GOV-13 | Bias and fairness testing | high | ✅ PASS |

### 3. EU AI Act Risk Classifier (`src/risk_tier.py`)
Classifies systems into risk tiers (Unacceptable → High → Limited → Minimal) based on use case indicators, with compliance gap analysis for high-risk systems.

### 4. Framework Mapping (`controls/nist_ai_rmf_mapping.md`)
Shows how each control maps to:
- NIST AI RMF functions (GOVERN, MAP, MEASURE, MANAGE)
- EU AI Act articles

## Sample Output

```
================================================================================
AI GOVERNANCE CONTROL EVALUATION REPORT
================================================================================
System: Acme Risk Triage
Evaluated: 2024-12-24 10:30:00
Controls Evaluated: 15
================================================================================

## Summary

**Overall Pass Rate:** 93.3% (14/15)
**Weighted Score:** 94.1%

### By Severity

| Severity | Passed | Failed | Rate |
|----------|--------|--------|------|
| high | 8 | 0 | 100% |
| medium | 5 | 1 | 83.3% |
| low | 1 | 0 | 100% |
```

## Project Structure

```
ai-governance-controls/
├── controls/
│   ├── controls.yaml          # Control catalog (15 controls)
│   └── nist_ai_rmf_mapping.md # Framework crosswalk
├── src/
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

Then add the corresponding field to your system profile JSON.

## Next Steps

- [ ] Add scoring weights by control criticality
- [ ] Add evidence attachment support (links to artifacts)
- [ ] Map to ISO 42001 (AI Management System)
- [ ] GitHub Actions CI for control validation
- [ ] Generate executive-ready PDF reports

## Related Frameworks

- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [EU AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)
- [ISO/IEC 42001:2023](https://www.iso.org/standard/81230.html)

## License

MIT License - See [LICENSE](LICENSE)

---

*Built by Del Schlangen | [LinkedIn](https://linkedin.com/in/del-s-759557175/)*
