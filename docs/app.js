/**
 * AI Governance Controls Evaluator
 * JavaScript port of evaluate_profile.py and risk_tier.py
 */

// =============================================================================
// Controls Catalog - Ported from controls/controls.yaml
// =============================================================================

const CONTROLS = [
    {
        id: "GOV-01",
        title: "System owner assigned",
        requirement: "A named accountable owner exists for the system.",
        evidence: "owner",
        severity: "high",
        nist_ai_rmf: ["GOVERN 1.1", "GOVERN 1.2"],
        eu_ai_act_article: "Art. 16 - Provider obligations"
    },
    {
        id: "GOV-02",
        title: "Data inventory exists",
        requirement: "System maintains an inventory of data types processed.",
        evidence: "data_inventory",
        severity: "high",
        nist_ai_rmf: ["MAP 1.1", "MAP 1.5"],
        eu_ai_act_article: "Art. 10 - Data governance"
    },
    {
        id: "GOV-03",
        title: "Logging enabled",
        requirement: "Security-relevant events are logged with retention policy.",
        evidence: "logging",
        severity: "medium",
        nist_ai_rmf: ["MEASURE 2.3", "MANAGE 2.2"],
        eu_ai_act_article: "Art. 12 - Record-keeping"
    },
    {
        id: "GOV-04",
        title: "Model change control",
        requirement: "Model updates require documented review/approval.",
        evidence: "change_control",
        severity: "high",
        nist_ai_rmf: ["GOVERN 1.4", "MANAGE 1.3"],
        eu_ai_act_article: "Art. 9 - Risk management system"
    },
    {
        id: "GOV-05",
        title: "Incident response playbook",
        requirement: "A playbook exists with roles + escalation path.",
        evidence: "ir_playbook",
        severity: "high",
        nist_ai_rmf: ["MANAGE 4.1", "MANAGE 4.2"],
        eu_ai_act_article: "Art. 62 - Reporting of serious incidents"
    },
    {
        id: "GOV-06",
        title: "Vendor due diligence",
        requirement: "Vendors have documented security + privacy review.",
        evidence: "vendor_review",
        severity: "medium",
        nist_ai_rmf: ["GOVERN 6.1", "MAP 3.4"],
        eu_ai_act_article: "Art. 25 - Responsibilities along the AI value chain"
    },
    {
        id: "GOV-07",
        title: "Access control",
        requirement: "Role-based access and least privilege for admin functions.",
        evidence: "access_control",
        severity: "high",
        nist_ai_rmf: ["GOVERN 1.5", "MANAGE 2.4"],
        eu_ai_act_article: "Art. 9 - Risk management system"
    },
    {
        id: "GOV-08",
        title: "Data retention defined",
        requirement: "Retention periods exist for all stored data categories.",
        evidence: "retention",
        severity: "medium",
        nist_ai_rmf: ["GOVERN 1.6", "MAP 1.5"],
        eu_ai_act_article: "Art. 10 - Data governance"
    },
    {
        id: "GOV-09",
        title: "Monitoring & alerting",
        requirement: "Alerts exist for abnormal patterns and failures.",
        evidence: "monitoring",
        severity: "medium",
        nist_ai_rmf: ["MEASURE 2.3", "MANAGE 2.2"],
        eu_ai_act_article: "Art. 9 - Risk management system"
    },
    {
        id: "GOV-10",
        title: "User-facing transparency",
        requirement: "Users are informed of key system behaviors/limits.",
        evidence: "transparency",
        severity: "low",
        nist_ai_rmf: ["MAP 1.6", "MANAGE 3.1"],
        eu_ai_act_article: "Art. 13 - Transparency and provision of information"
    },
    {
        id: "GOV-11",
        title: "Model documentation",
        requirement: "Model cards or system cards exist documenting intended use, limitations, and performance metrics.",
        evidence: "model_card",
        severity: "high",
        nist_ai_rmf: ["MAP 1.1", "MAP 1.3", "MEASURE 2.1"],
        eu_ai_act_article: "Art. 11 - Technical documentation"
    },
    {
        id: "GOV-12",
        title: "Training data provenance",
        requirement: "Training data sources are documented with licensing and consent status.",
        evidence: "data_provenance",
        severity: "high",
        nist_ai_rmf: ["MAP 1.5", "MEASURE 2.6"],
        eu_ai_act_article: "Art. 10 - Data governance"
    },
    {
        id: "GOV-13",
        title: "Bias and fairness testing",
        requirement: "Demographic performance disparities are measured and documented pre-deployment.",
        evidence: "fairness_eval",
        severity: "high",
        nist_ai_rmf: ["MEASURE 2.10", "MEASURE 2.11"],
        eu_ai_act_article: "Art. 10(2)(f) - Examination for bias"
    },
    {
        id: "GOV-14",
        title: "Human oversight mechanism",
        requirement: "High-risk decisions have a defined human review pathway.",
        evidence: "human_oversight",
        severity: "high",
        nist_ai_rmf: ["GOVERN 1.3", "MANAGE 2.1"],
        eu_ai_act_article: "Art. 14 - Human oversight"
    },
    {
        id: "GOV-15",
        title: "Output monitoring",
        requirement: "System outputs are sampled and reviewed for harmful or off-policy content.",
        evidence: "output_monitoring",
        severity: "medium",
        nist_ai_rmf: ["MEASURE 2.3", "MANAGE 2.2"],
        eu_ai_act_article: "Art. 9 - Risk management system"
    }
];

