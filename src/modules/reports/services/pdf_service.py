"""
VeldrixAI PDF Service — thin wrapper around the branded pdf_generator.
"""

from datetime import datetime
from typing import Any, Dict

from src.modules.reports.services.pdf_generator import generate_veldrix_pdf


# ── Pillar thresholds ─────────────────────────────────────────────────────────
_PASS  = 85.0
_WARN  = 70.0

# Per-pillar: (severity_if_fail, severity_if_warn, finding_template, rec_template)
_PILLAR_META: Dict[str, Dict] = {
    "Content Risk Analysis": {
        "fail_sev": "CRITICAL",
        "warn_sev": "HIGH",
        "finding_fail": "Content safety score is critically low ({score:.1f}/100). The model produced responses flagged as harmful, toxic, or policy-violating.",
        "finding_warn": "Content safety score is below target ({score:.1f}/100). Some responses contain borderline harmful or inappropriate content.",
        "finding_pass": "No harmful or toxic content detected. Content safety checks passed.",
        "rec_fail": "Immediately enable hard-block enforcement on the Content Risk pillar at threshold 0.85. Review all flagged responses and audit the model's training data for harmful patterns.",
        "rec_warn": "Lower the Content Risk soft-block threshold to 0.80 and enable response rewriting for borderline cases. Schedule a content safety audit.",
    },
    "Hallucination & Factual Integrity": {
        "fail_sev": "HIGH",
        "warn_sev": "MEDIUM",
        "finding_fail": "Hallucination risk is high ({score:.1f}/100). The model is generating factually unreliable or ungrounded responses at a significant rate.",
        "finding_warn": "Hallucination risk is elevated ({score:.1f}/100). Some responses contain uncertain or unverified claims.",
        "finding_pass": "Factual integrity checks passed. Responses are well-grounded with low hallucination risk.",
        "rec_fail": "Deploy a Retrieval-Augmented Generation (RAG) layer to ground model responses against a verified knowledge base. Enable hallucination hard-block for high-stakes query types.",
        "rec_warn": "Add a RAG grounding layer for knowledge-intensive queries. Enable uncertain-claim flagging and surface confidence scores to end-users.",
    },
    "Bias & Ethics Analysis": {
        "fail_sev": "HIGH",
        "warn_sev": "MEDIUM",
        "finding_fail": "Bias and ethics score is critically low ({score:.1f}/100). The model is producing responses with significant demographic bias or ethical violations.",
        "finding_warn": "Bias score is below target ({score:.1f}/100). Responses show measurable demographic or ethical bias in some cases.",
        "finding_pass": "No significant demographic bias or ethical violations detected. Bias checks passed.",
        "rec_fail": "Immediately block or rewrite responses flagged for bias. Initiate a bias audit across demographic groups and consider fine-tuning on a debiased dataset.",
        "rec_warn": "Enable bias-aware rewriting for flagged responses. Conduct quarterly bias audits and monitor demographic parity metrics.",
    },
    "Policy Violation & Prompt Security": {
        "fail_sev": "CRITICAL",
        "warn_sev": "HIGH",
        "finding_fail": "Policy and prompt security score is critically low ({score:.1f}/100). Prompt injection attempts or serious policy violations were detected.",
        "finding_warn": "Policy compliance score is below target ({score:.1f}/100). Some responses violate business policy rules or show signs of prompt manipulation.",
        "finding_pass": "No prompt injection or policy violations detected. Security checks passed.",
        "rec_fail": "Enable hard-block on all prompt injection patterns immediately. Review violated policy rules and tighten the policy context passed to the evaluation engine.",
        "rec_warn": "Tighten policy rule definitions and enable soft-block with human review for borderline violations. Update injection detection patterns regularly.",
    },
    "Legal Exposure & Compliance": {
        "fail_sev": "HIGH",
        "warn_sev": "MEDIUM",
        "finding_fail": "Legal and compliance score is critically low ({score:.1f}/100). Responses contain significant legal exposure, PII leakage, or regulatory violations.",
        "finding_warn": "Legal exposure score is below target ({score:.1f}/100). Some responses may require disclaimers or contain regulatory risk.",
        "finding_pass": "No significant legal exposure or compliance violations detected.",
        "rec_fail": "Enable PII auto-masking immediately. Block responses with high legal risk scores and engage legal review for flagged content categories.",
        "rec_warn": "Enable automatic disclaimer injection for responses flagged with legal risk. Activate PII masking for email, phone, and ID patterns.",
    },
}

