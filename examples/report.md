# AI Governance Control Evaluation Report

**System:** Acme Risk Triage

**Evaluated:** 2025-12-25 03:10:36

**Controls Evaluated:** 15


## Executive Summary

| Metric | Value |
|--------|-------|
| Overall Pass Rate | 93.3% |
| Weighted Score | 94.7% |
| Controls Passed | 14/15 |
| High-Severity Failures | 0 |

## Control Results

| ID | Control | Severity | Result |
|------|---------|----------|--------|
| GOV-01 | System owner assigned | high | ✅ PASS |
| GOV-02 | Data inventory exists | high | ✅ PASS |
| GOV-03 | Logging enabled | medium | ✅ PASS |
| GOV-04 | Model change control | high | ✅ PASS |
| GOV-05 | Incident response playbook | high | ✅ PASS |
| GOV-06 | Vendor due diligence | medium | ❌ FAIL |
| GOV-07 | Access control | high | ✅ PASS |
| GOV-08 | Data retention defined | medium | ✅ PASS |
| GOV-09 | Monitoring & alerting | medium | ✅ PASS |
| GOV-10 | User-facing transparency | low | ✅ PASS |
| GOV-11 | Model documentation | high | ✅ PASS |
| GOV-12 | Training data provenance | high | ✅ PASS |
| GOV-13 | Bias and fairness testing | high | ✅ PASS |
| GOV-14 | Human oversight mechanism | high | ✅ PASS |
| GOV-15 | Output monitoring | medium | ✅ PASS |

## Results by Severity

| Severity | Passed | Failed | Rate |
|----------|--------|--------|------|
| high | 9 | 0 | 100.0% |
| medium | 4 | 1 | 80.0% |
| low | 1 | 0 | 100.0% |

## Failed Controls - Remediation Required

### GOV-06: Vendor due diligence

- **Severity:** medium
- **Evidence Path:** `vendor_review`
- **Current Value:** `{'exists': False}`
- **NIST AI RMF:** GOVERN 6.1, MAP 3.4
- **EU AI Act:** Art. 25 - Responsibilities along the AI value chain