// =============================================================================
// Remediation Guidance - Ported from evaluate_profile.py
// =============================================================================

const REMEDIATION_GUIDANCE = {
    "GOV-01": {
        steps: [
            "Identify a senior stakeholder accountable for system outcomes",
            "Document the owner's name, role, and contact information",
            "Ensure owner has authority to make decisions about the system",
            "Add owner field to system profile JSON"
        ],
        artifacts: ["RACI matrix", "System ownership charter", "Org chart excerpt"]
    },
    "GOV-02": {
        steps: [
            "Catalog all data sources ingested by the system",
            "Document data types, schemas, and sensitivity classifications",
            "Map data flows from source to model to output",
            "Create a data dictionary with field-level descriptions"
        ],
        artifacts: ["Data inventory spreadsheet", "Data flow diagram", "Data dictionary"]
    },
    "GOV-03": {
        steps: [
            "Enable logging for authentication, authorization, and model inference",
            "Set log retention period per compliance requirements (min 90 days)",
            "Ensure logs include timestamp, user ID, action, and outcome",
            "Configure log forwarding to centralized SIEM"
        ],
        artifacts: ["Logging configuration", "Retention policy document", "SIEM integration docs"]
    },
    "GOV-04": {
        steps: [
            "Establish a change control board or approval process",
            "Require peer review for all model updates",
            "Document rollback procedures",
            "Maintain version history with change rationale"
        ],
        artifacts: ["Change control procedure", "Approval workflow", "Version control logs"]
    },
    "GOV-05": {
        steps: [
            "Create incident response playbook specific to AI failures",
            "Define escalation paths and on-call responsibilities",
            "Include model rollback and fallback procedures",
            "Conduct tabletop exercises annually"
        ],
        artifacts: ["IR playbook document", "Escalation matrix", "Tabletop exercise reports"]
    },
    "GOV-06": {
        steps: [
            "Create vendor assessment questionnaire covering security and AI ethics",
            "Review vendor's SOC 2, ISO 27001, or equivalent certifications",
            "Document data processing agreements and liability terms",
            "Conduct annual vendor risk reassessment"
        ],
        artifacts: ["Vendor assessment template", "Security questionnaire responses", "DPA agreements"]
    },
    "GOV-07": {
        steps: [
            "Implement role-based access control (RBAC)",
            "Apply least privilege principle to admin functions",
            "Enable multi-factor authentication for privileged access",
            "Conduct quarterly access reviews"
        ],
        artifacts: ["RBAC policy", "Access matrix", "Quarterly access review logs"]
    },
    "GOV-08": {
        steps: [
            "Define retention periods for each data category",
            "Implement automated data deletion or archival",
            "Document legal and regulatory retention requirements",
            "Create data retention schedule"
        ],
        artifacts: ["Retention policy", "Retention schedule", "Deletion audit logs"]
    },
    "GOV-09": {
        steps: [
            "Set up monitoring for model performance drift",
            "Configure alerts for anomalous input patterns",
            "Create dashboard for key model metrics",
            "Define alert thresholds and escalation procedures"
        ],
        artifacts: ["Monitoring dashboard", "Alert configuration", "Runbook for alerts"]
    },
    "GOV-10": {
        steps: [
            "Create user-facing documentation explaining AI involvement",
            "Document system limitations and failure modes",
            "Provide clear feedback mechanisms for users",
            "Include AI disclosure in terms of service"
        ],
        artifacts: ["User documentation", "Limitations disclosure", "ToS AI addendum"]
    },
    "GOV-11": {
        steps: [
            "Create model card documenting intended use and limitations",
            "Document training data characteristics and known biases",
            "Include performance metrics across relevant subgroups",
            "Update documentation with each model version"
        ],
        artifacts: ["Model card", "Performance reports", "Limitation documentation"]
    },
    "GOV-12": {
        steps: [
            "Document all training data sources with URLs/references",
            "Record licensing terms for each dataset",
            "Document consent status for personal data",
            "Maintain data lineage from source to model"
        ],
        artifacts: ["Data provenance log", "License inventory", "Consent records"]
    },
    "GOV-13": {
        steps: [
            "Define relevant protected groups for fairness evaluation",
            "Run disaggregated performance analysis across groups",
            "Set acceptable disparity thresholds",
            "Document mitigation steps for identified biases"
        ],
        artifacts: ["Fairness evaluation report", "Bias mitigation plan", "Disaggregated metrics"]
    },
    "GOV-14": {
        steps: [
            "Define which decisions require human review",
            "Create workflow for human-in-the-loop review",
            "Set criteria for escalation to human decision-maker",
            "Document override procedures and logging"
        ],
        artifacts: ["Human oversight policy", "Review workflow", "Override logs"]
    },
    "GOV-15": {
        steps: [
            "Implement output sampling and review process",
            "Create taxonomy of harmful or off-policy outputs",
            "Set up automated content filters where applicable",
            "Conduct periodic manual output audits"
        ],
        artifacts: ["Output review policy", "Sampling methodology", "Audit reports"]
    }
};

