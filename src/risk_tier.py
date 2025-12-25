#!/usr/bin/env python3
"""
risk_tier.py

Classifies AI systems according to EU AI Act risk tiers based on system profile.

Risk Tiers (EU AI Act):
- UNACCEPTABLE: Prohibited uses (social scoring, real-time biometric ID in public, etc.)
- HIGH: Listed in Annex III (employment, credit, law enforcement, etc.)
- LIMITED: Transparency obligations (chatbots, emotion recognition, etc.)
- MINIMAL: No specific obligations (spam filters, video games, etc.)

This is a simplified classifier for demonstration. Real classification requires
legal analysis of the specific use case against Annex III categories.

Usage:
    python risk_tier.py [OPTIONS]

Options:
    -p, --profile PATH    Path to system profile JSON (default: sample_system_profile.json)
    -f, --format FORMAT   Output format: table, json (default: table)
    -o, --output PATH     Output file path (optional)
    -q, --quiet           Minimal output
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime


# Annex III high-risk categories (simplified)
ANNEX_III_CATEGORIES = {
    "biometric": "Biometric identification and categorisation",
    "critical_infrastructure": "Management and operation of critical infrastructure",
    "education": "Education and vocational training",
    "employment": "Employment, workers management, access to self-employment",
    "essential_services": "Access to essential private/public services and benefits",
    "law_enforcement": "Law enforcement",
    "migration": "Migration, asylum and border control management",
    "justice": "Administration of justice and democratic processes"
}

# Keywords that suggest high-risk categories
HIGH_RISK_INDICATORS = {
    "biometric": ["face", "facial", "fingerprint", "voice_id", "biometric", "identity"],
    "critical_infrastructure": ["power", "water", "traffic", "energy", "grid", "scada"],
    "education": ["student", "grading", "admission", "learning", "education"],
    "employment": ["hiring", "recruitment", "employee", "hr", "performance_review", "termination"],
    "essential_services": ["credit", "loan", "insurance", "benefits", "healthcare", "housing"],
    "law_enforcement": ["police", "surveillance", "criminal", "enforcement", "security"],
    "migration": ["visa", "border", "asylum", "immigration", "passport"],
    "justice": ["court", "judge", "legal", "sentencing", "parole"]
}

# Unacceptable use indicators
UNACCEPTABLE_INDICATORS = [
    "social_scoring",
    "subliminal",
    "exploitation_vulnerable",
    "real_time_biometric_public",
    "predictive_policing_individual"
]

# Limited risk indicators (transparency obligations)
LIMITED_RISK_INDICATORS = [
    "chatbot",
    "emotion_recognition",
    "deepfake",
    "synthetic_media",
    "content_generation"
]


def classify_risk_tier(profile: Dict[str, Any]) -> Tuple[str, List[str], List[str]]:
    """
    Classify system into EU AI Act risk tier.
    
    Returns:
        - tier: "unacceptable", "high", "limited", or "minimal"
        - reasons: List of reasons for classification
        - obligations: List of applicable obligations
    """
    reasons = []
    obligations = []
    
    # Get system info for classification
    system_name = profile.get("system_name", "").lower()
    description = profile.get("system_description", "").lower()
    data_inventory = [d.lower() for d in profile.get("data_inventory", [])]
    declared_tier = profile.get("risk_tier", "").lower()
    
    # Combine all text for keyword matching
    all_text = f"{system_name} {description} {' '.join(data_inventory)}"
    
    # Check for unacceptable uses
    for indicator in UNACCEPTABLE_INDICATORS:
        if indicator in all_text:
            return (
                "unacceptable",
                [f"Detected prohibited use indicator: {indicator}"],
                ["System deployment prohibited under EU AI Act Article 5"]
            )
    
    # Check for high-risk indicators
    high_risk_matches = []
    for category, keywords in HIGH_RISK_INDICATORS.items():
        for keyword in keywords:
            if keyword in all_text:
                high_risk_matches.append((category, keyword))
    
    if high_risk_matches:
        categories = set(m[0] for m in high_risk_matches)
        reasons = [
            f"Matches Annex III category: {ANNEX_III_CATEGORIES.get(cat, cat)}"
            for cat in categories
        ]
        obligations = [
            "Art. 9: Risk management system required",
            "Art. 10: Data governance requirements",
            "Art. 11: Technical documentation required",
            "Art. 12: Record-keeping obligations",
            "Art. 13: Transparency requirements",
            "Art. 14: Human oversight measures",
            "Art. 15: Accuracy, robustness, cybersecurity",
            "Art. 16: Provider quality management system",
            "Art. 17: CE marking and EU declaration of conformity"
        ]
        return ("high", reasons, obligations)
    
    # Check for limited risk indicators
    for indicator in LIMITED_RISK_INDICATORS:
        if indicator in all_text:
            reasons.append(f"Limited risk indicator: {indicator}")
    
    if reasons:
        obligations = [
            "Art. 50: Transparency obligations",
            "Users must be informed they are interacting with AI",
            "Synthetic content must be labeled"
        ]
        return ("limited", reasons, obligations)
    
    # Default to minimal risk
    return (
        "minimal",
        ["No high-risk or limited-risk indicators detected"],
        ["No specific EU AI Act obligations (general product safety applies)"]
    )


def evaluate_high_risk_compliance(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    For high-risk systems, evaluate compliance with Annex III requirements.
    """
    checks = {
        "risk_management_system": bool(profile.get("ir_playbook", {}).get("exists")),
        "data_governance": bool(profile.get("data_provenance", {}).get("documented")),
        "technical_documentation": bool(profile.get("model_card", {}).get("exists")),
        "record_keeping": bool(profile.get("logging", {}).get("enabled")),
        "transparency": bool(profile.get("transparency", {}).get("user_informed_of_ai")),
        "human_oversight": bool(profile.get("human_oversight", {}).get("exists")),
        "accuracy_testing": bool(profile.get("fairness_eval", {}).get("conducted"))
    }
    
    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    
    return {
        "checks": checks,
        "passed": passed,
        "total": total,
        "compliance_rate": round(passed / total * 100, 1) if total > 0 else 0
    }


