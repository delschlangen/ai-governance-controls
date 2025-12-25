# NIST AI Risk Management Framework Mapping

This document maps the controls in `controls.yaml` to the NIST AI Risk Management Framework (AI RMF 1.0, January 2023).

## Framework Overview

The NIST AI RMF organizes AI risk management into four core functions:

| Function | Purpose | Key Activities |
|----------|---------|----------------|
| **GOVERN** | Cultivate risk management culture | Policies, roles, accountability, resource allocation |
| **MAP** | Understand AI system context | Use cases, stakeholders, technical specs, data requirements |
| **MEASURE** | Analyze and assess AI risks | Testing, metrics, bias detection, performance monitoring |
| **MANAGE** | Prioritize and act on risks | Mitigation, incident response, continuous improvement |

---

## Control-to-Framework Mapping

### GOVERN Function

| Control ID | Control Title | GOVERN Categories |
|------------|---------------|-------------------|
| GOV-01 | System owner assigned | GOVERN 1.1, GOVERN 1.2 |
| GOV-04 | Model change control | GOVERN 1.4 |
| GOV-06 | Vendor due diligence | GOVERN 6.1 |
| GOV-07 | Access control | GOVERN 1.5 |
| GOV-08 | Data retention defined | GOVERN 1.6 |
| GOV-14 | Human oversight mechanism | GOVERN 1.3 |

### MAP Function

| Control ID | Control Title | MAP Categories |
|------------|---------------|----------------|
| GOV-02 | Data inventory exists | MAP 1.1, MAP 1.5 |
| GOV-06 | Vendor due diligence | MAP 3.4 |
| GOV-08 | Data retention defined | MAP 1.5 |
| GOV-10 | User-facing transparency | MAP 1.6 |
| GOV-11 | Model documentation | MAP 1.1, MAP 1.3 |
| GOV-12 | Training data provenance | MAP 1.5 |

### MEASURE Function

| Control ID | Control Title | MEASURE Categories |
|------------|---------------|-------------------|
| GOV-03 | Logging enabled | MEASURE 2.3 |
| GOV-09 | Monitoring & alerting | MEASURE 2.3 |
| GOV-11 | Model documentation | MEASURE 2.1 |
| GOV-12 | Training data provenance | MEASURE 2.6 |
| GOV-13 | Bias and fairness testing | MEASURE 2.10, MEASURE 2.11 |
| GOV-15 | Output monitoring | MEASURE 2.3 |

### MANAGE Function

| Control ID | Control Title | MANAGE Categories |
|------------|---------------|-------------------|
| GOV-03 | Logging enabled | MANAGE 2.2 |
| GOV-04 | Model change control | MANAGE 1.3 |
| GOV-05 | Incident response playbook | MANAGE 4.1, MANAGE 4.2 |
| GOV-07 | Access control | MANAGE 2.4 |
| GOV-09 | Monitoring & alerting | MANAGE 2.2 |
| GOV-10 | User-facing transparency | MANAGE 3.1 |
| GOV-14 | Human oversight mechanism | MANAGE 2.1 |
| GOV-15 | Output monitoring | MANAGE 2.2 |

---

## Coverage Analysis

```
GOVERN: 6 controls (40%)
MAP:    6 controls (40%)
MEASURE: 6 controls (40%)
MANAGE: 8 controls (53%)
```

### Gaps Identified (Future Controls)

The following NIST AI RMF areas are not currently covered:

| Gap Area | NIST Reference | Recommended Control |
|----------|----------------|---------------------|
| Third-party AI component inventory | MAP 3.4 | Track embedded AI in dependencies |
| Explainability requirements | MEASURE 2.8 | Define interpretability needs by use case |
| Decommissioning procedures | MANAGE 4.3 | Secure model retirement process |
| Stakeholder feedback loops | GOVERN 5.1 | External input mechanisms |

---

## EU AI Act Cross-Reference

Controls also map to EU AI Act requirements (see `controls.yaml` for article references):

| EU AI Act Article | Controls Addressing |
|-------------------|---------------------|
| Art. 9 - Risk management | GOV-04, GOV-07, GOV-09, GOV-15 |
| Art. 10 - Data governance | GOV-02, GOV-08, GOV-12 |
| Art. 11 - Technical documentation | GOV-11 |
| Art. 12 - Record-keeping | GOV-03 |
| Art. 13 - Transparency | GOV-10 |
| Art. 14 - Human oversight | GOV-14 |
| Art. 16 - Provider obligations | GOV-01 |
| Art. 62 - Incident reporting | GOV-05 |

---

## References

- [NIST AI RMF 1.0](https://www.nist.gov/itl/ai-risk-management-framework)
- [NIST AI RMF Playbook](https://airc.nist.gov/AI_RMF_Knowledge_Base/Playbook)
- [EU AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)