// =============================================================================
// EU AI Act Risk Classification - Ported from risk_tier.py
// =============================================================================

const HIGH_RISK_INDICATORS = {
    biometric: ["face", "facial", "fingerprint", "voice_id", "biometric", "identity"],
    critical_infrastructure: ["power", "water", "traffic", "energy", "grid", "scada"],
    education: ["student", "grading", "admission", "learning", "education"],
    employment: ["hiring", "recruitment", "employee", "hr", "performance_review", "termination"],
    essential_services: ["credit", "loan", "insurance", "benefits", "healthcare", "housing"],
    law_enforcement: ["police", "surveillance", "criminal", "enforcement", "security"],
    migration: ["visa", "border", "asylum", "immigration", "passport"],
    justice: ["court", "judge", "legal", "sentencing", "parole"]
};

const ANNEX_III_CATEGORIES = {
    biometric: "Biometric identification and categorisation",
    critical_infrastructure: "Management and operation of critical infrastructure",
    education: "Education and vocational training",
    employment: "Employment, workers management, access to self-employment",
    essential_services: "Access to essential private/public services and benefits",
    law_enforcement: "Law enforcement",
    migration: "Migration, asylum and border control management",
    justice: "Administration of justice and democratic processes"
};

const UNACCEPTABLE_INDICATORS = [
    "social_scoring",
    "subliminal",
    "exploitation_vulnerable",
    "real_time_biometric_public",
    "predictive_policing_individual"
];

const LIMITED_RISK_INDICATORS = [
    "chatbot",
    "emotion_recognition",
    "deepfake",
    "synthetic_media",
    "content_generation"
];