def print_classification_report(profile: Dict[str, Any]):
    """Print the risk tier classification report."""
    
    tier, reasons, obligations = classify_risk_tier(profile)
    
    tier_colors = {
        "unacceptable": "🔴",
        "high": "🟠",
        "limited": "🟡",
        "minimal": "🟢"
    }
    
    print("=" * 70)
    print("EU AI ACT RISK TIER CLASSIFICATION")
    print("=" * 70)
    print(f"System: {profile.get('system_name', 'Unknown')}")
    print(f"Description: {profile.get('system_description', 'N/A')}")
    print("=" * 70)
    
    print(f"\n## Classification Result\n")
    print(f"**Risk Tier:** {tier_colors.get(tier, '⚪')} {tier.upper()}")
    
    print(f"\n### Classification Reasons\n")
    for reason in reasons:
        print(f"- {reason}")
    
    print(f"\n### Applicable Obligations\n")
    for obligation in obligations:
        print(f"- {obligation}")
    
    # For high-risk systems, show compliance status
    if tier == "high":
        print("\n" + "=" * 70)
        print("## HIGH-RISK COMPLIANCE CHECK")
        print("=" * 70)
        
        compliance = evaluate_high_risk_compliance(profile)
        
        print(f"\n**Compliance Rate:** {compliance['compliance_rate']}%\n")
        print("| Requirement | Status |")
        print("|-------------|--------|")
        
        requirement_names = {
            "risk_management_system": "Risk Management System (Art. 9)",
            "data_governance": "Data Governance (Art. 10)",
            "technical_documentation": "Technical Documentation (Art. 11)",
            "record_keeping": "Record-Keeping (Art. 12)",
            "transparency": "Transparency (Art. 13)",
            "human_oversight": "Human Oversight (Art. 14)",
            "accuracy_testing": "Accuracy/Fairness Testing (Art. 15)"
        }
        
        for check, passed in compliance["checks"].items():
            status = "✅" if passed else "❌"
            name = requirement_names.get(check, check)
            print(f"| {name} | {status} |")
        
        # Gaps
        gaps = [k for k, v in compliance["checks"].items() if not v]
        if gaps:
            print("\n### Compliance Gaps\n")
            for gap in gaps:
                print(f"- ❌ {requirement_names.get(gap, gap)}: Evidence missing or insufficient")


def generate_json_report(profile: Dict[str, Any]) -> str:
    """Generate a JSON classification report."""
    tier, reasons, obligations = classify_risk_tier(profile)

    report = {
        "metadata": {
            "system_name": profile.get("system_name", "Unknown"),
            "system_description": profile.get("system_description", ""),
            "classified_at": datetime.now().isoformat()
        },
        "classification": {
            "risk_tier": tier,
            "reasons": reasons,
            "obligations": obligations
        }
    }

    # Add high-risk compliance if applicable
    if tier == "high":
        compliance = evaluate_high_risk_compliance(profile)
        report["high_risk_compliance"] = compliance

    return json.dumps(report, indent=2)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Classify AI systems under EU AI Act risk tiers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Classify default sample profile
  python risk_tier.py

  # Classify a specific profile
  python risk_tier.py -p my_system.json

  # Output as JSON
  python risk_tier.py -p my_system.json -f json

  # Save report to file
  python risk_tier.py -p my_system.json -o classification.json -f json
"""
    )

    parser.add_argument(
        "-p", "--profile",
        type=Path,
        help="Path to system profile JSON (default: sample_system_profile.json)"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file path (optional)"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Minimal output"
    )

    return parser.parse_args()


def main():
    args = parse_args()
    script_dir = Path(__file__).parent

    # Determine profile path
    if args.profile:
        profile_path = args.profile
    else:
        profile_path = script_dir / "sample_system_profile.json"

    if not profile_path.exists():
        print(f"ERROR: Profile not found at {profile_path}")
        sys.exit(1)

    with open(profile_path) as f:
        profile = json.load(f)

    # Generate output
    if args.format == "json":
        output = generate_json_report(profile)
        if not args.quiet:
            print(output)
    else:
        if not args.quiet:
            print_classification_report(profile)

    # Save to file if specified
    if args.output:
        if args.format == "json":
            content = generate_json_report(profile)
        else:
            # For table format, we save as JSON anyway
            content = generate_json_report(profile)

        with open(args.output, "w") as f:
            f.write(content)
        if not args.quiet:
            print(f"\nReport saved to: {args.output}")

    # Exit with code based on risk tier
    tier, _, _ = classify_risk_tier(profile)
    if tier == "unacceptable":
        sys.exit(2)  # Prohibited
    elif tier == "high":
        compliance = evaluate_high_risk_compliance(profile)
        if compliance["compliance_rate"] < 100:
            sys.exit(1)  # High-risk with gaps

    sys.exit(0)


if __name__ == "__main__":
    main()
