"""
agents/report_agent.py
AGENT 5 of 5: Report Agent
Job: take everything from the previous 4 agents (findings, differentials,
evidence) and draft a final, structured radiologist-style report using
Google Gemini (FREE tier).
"""
from google import genai
from google.genai import types
from config import GEMINI_API_KEY
from agents.pipeline_state import set_status

client = genai.Client(api_key=GEMINI_API_KEY)

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
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_prompt,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        )
        report_text = response.text.strip()
        set_status("Report Agent", "done", "Report drafted successfully")
        return report_text

    except Exception as e:
        set_status("Report Agent", "error", f"Failed to draft report: {e}")
        return f"Report generation failed: {e}"