const TIER_OBLIGATIONS = {
    unacceptable: ["System deployment prohibited under EU AI Act Article 5"],
    high: [
        "Art. 9: Risk management system required",
        "Art. 10: Data governance requirements",
        "Art. 11: Technical documentation required",
        "Art. 12: Record-keeping obligations",
        "Art. 13: Transparency requirements",
        "Art. 14: Human oversight measures",
        "Art. 15: Accuracy, robustness, cybersecurity",
        "Art. 16: Provider quality management system",
        "Art. 17: CE marking and EU declaration of conformity"
    ],
    limited: [
        "Art. 50: Transparency obligations",
        "Users must be informed they are interacting with AI",
        "Synthetic content must be labeled"
    ],
    minimal: ["No specific EU AI Act obligations (general product safety applies)"]
};

// =============================================================================
// Sample System Profile
// =============================================================================

const SAMPLE_PROFILE = {
    "system_name": "Acme Risk Triage",
    "system_description": "ML-powered ticket routing and priority classification for customer support",
    "deployment_date": "2024-03-15",
    "risk_tier": "high",
    "owner": "Program Manager, Trust Ops",
    "data_inventory": [
        "support_tickets",
        "account_metadata",
        "interaction_history",
        "model_predictions"
    ],
    "logging": {
        "enabled": true,
        "retention_days": 90,
        "includes_model_inputs": true,
        "includes_model_outputs": true
    },
    "change_control": {
        "exists": true,
        "approver_role": "Risk Committee",
        "requires_testing": true,
        "rollback_procedure": true
    },
    "ir_playbook": {
        "exists": true,
        "pager_rotation": true,
        "escalation_path": ["On-call Engineer", "Trust Ops Lead", "CISO"],
        "last_drill": "2024-09-01"
    },
    "vendor_review": {
        "exists": false
    },
    "access_control": {
        "rbac": true,
        "mfa_admin": true,
        "roles_defined": ["viewer", "operator", "admin", "model_deployer"]
    },
    "retention": {
        "support_tickets_days": 365,
        "account_metadata_days": 730,
        "model_predictions_days": 90
    },
    "monitoring": {
        "alerts": [
            "error_rate_spike",
            "latency_spike",
            "prediction_drift",
            "fairness_metric_deviation"
        ]
    },
    "transparency": {
        "notice_url": "https://example.com/ai-notice",
        "user_informed_of_ai": true,
        "opt_out_available": false
    },
    "model_card": {
        "exists": true,
        "location": "https://internal.example.com/docs/risk-triage-model-card",
        "last_updated": "2024-06-01",
        "includes_limitations": true,
        "includes_performance_metrics": true
    },
    "data_provenance": {
        "documented": true,
        "sources": [
            {
                "name": "Historical support tickets",
                "consent_basis": "Legitimate interest",
                "license": "Internal data"
            },
            {
                "name": "Public benchmark dataset",
                "consent_basis": "Public domain",
                "license": "CC-BY-4.0"
            }
        ],
        "pii_handling": "Pseudonymized before training"
    },
    "fairness_eval": {
        "conducted": true,
        "last_evaluation": "2024-05-15",
        "metrics_measured": ["demographic_parity", "equalized_odds"],
        "protected_attributes": ["account_region", "account_tier"],
        "findings_documented": true,
        "remediation_applied": true
    },
    "human_oversight": {
        "exists": true,
        "mechanism": "High-priority predictions require human review",
        "threshold": "confidence < 0.85 OR escalation_flag = true",
        "reviewer_role": "Trust Ops Analyst"
    },
    "output_monitoring": {
        "enabled": true,
        "sample_rate": 0.05,
        "review_frequency": "weekly",
        "escalation_criteria": ["offensive_content", "pii_leakage", "policy_violation"]
    }
};

// =============================================================================
// Evaluation Logic
// =============================================================================

/**
 * Determine if a value indicates control compliance
 * Ported from Python truthy() function
 */
function isTruthy(val) {
    if (val === null || val === undefined) return false;
    if (typeof val === 'boolean') return val;
    if (typeof val === 'object') {
        if ('exists' in val) return Boolean(val.exists);
        if ('enabled' in val) return Boolean(val.enabled);
        if ('conducted' in val) return Boolean(val.conducted);
        if ('documented' in val) return Boolean(val.documented);
        if (Array.isArray(val)) return val.length > 0;
        return Object.keys(val).length > 0;
    }
    if (typeof val === 'string') return val.length > 0;
    if (Array.isArray(val)) return val.length > 0;
    if (typeof val === 'number') return true;
    return Boolean(val);
}

