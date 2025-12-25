#!/usr/bin/env python3
"""
validate_controls.py

Validates the controls.yaml file for:
- Required fields present on each control
- Valid severity levels
- Unique control IDs
- Valid evidence path format

Usage:
    python validate_controls.py [OPTIONS]

Options:
    -c, --controls PATH   Path to controls YAML (default: controls/controls.yaml)
    -f, --format FORMAT   Output format: table, json (default: table)
    -q, --quiet           Only output errors (no summary stats)
    --strict              Treat warnings as errors
"""

import argparse
import json
import yaml
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Required fields for each control
REQUIRED_FIELDS = ["id", "title", "requirement", "evidence", "severity"]

# Valid severity levels
VALID_SEVERITIES = ["low", "medium", "high", "critical"]

# Optional but recommended fields
RECOMMENDED_FIELDS = ["nist_ai_rmf", "eu_ai_act_article"]


def load_controls(filepath: str) -> Dict[str, Any]:
    """Load and parse the controls YAML file."""
    with open(filepath, "r") as f:
        return yaml.safe_load(f)


def validate_required_fields(control: Dict[str, Any]) -> List[str]:
    """Check that all required fields are present."""
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in control:
            errors.append(f"Missing required field: {field}")
        elif not control[field]:
            errors.append(f"Empty required field: {field}")
    return errors


def validate_severity(control: Dict[str, Any]) -> List[str]:
    """Check that severity is a valid value."""
    errors = []
    severity = control.get("severity", "").lower()
    if severity and severity not in VALID_SEVERITIES:
        errors.append(f"Invalid severity '{severity}'. Must be one of: {VALID_SEVERITIES}")
    return errors


def validate_evidence_path(control: Dict[str, Any]) -> List[str]:
    """Check that evidence path follows expected format."""
    errors = []
    evidence = control.get("evidence", "")
    if evidence and not evidence.startswith("system_profile."):
        errors.append(f"Evidence path should start with 'system_profile.' Got: {evidence}")
    return errors


def check_recommended_fields(control: Dict[str, Any]) -> List[str]:
    """Warn about missing recommended fields."""
    warnings = []
    for field in RECOMMENDED_FIELDS:
        if field not in control:
            warnings.append(f"Missing recommended field: {field}")
    return warnings


def validate_unique_ids(controls: List[Dict[str, Any]]) -> List[str]:
    """Check that all control IDs are unique."""
    errors = []
    seen_ids = set()
    for control in controls:
        control_id = control.get("id", "")
        if control_id in seen_ids:
            errors.append(f"Duplicate control ID: {control_id}")
        seen_ids.add(control_id)
    return errors


def validate_controls_file(controls_path: Path, strict: bool = False) -> Dict[str, Any]:
    """Validate a controls file and return results."""
    try:
        data = load_controls(controls_path)
    except yaml.YAMLError as e:
        return {
            "valid": False,
            "error": f"Invalid YAML syntax: {e}",
            "controls_count": 0,
            "errors": [],
            "warnings": []
        }

    controls = data.get("controls", [])

    if not controls:
        return {
            "valid": False,
            "error": "No controls found in file",
            "controls_count": 0,
            "errors": [],
            "warnings": []
        }

    all_errors = []
    all_warnings = []

    # Check unique IDs across all controls
    id_errors = validate_unique_ids(controls)
    all_errors.extend(id_errors)

    # Validate each control
    for control in controls:
        control_id = control.get("id", "UNKNOWN")

        errors = []
        errors.extend(validate_required_fields(control))
        errors.extend(validate_severity(control))
        errors.extend(validate_evidence_path(control))

        warnings = check_recommended_fields(control)

        for error in errors:
            all_errors.append({"control_id": control_id, "message": error, "type": "error"})

        for warning in warnings:
            all_warnings.append({"control_id": control_id, "message": warning, "type": "warning"})

    # Severity breakdown
    severity_counts = {}
    for control in controls:
        sev = control.get("severity", "unknown")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    is_valid = len(all_errors) == 0 and (not strict or len(all_warnings) == 0)

    return {
        "valid": is_valid,
        "controls_count": len(controls),
        "errors": all_errors,
        "warnings": all_warnings,
        "severity_distribution": severity_counts,
        "validated_at": datetime.now().isoformat()
    }


def print_table_report(result: Dict[str, Any], controls_path: Path, quiet: bool = False):
    """Print validation results in table format."""
    if not quiet:
        print(f"Validating: {controls_path}\n")
        print("=" * 60)
        print(f"Found {result['controls_count']} controls\n")

    print("VALIDATION RESULTS")
    print("=" * 60)

    if result.get("error"):
        print(f"\nERROR: {result['error']}")
        return

    errors = result.get("errors", [])
    warnings = result.get("warnings", [])

    if errors:
        print(f"\nERRORS ({len(errors)}):")
        for err in errors:
            print(f"   [{err['control_id']}] {err['message']}")

    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):")
        for warn in warnings:
            print(f"   [{warn['control_id']}] {warn['message']}")

    if not errors and not warnings:
        print("\nAll controls passed validation!")
    elif not errors:
        print(f"\nValidation passed with {len(warnings)} warnings")

    if not quiet:
        print("\n" + "=" * 60)
        print("SUMMARY")
        print(f"  Total controls: {result['controls_count']}")
        print(f"  Errors: {len(errors)}")
        print(f"  Warnings: {len(warnings)}")

        severity_counts = result.get("severity_distribution", {})
        print("\n  Severity Distribution:")
        for sev in ["critical", "high", "medium", "low"]:
            if sev in severity_counts:
                print(f"    {sev}: {severity_counts[sev]}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate AI governance controls catalog",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate default controls file
  python validate_controls.py

  # Validate a specific file
  python validate_controls.py -c my_controls.yaml

  # Output as JSON
  python validate_controls.py -f json

  # Strict mode (warnings are errors)
  python validate_controls.py --strict

  # Quiet mode (only errors)
  python validate_controls.py -q
"""
    )

    parser.add_argument(
        "-c", "--controls",
        type=Path,
        help="Path to controls YAML (default: controls/controls.yaml)"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Only output errors (no summary stats)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )

    return parser.parse_args()


def main():
    args = parse_args()
    script_dir = Path(__file__).parent

    # Determine path to controls file
    if args.controls:
        controls_path = args.controls
    else:
        controls_path = script_dir.parent / "controls" / "controls.yaml"

    if not controls_path.exists():
        print(f"ERROR: Controls file not found at {controls_path}")
        sys.exit(1)

    # Validate
    result = validate_controls_file(controls_path, args.strict)

    # Output
    if args.format == "json":
        result["file"] = str(controls_path)
        print(json.dumps(result, indent=2))
    else:
        print_table_report(result, controls_path, args.quiet)

    # Exit with error code if validation failed
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
