"""
agents/report_agent.py
AGENT 5 of 5: Report Agent
Job: take everything from the previous 4 agents (findings, differentials,
evidence) and draft a final, structured radiologist-style report using
Google Gemini (FREE tier).
"""
from config import is_valid_gemini_key
from agents.pipeline_state import set_status
from agents.fallbacks import demo_report
from agents import gemini_utils

SYSTEM_PROMPT = """You are a medical report-writing assistant helping draft a structured
radiology report for a licensed radiologist to review and sign off on.
Write in this format:

FINDINGS:
(summarize the imaging findings in clinical language)

IMPRESSION:
(list the differential diagnoses, most likely first)

RECOMMENDATION:
(suggest next steps, e.g. follow-up imaging, specialist referral)

Always end with: "This report was AI-assisted and requires review by a licensed radiologist before clinical use."
Keep it concise — under 200 words."""


def draft_report(findings: list[dict], differentials: list[dict], evidence: list[dict]) -> str:
    set_status("Report Agent", "active", "Drafting radiologist report...")

    if not is_valid_gemini_key():
        report_text = demo_report(findings, differentials, evidence)
        set_status("Report Agent", "done", "Report drafted (local mode)")
        return report_text

    findings_text = "\n".join(f"- {f['label']} ({f['confidence']:.0%} confidence)" for f in findings)
    differentials_text = "\n".join(
        f"- {d['diagnosis']} ({d['probability']:.0%}): {d['reasoning']}" for d in differentials
    )
    evidence_text = "\n".join(f"- {e['diagnosis']}: {e['citation']}" for e in evidence)

    user_prompt = f"""Findings:
{findings_text}

Differential diagnoses:
{differentials_text}

Supporting literature:
{evidence_text}

Draft the report now."""

    try:
        report_text = gemini_utils.generate_text(SYSTEM_PROMPT, user_prompt)
        set_status("Report Agent", "done", "Report drafted successfully")
        return report_text

    except (gemini_utils.GeminiKeysExhaustedError, Exception):
        report_text = demo_report(findings, differentials, evidence)
        set_status("Report Agent", "done", "Report drafted (fallback)")
        return report_text
