#!/usr/bin/env python3
"""
evaluate_profile.py

Evaluates a system profile against the control catalog.
Outputs a pass/fail report for each control with severity-weighted scoring.
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple
from datetime import datetime


def truthy(val: Any) -> bool:
    """
    Determine if a value indicates control compliance.
    
    Handles various evidence formats:
    - Boolean: direct pass/fail
    - Dict with 'exists' key: check exists flag
    - Dict with 'enabled' key: check enabled flag  
    - Dict with 'conducted' key: check conducted flag
    - Non-empty lists/strings: pass
    - None or empty: fail
    """
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, dict):
        # Check common boolean indicators in dicts
        if "exists" in val:
            return bool(val["exists"])
        if "enabled" in val:
            return bool(val["enabled"])
        if "conducted" in val:
            return bool(val["conducted"])
        if "documented" in val:
            return bool(val["documented"])
        # Non-empty dict with data is truthy
        return len(val) > 0
    if isinstance(val, (list, str)):
        return len(val) > 0
    if isinstance(val, (int, float)):
        return True
    return bool(val)


def get_path(obj: Dict, path: str) -> Any:
    """
    Navigate a nested dict using dot notation.
    
    Example: get_path(obj, "logging.enabled") returns obj["logging"]["enabled"]
    """
    current = obj
    for part in path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def severity_to_weight(severity: str) -> int:
    """Convert severity to numeric weight for scoring."""
    weights = {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "low": 1
    }
    return weights.get(severity.lower(), 1)


def evaluate_controls(controls: List[Dict], profile: Dict) -> List[Dict]:
    """
    Evaluate each control against the system profile.
    
    Returns list of results with pass/fail status and details.
    """
    results = []
    
    for control in controls:
        # Extract evidence path (remove "system_profile." prefix)
        evidence_path = control["evidence"].replace("system_profile.", "")
        
        # Get the evidence value from profile
        evidence_value = get_path(profile, evidence_path)
        
        # Evaluate
        passed = truthy(evidence_value)
        
        results.append({
            "id": control["id"],
            "title": control["title"],
            "severity": control["severity"],
            "weight": severity_to_weight(control["severity"]),
            "passed": passed,
            "evidence_path": evidence_path,
            "evidence_value": evidence_value,
            "nist_mapping": control.get("nist_ai_rmf", []),
            "eu_article": control.get("eu_ai_act_article", "")
        })
    
    return results


def calculate_scores(results: List[Dict]) -> Dict:
    """Calculate overall and severity-weighted scores."""
    total_controls = len(results)
    passed_controls = sum(1 for r in results if r["passed"])
    
    # Weighted scoring
    total_weight = sum(r["weight"] for r in results)
    earned_weight = sum(r["weight"] for r in results if r["passed"])
    
    # By severity
    by_severity = {}
    for sev in ["high", "medium", "low"]:
        sev_results = [r for r in results if r["severity"] == sev]
        if sev_results:
            by_severity[sev] = {
                "total": len(sev_results),
                "passed": sum(1 for r in sev_results if r["passed"]),
                "failed": sum(1 for r in sev_results if not r["passed"])
            }
    
    return {
        "total": total_controls,
        "passed": passed_controls,
        "failed": total_controls - passed_controls,
        "pass_rate": round(passed_controls / total_controls * 100, 1) if total_controls > 0 else 0,
        "weighted_score": round(earned_weight / total_weight * 100, 1) if total_weight > 0 else 0,
        "by_severity": by_severity
    }


def print_report(results: List[Dict], scores: Dict, profile: Dict, output_format: str = "table"):
    """Print the evaluation report."""
    
    print("=" * 80)
    print("AI GOVERNANCE CONTROL EVALUATION REPORT")
    print("=" * 80)
    print(f"System: {profile.get('system_name', 'Unknown')}")
    print(f"Evaluated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Controls Evaluated: {scores['total']}")
    print("=" * 80)
    
    # Results table
    print("\n## Control Results\n")
    print("| ID | Control | Severity | Result |")
    print("|------|---------|----------|--------|")
    
    for r in results:
        status = "✅ PASS" if r["passed"] else "❌ FAIL"
        print(f"| {r['id']} | {r['title']} | {r['severity']} | {status} |")
    
    # Summary
    print("\n" + "=" * 80)
    print("## Summary\n")
    print(f"**Overall Pass Rate:** {scores['pass_rate']}% ({scores['passed']}/{scores['total']})")
    print(f"**Weighted Score:** {scores['weighted_score']}%")
    print(f"  _(High-severity controls weighted 3x, medium 2x, low 1x)_\n")
    
    print("### By Severity\n")
    print("| Severity | Passed | Failed | Rate |")
    print("|----------|--------|--------|------|")
    for sev in ["high", "medium", "low"]:
        if sev in scores["by_severity"]:
            s = scores["by_severity"][sev]
            rate = round(s["passed"] / s["total"] * 100, 1) if s["total"] > 0 else 0
            print(f"| {sev} | {s['passed']} | {s['failed']} | {rate}% |")
    
    # Failed controls detail
    failed = [r for r in results if not r["passed"]]
    if failed:
        print("\n" + "=" * 80)
        print("## Failed Controls - Remediation Required\n")
        for r in failed:
            print(f"### {r['id']}: {r['title']}")
            print(f"- **Severity:** {r['severity']}")
            print(f"- **Evidence Path:** `{r['evidence_path']}`")
            print(f"- **Current Value:** `{r['evidence_value']}`")
            if r["nist_mapping"]:
                print(f"- **NIST AI RMF:** {', '.join(r['nist_mapping'])}")
            if r["eu_article"]:
                print(f"- **EU AI Act:** {r['eu_article']}")
            print()


def generate_markdown_report(results: List[Dict], scores: Dict, profile: Dict) -> str:
    """Generate a markdown report suitable for saving to file."""
    lines = []
    
    lines.append("# AI Governance Control Evaluation Report\n")
    lines.append(f"**System:** {profile.get('system_name', 'Unknown')}\n")
    lines.append(f"**Evaluated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"**Controls Evaluated:** {scores['total']}\n")
    
    # Summary box
    lines.append("\n## Executive Summary\n")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Overall Pass Rate | {scores['pass_rate']}% |")
    lines.append(f"| Weighted Score | {scores['weighted_score']}% |")
    lines.append(f"| Controls Passed | {scores['passed']}/{scores['total']} |")
    lines.append(f"| High-Severity Failures | {scores['by_severity'].get('high', {}).get('failed', 0)} |")
    
    # Results table
    lines.append("\n## Control Results\n")
    lines.append("| ID | Control | Severity | Result |")
    lines.append("|------|---------|----------|--------|")
    
    for r in results:
        status = "✅ PASS" if r["passed"] else "❌ FAIL"
        lines.append(f"| {r['id']} | {r['title']} | {r['severity']} | {status} |")
    
    # By severity
    lines.append("\n## Results by Severity\n")
    lines.append("| Severity | Passed | Failed | Rate |")
    lines.append("|----------|--------|--------|------|")
    for sev in ["high", "medium", "low"]:
        if sev in scores["by_severity"]:
            s = scores["by_severity"][sev]
            rate = round(s["passed"] / s["total"] * 100, 1) if s["total"] > 0 else 0
            lines.append(f"| {sev} | {s['passed']} | {s['failed']} | {rate}% |")
    
    # Failed controls
    failed = [r for r in results if not r["passed"]]
    if failed:
        lines.append("\n## Failed Controls - Remediation Required\n")
        for r in failed:
            lines.append(f"### {r['id']}: {r['title']}\n")
            lines.append(f"- **Severity:** {r['severity']}")
            lines.append(f"- **Evidence Path:** `{r['evidence_path']}`")
            lines.append(f"- **Current Value:** `{r['evidence_value']}`")
            if r["nist_mapping"]:
                lines.append(f"- **NIST AI RMF:** {', '.join(r['nist_mapping'])}")
            if r["eu_article"]:
                lines.append(f"- **EU AI Act:** {r['eu_article']}")
            lines.append("")
    else:
        lines.append("\n## ✅ All Controls Passed\n")
        lines.append("No remediation required.\n")
    
    return "\n".join(lines)


def main():
    script_dir = Path(__file__).parent
    
    # Load controls
    controls_path = script_dir.parent / "controls" / "controls.yaml"
    if not controls_path.exists():
        print(f"ERROR: Controls file not found at {controls_path}")
        sys.exit(1)
    
    with open(controls_path) as f:
        controls_data = yaml.safe_load(f)
    controls = controls_data.get("controls", [])
    
    # Load profile
    profile_path = script_dir / "sample_system_profile.json"
    if not profile_path.exists():
        print(f"ERROR: Profile not found at {profile_path}")
        sys.exit(1)
    
    with open(profile_path) as f:
        profile = json.load(f)
    
    # Evaluate
    results = evaluate_controls(controls, profile)
    scores = calculate_scores(results)
    
    # Print to console
    print_report(results, scores, profile)
    
    # Generate markdown report
    report_md = generate_markdown_report(results, scores, profile)
    
    # Save report
    report_path = script_dir.parent / "examples" / "report.md"
    with open(report_path, "w") as f:
        f.write(report_md)
    print(f"\n📄 Report saved to: {report_path}")
    
    # Exit with error if any high-severity controls failed
    high_failures = scores["by_severity"].get("high", {}).get("failed", 0)
    if high_failures > 0:
        print(f"\n⚠️  WARNING: {high_failures} high-severity control(s) failed")
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
