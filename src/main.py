#!/usr/bin/env python3
"""
AI Governance Controls Toolkit - Unified CLI

A comprehensive toolkit for operationalizing AI governance frameworks
into machine-readable, auditable controls.

Usage:
    python main.py <command> [options]

Commands:
    validate    Validate the controls catalog
    evaluate    Evaluate a system profile against controls
    classify    Classify system under EU AI Act risk tiers
    init        Generate a new system profile template
    report      Generate a full compliance report (evaluate + classify)

Examples:
    python main.py validate
    python main.py evaluate -p my_system.json -f json
    python main.py classify -p my_system.json
    python main.py init -o new_system.json
    python main.py report -p my_system.json -o compliance_report.json
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Import the individual modules
from validate_controls import validate_controls_file
from evaluate_profile import (
    evaluate_controls,
    calculate_scores,
    generate_json_report as generate_eval_json,
    generate_markdown_report,
    print_report,
    REMEDIATION_GUIDANCE
)
from risk_tier import (
    classify_risk_tier,
    evaluate_high_risk_compliance,
    print_classification_report,
    generate_json_report as generate_risk_json
)

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)


def load_controls(controls_path: Path):
    """Load controls from YAML file."""
    with open(controls_path) as f:
        data = yaml.safe_load(f)
    return data.get("controls", [])


def cmd_validate(args):
    """Validate the controls catalog."""
    script_dir = Path(__file__).parent
    controls_path = args.controls or script_dir.parent / "controls" / "controls.yaml"

    if not controls_path.exists():
        print(f"ERROR: Controls file not found at {controls_path}")
        return 1

    result = validate_controls_file(controls_path, args.strict)

    if args.format == "json":
        result["file"] = str(controls_path)
        print(json.dumps(result, indent=2))
    else:
        print(f"Validating: {controls_path}\n")
        print("=" * 60)

        if result["valid"]:
            print(f"All {result['controls_count']} controls passed validation!")
        else:
            for err in result.get("errors", []):
                print(f"  ERROR [{err['control_id']}]: {err['message']}")

        print(f"\nSeverity distribution: {result.get('severity_distribution', {})}")

    return 0 if result["valid"] else 1


def cmd_evaluate(args):
    """Evaluate a system profile against controls."""
    script_dir = Path(__file__).parent
    controls_path = args.controls or script_dir.parent / "controls" / "controls.yaml"
    profile_path = args.profile or script_dir / "sample_system_profile.json"

    if not controls_path.exists():
        print(f"ERROR: Controls file not found at {controls_path}")
        return 1

    if not profile_path.exists():
        print(f"ERROR: Profile not found at {profile_path}")
        return 1

    controls = load_controls(controls_path)

    with open(profile_path) as f:
        profile = json.load(f)

    results = evaluate_controls(controls, profile, args.severity, args.failed_only)
    scores = calculate_scores(results)

    if args.format == "json":
        output = generate_eval_json(results, scores, profile)
        print(output)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
    elif args.format == "markdown":
        output = generate_markdown_report(results, scores, profile)
        print(output)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
    else:
        print_report(results, scores, profile)

    high_failures = scores["by_severity"].get("high", {}).get("failed", 0)
    return 1 if high_failures > 0 else 0


def cmd_classify(args):
    """Classify system under EU AI Act risk tiers."""
    script_dir = Path(__file__).parent
    profile_path = args.profile or script_dir / "sample_system_profile.json"

    if not profile_path.exists():
        print(f"ERROR: Profile not found at {profile_path}")
        return 1

    with open(profile_path) as f:
        profile = json.load(f)

    if args.format == "json":
        output = generate_risk_json(profile)
        print(output)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
    else:
        print_classification_report(profile)

    tier, _, _ = classify_risk_tier(profile)
    if tier == "unacceptable":
        return 2
    elif tier == "high":
        compliance = evaluate_high_risk_compliance(profile)
        if compliance["compliance_rate"] < 100:
            return 1
    return 0


def cmd_init(args):
    """Generate a new system profile template."""
    template = {
        "system_name": "Your System Name",
        "system_description": "Brief description of what the system does",
        "owner": "",
        "data_inventory": [],
        "logging": {
            "enabled": False,
            "retention_days": 0,
            "includes": []
        },
        "change_control": {
            "exists": False,
            "process": ""
        },
        "ir_playbook": {
            "exists": False,
            "last_tested": ""
        },
        "vendor_review": {
            "exists": False,
            "vendors_assessed": []
        },
        "access_control": {
            "rbac": False,
            "mfa_required": False,
            "last_review": ""
        },
        "retention": {
            "defined": False,
            "categories": {}
        },
        "monitoring": {
            "enabled": False,
            "alerts_configured": False,
            "metrics_tracked": []
        },
        "transparency": {
            "user_informed_of_ai": False,
            "limitations_documented": False
        },
        "model_card": {
            "exists": False,
            "url": ""
        },
        "data_provenance": {
            "documented": False,
            "sources": []
        },
        "fairness_eval": {
            "conducted": False,
            "groups_evaluated": [],
            "last_evaluation": ""
        },
        "human_oversight": {
            "exists": False,
            "escalation_path": ""
        },
        "output_monitoring": {
            "enabled": False,
            "sampling_rate": 0
        }
    }

    # Add field descriptions as comments in a separate guide
    field_guide = """