/**
 * Get nested path from object using dot notation
 */
function getPath(obj, path) {
    const parts = path.split('.');
    let current = obj;
    for (const part of parts) {
        if (current && typeof current === 'object' && part in current) {
            current = current[part];
        } else {
            return undefined;
        }
    }
    return current;
}

/**
 * Convert severity to weight for scoring
 */
function severityToWeight(severity) {
    const weights = { critical: 4, high: 3, medium: 2, low: 1 };
    return weights[severity.toLowerCase()] || 1;
}

/**
 * Evaluate all controls against a profile
 */
function evaluateControls(profile) {
    const results = [];

    for (const control of CONTROLS) {
        const evidenceValue = getPath(profile, control.evidence);
        const passed = isTruthy(evidenceValue);
        const guidance = REMEDIATION_GUIDANCE[control.id] || {};

        results.push({
            id: control.id,
            title: control.title,
            requirement: control.requirement,
            severity: control.severity,
            weight: severityToWeight(control.severity),
            passed: passed,
            evidencePath: control.evidence,
            evidenceValue: evidenceValue,
            nistMapping: control.nist_ai_rmf,
            euArticle: control.eu_ai_act_article,
            remediationSteps: guidance.steps || [],
            requiredArtifacts: guidance.artifacts || []
        });
    }

    return results;
}

/**
 * Calculate scores from evaluation results
 */
function calculateScores(results) {
    const totalControls = results.length;
    const passedControls = results.filter(r => r.passed).length;

    const totalWeight = results.reduce((sum, r) => sum + r.weight, 0);
    const earnedWeight = results.filter(r => r.passed).reduce((sum, r) => sum + r.weight, 0);

    const bySeverity = {};
    for (const sev of ['high', 'medium', 'low']) {
        const sevResults = results.filter(r => r.severity === sev);
        if (sevResults.length > 0) {
            bySeverity[sev] = {
                total: sevResults.length,
                passed: sevResults.filter(r => r.passed).length,
                failed: sevResults.filter(r => !r.passed).length
            };
        }
    }

    return {
        total: totalControls,
        passed: passedControls,
        failed: totalControls - passedControls,
        passRate: totalControls > 0 ? Math.round((passedControls / totalControls) * 1000) / 10 : 0,
        weightedScore: totalWeight > 0 ? Math.round((earnedWeight / totalWeight) * 1000) / 10 : 0,
        bySeverity: bySeverity
    };
}

/**
 * Classify risk tier based on profile
 * Ported from risk_tier.py
 */
function classifyRiskTier(profile) {
    const systemName = (profile.system_name || '').toLowerCase();
    const description = (profile.system_description || '').toLowerCase();
    const dataInventory = (profile.data_inventory || []).map(d => d.toLowerCase());

    const allText = `${systemName} ${description} ${dataInventory.join(' ')}`;

    // Check for unacceptable uses
    for (const indicator of UNACCEPTABLE_INDICATORS) {
        if (allText.includes(indicator)) {
            return {
                tier: 'unacceptable',
                reasons: [`Detected prohibited use indicator: ${indicator}`],
                obligations: TIER_OBLIGATIONS.unacceptable
            };
        }
    }

    // Check for high-risk indicators
    const highRiskMatches = [];
    for (const [category, keywords] of Object.entries(HIGH_RISK_INDICATORS)) {
        for (const keyword of keywords) {
            if (allText.includes(keyword)) {
                highRiskMatches.push({ category, keyword });
            }
        }
    }

    if (highRiskMatches.length > 0) {
        const categories = [...new Set(highRiskMatches.map(m => m.category))];
        const reasons = categories.map(cat =>
            `Matches Annex III category: ${ANNEX_III_CATEGORIES[cat] || cat}`
        );
        return {
            tier: 'high',
            reasons: reasons,
            obligations: TIER_OBLIGATIONS.high
        };
    }

    // Check for limited risk indicators
    const limitedReasons = [];
    for (const indicator of LIMITED_RISK_INDICATORS) {
        if (allText.includes(indicator)) {
            limitedReasons.push(`Limited risk indicator: ${indicator}`);
        }
    }

    if (limitedReasons.length > 0) {
        return {
            tier: 'limited',
            reasons: limitedReasons,
            obligations: TIER_OBLIGATIONS.limited
        };
    }

    // Default to minimal
    return {
        tier: 'minimal',
        reasons: ['No high-risk or limited-risk indicators detected'],
        obligations: TIER_OBLIGATIONS.minimal
    };
}