# Fallback for pillar names not in the map (e.g. degraded/partial)
_PILLAR_META_DEFAULT: Dict[str, str] = {
    "fail_sev": "MEDIUM",
    "warn_sev": "LOW",
    "finding_fail": "Pillar score is below acceptable threshold ({score:.1f}/100).",
    "finding_warn": "Pillar score is below target ({score:.1f}/100). Review flagged responses.",
    "finding_pass": "Pillar checks passed.",
    "rec_fail": "Investigate pillar failures and review flagged responses.",
    "rec_warn": "Monitor this pillar and review borderline responses.",
}


def _derive_findings_and_recs(
    pillar_scores: Dict[str, float],
    pillar_weights: Dict[str, float],
    pillar_results: Dict[str, Any],
    overall: float,
    risk_level: str,
    enforcement: Dict[str, int],
) -> tuple:
    """Derive precise findings and recommendations from actual evaluation data."""
    findings: list = []
    recommendations: list = []

    # Build a flags map: pillar_name -> list of flags
    flags_map: Dict[str, list] = {}
    for pid, pdata in pillar_results.items():
        name = pdata.get("metadata", {}).get("name", pid)
        flags_map[name] = pdata.get("flags", [])

    for pillar_name, score in pillar_scores.items():
        meta = _PILLAR_META.get(pillar_name, _PILLAR_META_DEFAULT)
        flags = flags_map.get(pillar_name, [])
        flags_str = f" Flags: {', '.join(flags[:4])}" if flags else ""

        if score < _WARN:
            sev = meta["fail_sev"]
            desc = meta["finding_fail"].format(score=score) + flags_str
            rec_body = meta["rec_fail"]
        elif score < _PASS:
            sev = meta["warn_sev"]
            desc = meta["finding_warn"].format(score=score) + flags_str
            rec_body = meta["rec_warn"]
        else:
            sev = "PASS"
            desc = meta["finding_pass"] + (flags_str if flags else "")
            rec_body = None

        findings.append({
            "pillar": pillar_name,
            "severity": sev,
            "description": desc,
            "action": rec_body or "Continue monitoring. No immediate action required.",
        })

        if rec_body:
            recommendations.append({
                "title": f"{'[CRITICAL] ' if sev == 'CRITICAL' else ''}{pillar_name} — {sev.title()} Risk Remediation",
                "body": rec_body,
            })

    # Overall risk-level recommendation
    if risk_level in ("HIGH_RISK", "CRITICAL"):
        recommendations.insert(0, {
            "title": "Immediate Action Required — Overall Trust Score Below Safe Threshold",
            "body": (
                f"The overall trust score of {overall:.1f}/100 indicates this model response "
                f"was classified as {risk_level.replace('_', ' ')}. "
                "Do not deploy this response to end-users without human review. "
                "Enforce a hard-block policy for responses scoring below 70 across any critical pillar."
            ),
        })
    elif risk_level == "REVIEW_REQUIRED":
        recommendations.append({
            "title": "Manual Review Recommended — Borderline Trust Score",
            "body": (
                f"The overall trust score of {overall:.1f}/100 falls in the caution zone. "
                "Route this response type through a human review queue before production deployment. "
                "Consider tightening pillar thresholds for this model or use-case."
            ),
        })

    # If everything passed, add a positive maintenance recommendation
    if not recommendations:
        recommendations.append({
            "title": "Maintain Current Governance Configuration",
            "body": (
                f"All five trust pillars passed with an overall score of {overall:.1f}/100. "
                "Continue monitoring with the current configuration. "
                "Schedule quarterly audits to ensure sustained compliance as model usage scales."
            ),
        })

    return findings, recommendations


