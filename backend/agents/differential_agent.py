"""
agents/differential_agent.py
AGENT 3 of 5: Differential Agent
Job: take the Detection Agent's findings and ask Google Gemini (FREE tier)
to produce a ranked DIFFERENTIAL DIAGNOSIS — i.e. "given these findings,
what are the most likely conditions, ranked by probability, with reasoning."

Get a free Gemini API key at: https://aistudio.google.com/app/apikey
"""
import json
from config import is_valid_gemini_key
from agents.pipeline_state import set_status
from agents.fallbacks import demo_differentials
from agents import gemini_utils

SYSTEM_PROMPT = """You are a differential diagnosis assistant supporting a radiologist.
Given a list of imaging findings, return ONLY valid JSON (no markdown, no preamble) as a list of objects:
[{"diagnosis": "...", "probability": 0.0-1.0, "reasoning": "one sentence"}]
Order by probability, highest first. Include 2-4 differentials. This is decision support only,
not a final diagnosis — a licensed radiologist must confirm."""


def rank_differentials(findings: list[dict]) -> list[dict]:
    set_status("Differential Agent", "active", "Ranking possible diagnoses...")

    if not is_valid_gemini_key():
        differentials = demo_differentials(findings)
        set_status("Differential Agent", "done", f"Ranked {len(differentials)} differential(s) (local mode)")
        return differentials

    findings_text = "\n".join(
        f"- {f['label']} (confidence: {f['confidence']:.2f}, location: {f.get('location', 'N/A')})"
        for f in findings
    )

    try:
        raw_text = gemini_utils.generate_text(
            SYSTEM_PROMPT,
            f"Findings:\n{findings_text}",
        )
        raw_text = raw_text.replace("```json", "").replace("```", "").strip()
        differentials = json.loads(raw_text)
        set_status("Differential Agent", "done", f"Ranked {len(differentials)} differential(s)")
        return differentials

    except (json.JSONDecodeError, ValueError, gemini_utils.GeminiKeysExhaustedError, Exception):
        differentials = demo_differentials(findings)
        set_status("Differential Agent", "done", f"Ranked {len(differentials)} differential(s) (fallback)")
        return differentials