/**
 * Get compliance status based on scores
 */
function getComplianceStatus(scores, riskTier) {
    const highFailures = scores.bySeverity.high?.failed || 0;

    if (riskTier === 'unacceptable') {
        return {
            status: 'non-compliant',
            message: 'System uses prohibited AI practices'
        };
    }

    if (highFailures > 0) {
        return {
            status: 'non-compliant',
            message: `${highFailures} high-severity control(s) failed`
        };
    }

    if (scores.passRate < 80) {
        return {
            status: 'warning',
            message: 'Below 80% compliance threshold'
        };
    }

    return {
        status: 'compliant',
        message: 'Meets baseline requirements'
    };
}

// =============================================================================
// UI Functions
// =============================================================================

/**
 * Render the controls table
 */
function renderControlsTable(results) {
    const tbody = document.getElementById('controlsBody');
    tbody.innerHTML = '';

    for (const result of results) {
        const row = document.createElement('tr');
        row.className = result.passed ? 'passed' : 'failed';
        row.dataset.status = result.passed ? 'passed' : 'failed';

        row.innerHTML = `
            <td><code>${result.id}</code></td>
            <td>${result.title}</td>
            <td><span class="severity-pill ${result.severity}">${result.severity}</span></td>
            <td class="nist-mapping">${result.nistMapping.join(', ')}</td>
            <td class="eu-article">${result.euArticle}</td>
            <td>
                <span class="result-badge ${result.passed ? 'pass' : 'fail'}">
                    ${result.passed ? '&#10003; PASS' : '&#10007; FAIL'}
                </span>
            </td>
        `;

        tbody.appendChild(row);
    }
}

/**
 * Render failed controls with remediation guidance
 */
function renderFailedControls(results) {
    const failed = results.filter(r => !r.passed);
    const container = document.getElementById('failedControlsList');
    const section = document.getElementById('failedControls');

    if (failed.length === 0) {
        section.classList.add('hidden');
        return;
    }

    section.classList.remove('hidden');
    container.innerHTML = '';

    for (const result of failed) {
        const card = document.createElement('div');
        card.className = 'failed-control-card';

        let stepsHtml = '';
        if (result.remediationSteps.length > 0) {
            stepsHtml = `
                <div class="remediation-section">
                    <h5>Remediation Steps</h5>
                    <ol class="remediation-steps">
                        ${result.remediationSteps.map(step => `<li>${step}</li>`).join('')}
                    </ol>
                </div>
            `;
        }

        let artifactsHtml = '';
        if (result.requiredArtifacts.length > 0) {
            artifactsHtml = `
                <div class="artifacts-section">
                    <h5>Required Artifacts</h5>
                    <div class="artifacts-list">
                        ${result.requiredArtifacts.map(a => `<span class="artifact-tag">${a}</span>`).join('')}
                    </div>
                </div>
            `;
        }

        card.innerHTML = `
            <div class="failed-control-header">
                <span class="failed-control-title">${result.title}</span>
                <span class="failed-control-id">${result.id}</span>
            </div>
            <div class="failed-control-requirement">${result.requirement}</div>
            <div class="failed-control-evidence">
                Evidence path: <code>${result.evidencePath}</code> = <code>${JSON.stringify(result.evidenceValue)}</code>
            </div>
            ${stepsHtml}
            ${artifactsHtml}
        `;

        container.appendChild(card);
    }
}

/**
 * Render EU AI Act obligations
 */
function renderObligations(classification) {
    const section = document.getElementById('obligationsSection');
    const list = document.getElementById('obligationsList');

    if (classification.tier === 'minimal') {
        section.classList.add('hidden');
        return;
    }

    section.classList.remove('hidden');
    list.innerHTML = `
        <ul>
            ${classification.obligations.map(o => `<li>${o}</li>`).join('')}
        </ul>
    `;
}

