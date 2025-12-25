#!/usr/bin/env python3
"""
evaluate_profile.py

Evaluates a system profile against the control catalog.
Outputs a pass/fail report for each control with severity-weighted scoring.

Usage:
    python evaluate_profile.py [OPTIONS]

Options:
    -p, --profile PATH    Path to system profile JSON (default: sample_system_profile.json)
    -c, --controls PATH   Path to controls YAML (default: controls/controls.yaml)
    -o, --output PATH     Output file path (optional, prints to stdout if not specified)
    -f, --format FORMAT   Output format: table, markdown, json (default: table)
    --severity LEVEL      Filter by minimum severity: low, medium, high, critical
    --failed-only         Only show failed controls
    --batch DIR           Evaluate all JSON profiles in directory
    -q, --quiet           Suppress console output (useful with --output)
"""

import argparse
import json
import yaml
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional
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


def severity_to_level(severity: str) -> int:
    """Convert severity to numeric level for filtering."""
    levels = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    return levels.get(severity.lower(), 0)


# Remediation guidance for each control - specific actionable steps
REMEDIATION_GUIDANCE = {
    "GOV-01": {
        "steps": [
            "Identify a senior stakeholder accountable for system outcomes",
            "Document the owner's name, role, and contact information",
            "Ensure owner has authority to make decisions about the system",
            "Add owner field to system profile JSON"
        ],
        "artifacts": ["RACI matrix", "System ownership charter", "Org chart excerpt"]
    },
    "GOV-02": {
        "steps": [
            "Catalog all data sources ingested by the system",
            "Document data types, schemas, and sensitivity classifications",
            "Map data flows from source to model to output",
            "Create a data dictionary with field-level descriptions"
        ],
        "artifacts": ["Data inventory spreadsheet", "Data flow diagram", "Data dictionary"]
    },
    "GOV-03": {
        "steps": [
            "Enable logging for authentication, authorization, and model inference",
            "Set log retention period per compliance requirements (min 90 days)",
            "Ensure logs include timestamp, user ID, action, and outcome",
            "Configure log forwarding to centralized SIEM"
        ],
        "artifacts": ["Logging configuration", "Retention policy document", "SIEM integration docs"]
    },
    "GOV-04": {
        "steps": [
            "Establish a change control board or approval process",
            "Require peer review for all model updates",
            "Document rollback procedures",
            "Maintain version history with change rationale"
        ],
        "artifacts": ["Change control procedure", "Approval workflow", "Version control logs"]
    },
    "GOV-05": {
        "steps": [
            "Create incident response playbook specific to AI failures",
            "Define escalation paths and on-call responsibilities",
            "Include model rollback and fallback procedures",
            "Conduct tabletop exercises annually"
        ],
        "artifacts": ["IR playbook document", "Escalation matrix", "Tabletop exercise reports"]
    },
    "GOV-06": {
        "steps": [
            "Create vendor assessment questionnaire covering security and AI ethics",
            "Review vendor's SOC 2, ISO 27001, or equivalent certifications",
            "Document data processing agreements and liability terms",
            "Conduct annual vendor risk reassessment"
        ],
        "artifacts": ["Vendor assessment template", "Security questionnaire responses", "DPA agreements"]
    },
    "GOV-07": {
        "steps": [
            "Implement role-based access control (RBAC)",
            "Apply least privilege principle to admin functions",
            "Enable multi-factor authentication for privileged access",
            "Conduct quarterly access reviews"
        ],
        "artifacts": ["RBAC policy", "Access matrix", "Quarterly access review logs"]
    },
    "GOV-08": {
        "steps": [
            "Define retention periods for each data category",
            "Implement automated data deletion or archival",
            "Document legal and regulatory retention requirements",
            "Create data retention schedule"
        ],
        "artifacts": ["Retention policy", "Retention schedule", "Deletion audit logs"]
    },
    "GOV-09": {
        "steps": [
            "Set up monitoring for model performance drift",
            "Configure alerts for anomalous input patterns",
            "Create dashboard for key model metrics",
            "Define alert thresholds and escalation procedures"
        ],
        "artifacts": ["Monitoring dashboard", "Alert configuration", "Runbook for alerts"]
    },
    "GOV-10": {
        "steps": [
            "Create user-facing documentation explaining AI involvement",
            "Document system limitations and failure modes",
            "Provide clear feedback mechanisms for users",
            "Include AI disclosure in terms of service"
        ],
        "artifacts": ["User documentation", "Limitations disclosure", "ToS AI addendum"]
    },
    "GOV-11": {
        "steps": [
            "Create model card documenting intended use and limitations",
            "Document training data characteristics and known biases",
            "Include performance metrics across relevant subgroups",
            "Update documentation with each model version"
        ],
        "artifacts": ["Model card", "Performance reports", "Limitation documentation"]
    },
    "GOV-12": {
        "steps": [
            "Document all training data sources with URLs/references",
            "Record licensing terms for each dataset",
            "Document consent status for personal data",
            "Maintain data lineage from source to model"
        ],
        "artifacts": ["Data provenance log", "License inventory", "Consent records"]
    },
    "GOV-13": {
        "steps": [
            "Define relevant protected groups for fairness evaluation",
            "Run disaggregated performance analysis across groups",
            "Set acceptable disparity thresholds",
            "Document mitigation steps for identified biases"
        ],
        "artifacts": ["Fairness evaluation report", "Bias mitigation plan", "Disaggregated metrics"]
    },
    "GOV-14": {
        "steps": [
            "Define which decisions require human review",
            "Create workflow for human-in-the-loop review",
            "Set criteria for escalation to human decision-maker",
            "Document override procedures and logging"
        ],
        "artifacts": ["Human oversight policy", "Review workflow", "Override logs"]
    },
    "GOV-15": {
        "steps": [
            "Implement output sampling and review process",
            "Create taxonomy of harmful or off-policy outputs",
            "Set up automated content filters where applicable",
            "Conduct periodic manual output audits"
        ],
        "artifacts": ["Output review policy", "Sampling methodology", "Audit reports"]
    }
}