class PDFService:
    @staticmethod
    def generate_report_pdf(
        title: str,
        report_type: str,
        input_payload: Dict[str, Any],
        output_summary: str,
        created_at: datetime,
        report_name: str = "Cobalt Nexus",
        vx_report_id: str = "VX-00000000-0000",
        tenant: str = "VeldrixAI Platform",
    ) -> bytes:
        """
        Generate a branded VeldrixAI PDF report.

        Extracts structured trust evaluation data from input_payload when available
        (produced by the evaluate endpoint) and passes it to the full PDF generator.
        Falls back to sample/default data for missing fields.
        """
        result: Dict[str, Any] = input_payload.get("result", {}) if input_payload else {}
        final_score = result.get("final_score") or {}
        pillar_results = result.get("pillar_results") or {}

        # Build pillar scores and weights from real evaluation data
        # Scores from core are already 0-100 range — do NOT multiply by 100
        pillar_scores: Dict[str, float] = {}
        pillar_weights: Dict[str, float] = {}
        for pid, pdata in pillar_results.items():
            name = pdata.get("metadata", {}).get("name", pid)
            raw_score = pdata.get("score", {})
            val = raw_score.get("value", 0) if isinstance(raw_score, dict) else float(raw_score or 0)
            pillar_scores[name] = round(float(val), 1)  # already 0-100
            weight = pdata.get("metadata", {}).get("weight", 0.20)
            # weight may be stored as fraction (0.25) or percent (25) — normalise to fraction
            pillar_weights[name] = float(weight) if float(weight) <= 1.0 else float(weight) / 100.0

        # Overall score: final_score.value is already 0-100
        raw_overall = final_score.get("value")
        overall = round(float(raw_overall), 1) if raw_overall is not None else None
        # Fallback: weighted average from pillar scores
        if overall is None and pillar_scores and pillar_weights:
            overall = round(
                sum(pillar_scores[p] * pillar_weights.get(p, 0.2) for p in pillar_scores), 1
            )
        overall = overall or 0.0

        # Enforcement action derived from risk_level
        risk_level = str(final_score.get("risk_level", "")).upper()
        enforcement_action = final_score.get("enforcement_action", "")
        if str(enforcement_action).upper() in ("BLOCK", "BLOCKED") or risk_level in ("HIGH_RISK", "HIGH", "CRITICAL"):
            enforcement = {"Allow": 0, "Block": 1, "Rewrite": 0}
        else:
            enforcement = {"Allow": 1, "Block": 0, "Rewrite": 0}

        model = input_payload.get("model", "—") if input_payload else "—"
        provider = input_payload.get("provider", "") if input_payload else ""
        model_name = f"{model} ({provider})" if provider else model

        findings, recommendations = _derive_findings_and_recs(
            pillar_scores, pillar_weights, pillar_results, overall, risk_level, enforcement
        )

        report_data = {
            "report_name":   report_name,
            "vx_report_id":  vx_report_id,
            "title":         title or "AI Model Trust Evaluation Report",
            "subtitle":      "Deep Research Analysis · VeldrixAI Runtime Evaluation",
            "report_type":   report_type.replace("_", " ").title(),
            "generated_at":  created_at.strftime("%B %d, %Y %H:%M UTC"),
            "model_name":    model_name,
            "eval_window":   "Single Evaluation",
            "total_evals":   1,
            "tenant":        tenant,
            "pillar_version": "v2.1.0",
            "overall_score": overall,
            "pillar_scores": pillar_scores or {},
            "pillar_weights": pillar_weights or {
                "Safety": 0.25, "Hallucination": 0.25, "Bias": 0.20,
                "Prompt Security": 0.15, "Compliance": 0.15,
            },
            "enforcement_actions": enforcement,
            "findings": findings,
            "recommendations": recommendations,
            "executive_summary": output_summary or (
                "This report presents the trust evaluation results for the specified AI model "
                "response, evaluated against the VeldrixAI five-pillar governance framework. "
                "Each pillar was assessed independently using dedicated detection models and "
                "heuristics, with results combined into a weighted overall trust score."
            ),
        }

        return generate_veldrix_pdf(report_data)