/**
 * Update severity bars
 */
function updateSeverityBars(scores) {
    for (const sev of ['high', 'medium', 'low']) {
        const data = scores.bySeverity[sev] || { total: 0, passed: 0 };
        const bar = document.getElementById(`${sev}Bar`);
        const count = document.getElementById(`${sev}Count`);

        const percentage = data.total > 0 ? (data.passed / data.total) * 100 : 0;
        bar.style.width = `${percentage}%`;
        count.textContent = `${data.passed}/${data.total}`;
    }
}

/**
 * Display evaluation results
 */
function displayResults(profile, results, scores, classification) {
    // Show results section
    document.getElementById('results').classList.remove('hidden');

    // System name
    document.getElementById('systemName').textContent = profile.system_name || 'Unknown System';

    // Summary cards
    document.getElementById('passRate').textContent = `${scores.passRate}%`;
    document.getElementById('passCount').textContent = `${scores.passed} / ${scores.total} controls`;

    document.getElementById('weightedScore').textContent = `${scores.weightedScore}%`;

    const tierBadge = document.getElementById('riskTier');
    tierBadge.textContent = classification.tier.toUpperCase();
    tierBadge.className = `card-value tier-badge tier-${classification.tier}`;
    document.getElementById('tierReason').textContent = classification.reasons[0] || '';

    const complianceStatus = getComplianceStatus(scores, classification.tier);
    const statusBadge = document.getElementById('complianceStatus');
    statusBadge.textContent = complianceStatus.status.replace('-', ' ').toUpperCase();
    statusBadge.className = `card-value status-badge status-${complianceStatus.status}`;
    document.getElementById('statusMessage').textContent = complianceStatus.message;

    // Severity bars
    updateSeverityBars(scores);

    // Controls table
    renderControlsTable(results);

    // Failed controls
    renderFailedControls(results);

    // Obligations
    renderObligations(classification);

    // Scroll to results
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

/**
 * Main evaluation function
 */
function evaluate() {
    const input = document.getElementById('profileInput');
    const errorDiv = document.getElementById('jsonError');

    // Clear previous error
    errorDiv.classList.remove('show');
    errorDiv.textContent = '';

    // Parse JSON
    let profile;
    try {
        profile = JSON.parse(input.value);
    } catch (e) {
        errorDiv.textContent = `Invalid JSON: ${e.message}`;
        errorDiv.classList.add('show');
        return;
    }

    // Validate it's an object
    if (typeof profile !== 'object' || profile === null || Array.isArray(profile)) {
        errorDiv.textContent = 'Profile must be a JSON object';
        errorDiv.classList.add('show');
        return;
    }

    // Run evaluation
    const results = evaluateControls(profile);
    const scores = calculateScores(results);
    const classification = classifyRiskTier(profile);

    // Display results
    displayResults(profile, results, scores, classification);
}

/**
 * Load sample profile
 */
function loadSample() {
    const input = document.getElementById('profileInput');
    input.value = JSON.stringify(SAMPLE_PROFILE, null, 2);
}

/**
 * Clear input
 */
function clearInput() {
    document.getElementById('profileInput').value = '';
    document.getElementById('jsonError').classList.remove('show');
    document.getElementById('results').classList.add('hidden');
}

/**
 * Filter table rows
 */
function filterTable(filter) {
    const rows = document.querySelectorAll('#controlsBody tr');

    rows.forEach(row => {
        if (filter === 'all') {
            row.classList.remove('hidden');
        } else {
            const status = row.dataset.status;
            row.classList.toggle('hidden', status !== filter);
        }
    });

    // Update active filter button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.filter === filter);
    });
}

// =============================================================================
// Event Listeners
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Evaluate button
    document.getElementById('evaluate').addEventListener('click', evaluate);

    // Load sample button
    document.getElementById('loadSample').addEventListener('click', loadSample);

    // Clear button
    document.getElementById('clearInput').addEventListener('click', clearInput);

    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => filterTable(btn.dataset.filter));
    });

    // Allow Ctrl+Enter to evaluate
    document.getElementById('profileInput').addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            evaluate();
        }
    });
});