def evaluate_controls(
    controls: List[Dict],
    profile: Dict,
    min_severity: Optional[str] = None,
    failed_only: bool = False
) -> List[Dict]:
    """
    Evaluate each control against the system profile.

    Args:
        controls: List of control definitions
        profile: System profile to evaluate
        min_severity: Filter to only include controls at or above this severity
        failed_only: Only include failed controls in results

    Returns list of results with pass/fail status and details.
    """
    results = []
    min_level = severity_to_level(min_severity) if min_severity else 0

    for control in controls:
        # Filter by severity if specified
        if min_severity and severity_to_level(control["severity"]) < min_level:
            continue

        # Extract evidence path (remove "system_profile." prefix)
        evidence_path = control["evidence"].replace("system_profile.", "")

        # Get the evidence value from profile
        evidence_value = get_path(profile, evidence_path)

        # Evaluate
        passed = truthy(evidence_value)

        # Skip if we only want failed and this passed
        if failed_only and passed:
            continue

        # Get remediation guidance
        guidance = REMEDIATION_GUIDANCE.get(control["id"], {})

        results.append({
            "id": control["id"],
            "title": control["title"],
            "requirement": control.get("requirement", ""),
            "severity": control["severity"],
            "weight": severity_to_weight(control["severity"]),
            "passed": passed,
            "evidence_path": evidence_path,
            "evidence_value": evidence_value,
            "nist_mapping": control.get("nist_ai_rmf", []),
            "eu_article": control.get("eu_ai_act_article", ""),
            "remediation_steps": guidance.get("steps", []),
            "required_artifacts": guidance.get("artifacts", [])
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
            print(f"- **Requirement:** {r.get('requirement', 'N/A')}")
            print(f"- **Evidence Path:** `{r['evidence_path']}`")
            print(f"- **Current Value:** `{r['evidence_value']}`")
            if r["nist_mapping"]:
                print(f"- **NIST AI RMF:** {', '.join(r['nist_mapping'])}")
            if r["eu_article"]:
                print(f"- **EU AI Act:** {r['eu_article']}")
            # Show remediation steps
            if r.get("remediation_steps"):
                print("\n**Remediation Steps:**")
                for i, step in enumerate(r["remediation_steps"], 1):
                    print(f"  {i}. {step}")
            if r.get("required_artifacts"):
                print(f"\n**Required Artifacts:** {', '.join(r['required_artifacts'])}")
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
            lines.append(f"- **Requirement:** {r.get('requirement', 'N/A')}")
            lines.append(f"- **Evidence Path:** `{r['evidence_path']}`")
            lines.append(f"- **Current Value:** `{r['evidence_value']}`")
            if r["nist_mapping"]:
                lines.append(f"- **NIST AI RMF:** {', '.join(r['nist_mapping'])}")
            if r["eu_article"]:
                lines.append(f"- **EU AI Act:** {r['eu_article']}")
            # Add remediation steps
            if r.get("remediation_steps"):
                lines.append("\n**Remediation Steps:**")
                for i, step in enumerate(r["remediation_steps"], 1):
                    lines.append(f"{i}. {step}")
            if r.get("required_artifacts"):
                lines.append(f"\n**Required Artifacts:** {', '.join(r['required_artifacts'])}")
            lines.append("")
    else:
        lines.append("\n## All Controls Passed\n")
        lines.append("No remediation required.\n")

    return "\n".join(lines)


def generate_json_report(results: List[Dict], scores: Dict, profile: Dict) -> str:
    """Generate a JSON report for programmatic use."""
    report = {
        "metadata": {
            "system_name": profile.get("system_name", "Unknown"),
            "system_description": profile.get("system_description", ""),
            "evaluated_at": datetime.now().isoformat(),
            "controls_evaluated": scores["total"]
        },
        "summary": {
            "pass_rate": scores["pass_rate"],
            "weighted_score": scores["weighted_score"],
            "total_controls": scores["total"],
            "passed": scores["passed"],
            "failed": scores["failed"],
            "by_severity": scores["by_severity"]
        },
        "controls": [
            {
                "id": r["id"],
                "title": r["title"],
                "requirement": r.get("requirement", ""),
                "severity": r["severity"],
                "passed": r["passed"],
                "evidence_path": r["evidence_path"],
                "evidence_value": r["evidence_value"],
                "nist_mapping": r["nist_mapping"],
                "eu_article": r["eu_article"],
                "remediation": {
                    "steps": r.get("remediation_steps", []),
                    "artifacts": r.get("required_artifacts", [])
                } if not r["passed"] else None
            }
            for r in results
        ],
        "failed_controls": [
            {
                "id": r["id"],
                "title": r["title"],
                "severity": r["severity"],
                "remediation_steps": r.get("remediation_steps", []),
                "required_artifacts": r.get("required_artifacts", [])
            }
            for r in results if not r["passed"]
        ]
    }
    return json.dumps(report, indent=2, default=str)


def evaluate_single_profile(
    profile_path: Path,
    controls: List[Dict],
    output_format: str,
    output_path: Optional[Path],
    min_severity: Optional[str],
    failed_only: bool,
    quiet: bool
) -> Tuple[Dict, int]:
    """Evaluate a single profile and return results."""
    with open(profile_path) as f:
        profile = json.load(f)

    results = evaluate_controls(controls, profile, min_severity, failed_only)
    scores = calculate_scores(results)

    # Generate output
    if output_format == "json":
        output = generate_json_report(results, scores, profile)
    elif output_format == "markdown":
        output = generate_markdown_report(results, scores, profile)
    else:
        output = None

    # Print or save
    if not quiet:
        if output_format in ("json", "markdown"):
            print(output)
        else:
            print_report(results, scores, profile)

    if output_path:
        if output_format == "json":
            content = generate_json_report(results, scores, profile)
        elif output_format == "markdown":
            content = generate_markdown_report(results, scores, profile)
        else:
            content = generate_markdown_report(results, scores, profile)

        with open(output_path, "w") as f:
            f.write(content)
        if not quiet:
            print(f"\nReport saved to: {output_path}")

    high_failures = scores["by_severity"].get("high", {}).get("failed", 0)
    return scores, 1 if high_failures > 0 else 0


def evaluate_batch(
    batch_dir: Path,
    controls: List[Dict],
    output_format: str,
    min_severity: Optional[str],
    failed_only: bool,
    quiet: bool
) -> int:
    """Evaluate all JSON profiles in a directory."""
    profiles = list(batch_dir.glob("*.json"))

    if not profiles:
        print(f"No JSON profiles found in {batch_dir}")
        return 1

    print(f"Found {len(profiles)} profiles to evaluate\n")
    print("=" * 80)

    all_results = []
    exit_code = 0

    for profile_path in profiles:
        if not quiet:
            print(f"\nEvaluating: {profile_path.name}")
            print("-" * 40)

        try:
            with open(profile_path) as f:
                profile = json.load(f)

            results = evaluate_controls(controls, profile, min_severity, failed_only)
            scores = calculate_scores(results)

            all_results.append({
                "profile": profile_path.name,
                "system_name": profile.get("system_name", "Unknown"),
                "pass_rate": scores["pass_rate"],
                "weighted_score": scores["weighted_score"],
                "passed": scores["passed"],
                "failed": scores["failed"],
                "high_failures": scores["by_severity"].get("high", {}).get("failed", 0)
            })

            if not quiet:
                print(f"  Pass Rate: {scores['pass_rate']}%")
                print(f"  Weighted Score: {scores['weighted_score']}%")
                print(f"  Failed: {scores['failed']}")

            if scores["by_severity"].get("high", {}).get("failed", 0) > 0:
                exit_code = 1

        except Exception as e:
            print(f"  ERROR: {e}")
            exit_code = 1

    # Print summary
    print("\n" + "=" * 80)
    print("BATCH EVALUATION SUMMARY")
    print("=" * 80)
    print(f"\n| Profile | System | Pass Rate | Weighted | High Failures |")
    print("|---------|--------|-----------|----------|---------------|")
    for r in all_results:
        print(f"| {r['profile'][:20]} | {r['system_name'][:15]} | {r['pass_rate']}% | {r['weighted_score']}% | {r['high_failures']} |")

    if output_format == "json":
        print("\n" + json.dumps({"batch_results": all_results}, indent=2))

    return exit_code


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Evaluate AI system profiles against governance controls",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate default sample profile
  python evaluate_profile.py

  # Evaluate a specific profile
  python evaluate_profile.py -p my_system.json

  # Output as JSON for integration
  python evaluate_profile.py -p my_system.json -f json

  # Save markdown report
  python evaluate_profile.py -p my_system.json -o report.md -f markdown

  # Only show high-severity failures
  python evaluate_profile.py --severity high --failed-only

  # Batch evaluate all profiles in a directory
  python evaluate_profile.py --batch ./profiles/
"""
    )

    parser.add_argument(
        "-p", "--profile",
        type=Path,
        help="Path to system profile JSON (default: sample_system_profile.json)"
    )
    parser.add_argument(
        "-c", "--controls",
        type=Path,
        help="Path to controls YAML (default: controls/controls.yaml)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file path (optional)"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["table", "markdown", "json"],
        default="table",
        help="Output format (default: table)"
    )
    parser.add_argument(
        "--severity",
        choices=["low", "medium", "high", "critical"],
        help="Filter by minimum severity level"
    )
    parser.add_argument(
        "--failed-only",
        action="store_true",
        help="Only show failed controls"
    )
    parser.add_argument(
        "--batch",
        type=Path,
        help="Directory containing JSON profiles for batch evaluation"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress console output (useful with --output)"
    )

    return parser.parse_args()


def main():
    args = parse_args()
    script_dir = Path(__file__).parent

    # Determine controls path
    if args.controls:
        controls_path = args.controls
    else:
        controls_path = script_dir.parent / "controls" / "controls.yaml"

    if not controls_path.exists():
        print(f"ERROR: Controls file not found at {controls_path}")
        sys.exit(1)

    with open(controls_path) as f:
        controls_data = yaml.safe_load(f)
    controls = controls_data.get("controls", [])

    # Batch mode
    if args.batch:
        if not args.batch.exists() or not args.batch.is_dir():
            print(f"ERROR: Batch directory not found: {args.batch}")
            sys.exit(1)

        exit_code = evaluate_batch(
            args.batch,
            controls,
            args.format,
            args.severity,
            args.failed_only,
            args.quiet
        )
        sys.exit(exit_code)

    # Single profile mode
    if args.profile:
        profile_path = args.profile
    else:
        profile_path = script_dir / "sample_system_profile.json"

    if not profile_path.exists():
        print(f"ERROR: Profile not found at {profile_path}")
        sys.exit(1)

    scores, exit_code = evaluate_single_profile(
        profile_path,
        controls,
        args.format,
        args.output,
        args.severity,
        args.failed_only,
        args.quiet
    )

    if exit_code > 0 and not args.quiet:
        high_failures = scores["by_severity"].get("high", {}).get("failed", 0)
        print(f"\nWARNING: {high_failures} high-severity control(s) failed")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
