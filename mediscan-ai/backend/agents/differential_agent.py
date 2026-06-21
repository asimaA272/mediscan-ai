"""
agents/differential_agent.py
AGENT 3 of 5: Differential Agent
Job: take the Detection Agent's findings and ask Google Gemini (FREE tier)
to produce a ranked DIFFERENTIAL DIAGNOSIS — i.e. "given these findings,
what are the most likely conditions, ranked by probability, with reasoning."

Get a free Gemini API key at: https://aistudio.google.com/app/apikey
"""
import json
from google import genai
from google.genai import types
from config import GEMINI_API_KEY
from agents.pipeline_state import set_status

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """You are a differential diagnosis assistant supporting a radiologist.
Given a list of imaging findings, return ONLY valid JSON (no markdown, no preamble) as a list of objects:
[{"diagnosis": "...", "probability": 0.0-1.0, "reasoning": "one sentence"}]
Order by probability, highest first. Include 2-4 differentials. This is decision support only,
not a final diagnosis — a licensed radiologist must confirm."""


def rank_differentials(findings: list[dict]) -> list[dict]:
    set_status("Differential Agent", "active", "Ranking possible diagnoses...")

    findings_text = "\n".join(
        f"- {f['label']} (confidence: {f['confidence']:.2f}, location: {f.get('location', 'N/A')})"
        for f in findings
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Findings:\n{findings_text}",
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        )
        raw_text = response.text.strip()
        raw_text = raw_text.replace("```json", "").replace("```", "").strip()
        differentials = json.loads(raw_text)

        set_status("Differential Agent", "done", f"Ranked {len(differentials)} differential(s)")
        return differentials

    except (json.JSONDecodeError, IndexError, Exception) as e:
        set_status("Differential Agent", "error", f"Failed to rank differentials: {e}")
        return [{"diagnosis": "Unable to generate differential", "probability": 0.0, "reasoning": str(e)}]
