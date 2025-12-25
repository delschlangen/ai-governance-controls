#!/usr/bin/env python3
"""
validate_controls.py

Validates the controls.yaml file for:
- Required fields present on each control
- Valid severity levels
- Unique control IDs
- Valid evidence path format
"""

import yaml
import sys
from pathlib import Path
from typing import List, Dict, Any

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


def main():
    # Determine path to controls file
    script_dir = Path(__file__).parent
    controls_path = script_dir.parent / "controls" / "controls.yaml"
    
    if not controls_path.exists():
        print(f"ERROR: Controls file not found at {controls_path}")
        sys.exit(1)
    
    print(f"Validating: {controls_path}\n")
    print("=" * 60)
    
    # Load controls
    try:
        data = load_controls(controls_path)
    except yaml.YAMLError as e:
        print(f"ERROR: Invalid YAML syntax\n{e}")
        sys.exit(1)
    
    controls = data.get("controls", [])
    
    if not controls:
        print("ERROR: No controls found in file")
        sys.exit(1)
    
    print(f"Found {len(controls)} controls\n")
    
    # Validate
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
        
        if errors:
            for error in errors:
                all_errors.append(f"[{control_id}] {error}")
        
        if warnings:
            for warning in warnings:
                all_warnings.append(f"[{control_id}] {warning}")
    
    # Report results
    print("VALIDATION RESULTS")
    print("=" * 60)
    
    if all_errors:
        print(f"\n❌ ERRORS ({len(all_errors)}):")
        for error in all_errors:
            print(f"   • {error}")
    
    if all_warnings:
        print(f"\n⚠️  WARNINGS ({len(all_warnings)}):")
        for warning in all_warnings:
            print(f"   • {warning}")
    
    if not all_errors and not all_warnings:
        print("\n✅ All controls passed validation!")
    elif not all_errors:
        print(f"\n✅ Validation passed with {len(all_warnings)} warnings")
    
    # Summary stats
    print("\n" + "=" * 60)
    print("SUMMARY")
    print(f"  Total controls: {len(controls)}")
    print(f"  Errors: {len(all_errors)}")
    print(f"  Warnings: {len(all_warnings)}")
    
    # Severity breakdown
    severity_counts = {}
    for control in controls:
        sev = control.get("severity", "unknown")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
    
    print("\n  Severity Distribution:")
    for sev in ["critical", "high", "medium", "low"]:
        if sev in severity_counts:
            print(f"    {sev}: {severity_counts[sev]}")
    
    # Exit with error code if validation failed
    sys.exit(1 if all_errors else 0)


if __name__ == "__main__":
    main()