# System Profile Field Guide

## Required for Governance Controls

- system_name: Official name of the AI system
- system_description: What the system does and its primary use case
- owner: Name/role of the accountable system owner

## Data Governance (GOV-02, GOV-08, GOV-12)
- data_inventory: List of data types processed (e.g., ["user_data", "logs"])
- retention: Data retention policies by category
- data_provenance: Training data sources and licensing

## Security & Access (GOV-03, GOV-07)
- logging: Event logging configuration
- access_control: RBAC and authentication settings

## Change Management (GOV-04, GOV-05)
- change_control: Model update approval process
- ir_playbook: Incident response procedures

## Vendor Management (GOV-06)
- vendor_review: Third-party vendor assessments

## Monitoring (GOV-09, GOV-15)
- monitoring: Performance and anomaly monitoring
- output_monitoring: Output quality sampling

## Transparency (GOV-10, GOV-11)
- transparency: User disclosure settings
- model_card: Model documentation

## AI-Specific (GOV-13, GOV-14)
- fairness_eval: Bias and fairness testing
- human_oversight: Human review mechanisms
"""

    output_path = args.output or Path("system_profile_template.json")

    with open(output_path, "w") as f:
        json.dump(template, f, indent=2)

    print(f"Generated profile template: {output_path}")
    print("\nNext steps:")
    print("1. Edit the template to reflect your system's actual configuration")
    print("2. Set boolean fields to true where controls are implemented")
    print("3. Fill in lists and details for each control area")
    print("4. Run: python main.py evaluate -p " + str(output_path))

    # Also output field guide if verbose
    if args.verbose:
        print("\n" + "=" * 60)
        print(field_guide)

    return 0


def cmd_report(args):
    """Generate a comprehensive compliance report."""
    script_dir = Path(__file__).parent
    controls_path = args.controls or script_dir.parent / "controls" / "controls.yaml"
    profile_path = args.profile or script_dir / "sample_system_profile.json"

    if not controls_path.exists():
        print(f"ERROR: Controls file not found at {controls_path}")
        return 1

    if not profile_path.exists():
        print(f"ERROR: Profile not found at {profile_path}")
        return 1

    controls = load_controls(controls_path)

    with open(profile_path) as f:
        profile = json.load(f)

    # Run evaluation
    results = evaluate_controls(controls, profile)
    scores = calculate_scores(results)

    # Run classification
    tier, reasons, obligations = classify_risk_tier(profile)
    high_risk_compliance = None
    if tier == "high":
        high_risk_compliance = evaluate_high_risk_compliance(profile)

    # Build comprehensive report
    report = {
        "metadata": {
            "system_name": profile.get("system_name", "Unknown"),
            "system_description": profile.get("system_description", ""),
            "generated_at": datetime.now().isoformat(),
            "controls_version": "1.0"
        },
        "executive_summary": {
            "overall_pass_rate": scores["pass_rate"],
            "weighted_score": scores["weighted_score"],
            "risk_tier": tier,
            "high_severity_failures": scores["by_severity"].get("high", {}).get("failed", 0),
            "total_controls": scores["total"],
            "recommendation": _get_recommendation(scores, tier)
        },
        "control_evaluation": {
            "summary": scores,
            "controls": [
                {
                    "id": r["id"],
                    "title": r["title"],
                    "severity": r["severity"],
                    "passed": r["passed"],
                    "evidence_path": r["evidence_path"],
                    "nist_mapping": r["nist_mapping"],
                    "eu_article": r["eu_article"]
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
        },
        "risk_classification": {
            "tier": tier,
            "reasons": reasons,
            "obligations": obligations,
            "high_risk_compliance": high_risk_compliance
        }
    }

    output = json.dumps(report, indent=2)

    if args.format == "json" or args.output:
        if not args.quiet:
            print(output)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"\nFull report saved to: {args.output}")
    else:
        # Print summary
        print("=" * 70)
        print("COMPREHENSIVE AI GOVERNANCE COMPLIANCE REPORT")
        print("=" * 70)
        print(f"System: {profile.get('system_name', 'Unknown')}")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        print("\n## Executive Summary\n")
        print(f"- **Overall Pass Rate:** {scores['pass_rate']}%")
        print(f"- **Weighted Score:** {scores['weighted_score']}%")
        print(f"- **EU AI Act Risk Tier:** {tier.upper()}")
        print(f"- **High-Severity Failures:** {scores['by_severity'].get('high', {}).get('failed', 0)}")
        print(f"\n**Recommendation:** {_get_recommendation(scores, tier)}")

        # Control summary
        print("\n## Control Evaluation\n")
        print_report(results, scores, profile)

        # Risk classification
        print("\n")
        print_classification_report(profile)

    # Determine exit code
    high_failures = scores["by_severity"].get("high", {}).get("failed", 0)
    if tier == "unacceptable":
        return 2
    elif high_failures > 0:
        return 1
    return 0


def _get_recommendation(scores: dict, tier: str) -> str:
    """Generate a recommendation based on scores and tier."""
    high_failures = scores["by_severity"].get("high", {}).get("failed", 0)

    if tier == "unacceptable":
        return "CRITICAL: System uses prohibited AI practices. Deployment not permitted under EU AI Act."
    elif high_failures > 0:
        return f"Address {high_failures} high-severity control failure(s) before production deployment."
    elif scores["pass_rate"] < 80:
        return "Improve control coverage to meet minimum compliance threshold of 80%."
    elif tier == "high":
        return "High-risk system - ensure ongoing compliance monitoring and annual reassessment."
    else:
        return "System meets baseline governance requirements. Continue periodic reviews."


def main():
    parser = argparse.ArgumentParser(
        description="AI Governance Controls Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  validate   Validate the controls catalog for schema errors
  evaluate   Evaluate a system profile against governance controls
  classify   Classify system under EU AI Act risk tiers
  init       Generate a new system profile template
  report     Generate comprehensive compliance report

Examples:
  %(prog)s validate
  %(prog)s evaluate -p my_system.json
  %(prog)s classify -p my_system.json -f json
  %(prog)s init -o new_system.json
  %(prog)s report -p my_system.json -o report.json
"""
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Validate command
    p_validate = subparsers.add_parser("validate", help="Validate controls catalog")
    p_validate.add_argument("-c", "--controls", type=Path, help="Controls YAML path")
    p_validate.add_argument("-f", "--format", choices=["table", "json"], default="table")
    p_validate.add_argument("--strict", action="store_true", help="Treat warnings as errors")

    # Evaluate command
    p_evaluate = subparsers.add_parser("evaluate", help="Evaluate system profile")
    p_evaluate.add_argument("-p", "--profile", type=Path, help="System profile JSON")
    p_evaluate.add_argument("-c", "--controls", type=Path, help="Controls YAML path")
    p_evaluate.add_argument("-o", "--output", type=Path, help="Output file path")
    p_evaluate.add_argument("-f", "--format", choices=["table", "markdown", "json"], default="table")
    p_evaluate.add_argument("--severity", choices=["low", "medium", "high", "critical"])
    p_evaluate.add_argument("--failed-only", action="store_true")

    # Classify command
    p_classify = subparsers.add_parser("classify", help="EU AI Act risk classification")
    p_classify.add_argument("-p", "--profile", type=Path, help="System profile JSON")
    p_classify.add_argument("-o", "--output", type=Path, help="Output file path")
    p_classify.add_argument("-f", "--format", choices=["table", "json"], default="table")

    # Init command
    p_init = subparsers.add_parser("init", help="Generate profile template")
    p_init.add_argument("-o", "--output", type=Path, help="Output file path")
    p_init.add_argument("-v", "--verbose", action="store_true", help="Show field guide")

    # Report command
    p_report = subparsers.add_parser("report", help="Generate full compliance report")
    p_report.add_argument("-p", "--profile", type=Path, help="System profile JSON")
    p_report.add_argument("-c", "--controls", type=Path, help="Controls YAML path")
    p_report.add_argument("-o", "--output", type=Path, help="Output file path")
    p_report.add_argument("-f", "--format", choices=["table", "json"], default="table")
    p_report.add_argument("-q", "--quiet", action="store_true")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to command handler
    commands = {
        "validate": cmd_validate,
        "evaluate": cmd_evaluate,
        "classify": cmd_classify,
        "init": cmd_init,
        "report": cmd_report
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
