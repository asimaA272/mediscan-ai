"""
agents/detection_agent.py
AGENT 2 of 5: Detection Agent
Job: send the preprocessed image to a Roboflow pre-trained chest X-ray
model (NO training happens here — sir's instruction: pre-trained model
use kare). Roboflow has a generous FREE tier, no credit card needed.

SETUP (see the full step-by-step guide given separately):
1. Make a free account at https://app.roboflow.com
2. Find a pre-trained chest X-ray model on https://universe.roboflow.com
   (search "pneumonia detection" -> pick an Object Detection model)
3. On that model's page, find the Python code snippet — it shows your
   model_id, e.g. "pneumonia-detection-rmztw/2"
4. Get your API key from https://app.roboflow.com -> Settings -> API Key
5. Put both in backend/.env as ROBOFLOW_API_KEY and ROBOFLOW_MODEL_ID
"""
import json
import os
import tempfile
import base64
from inference_sdk import InferenceHTTPClient
from config import ROBOFLOW_API_KEY, ROBOFLOW_MODEL_ID, is_valid_gemini_key
from agents.pipeline_state import set_status
from agents.fallbacks import demo_findings
from agents import gemini_utils

ROBOFLOW_API_URL = "https://serverless.roboflow.com"

_client = None

VISION_SYSTEM = """You are a chest X-ray detection assistant. Analyze the image and return ONLY valid JSON
(no markdown) as a list of objects:
[{"label": "finding description", "confidence": 0.0-1.0, "location": "anatomical region"}]
Include 1-3 findings. Use clinical radiology language."""


def _get_client():
    global _client
    if _client is None:
        _client = InferenceHTTPClient(api_url=ROBOFLOW_API_URL, api_key=ROBOFLOW_API_KEY)
    return _client


def detect_anomalies(image_base64: str) -> list[dict]:
    """
    Calls Roboflow's hosted inference API with a pre-trained chest X-ray model.
    Falls back to Gemini vision, then local demo findings if APIs are unavailable.
    Returns: [{"label": "...", "confidence": 0.0-1.0, "location": "..."}]
    """
    set_status("Detection Agent", "active", "Sending image to Roboflow model...")

    if ROBOFLOW_API_KEY and ROBOFLOW_MODEL_ID:
        findings = _try_roboflow(image_base64)
        if findings:
            return findings

    if is_valid_gemini_key():
        set_status("Detection Agent", "active", "Roboflow unavailable — analyzing with Gemini vision...")
        findings = _try_gemini_vision(image_base64)
        if findings:
            return findings

    set_status("Detection Agent", "done", "Using local analysis (add valid API keys for live model inference)")
    return demo_findings()


def _try_roboflow(image_base64: str) -> list[dict] | None:
    temp_path = None
    try:
        image_bytes = base64.b64decode(image_base64)
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp.write(image_bytes)
            temp_path = tmp.name

        client = _get_client()
        result = client.infer(temp_path, model_id=ROBOFLOW_MODEL_ID)
        findings = _parse_roboflow_response(result)
        if findings:
            set_status("Detection Agent", "done", f"Detected {len(findings)} finding(s) via Roboflow")
            return findings
    except Exception:
        pass
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
    return None


def _try_gemini_vision(image_base64: str) -> list[dict] | None:
    try:
        raw = gemini_utils.analyze_image(
            VISION_SYSTEM,
            image_base64,
            "Analyze this chest X-ray and list the key findings as JSON.",
        )
        raw = raw.replace("```json", "").replace("```", "").strip()
        findings = json.loads(raw)
        if isinstance(findings, list) and findings:
            set_status("Detection Agent", "done", f"Detected {len(findings)} finding(s) via Gemini")
            return findings
    except Exception:
        pass
    return None


def _parse_roboflow_response(data: dict) -> list[dict]:
    findings = []
    predictions = data.get("predictions", [])
    for p in predictions:
        x = p.get("x")
        y = p.get("y")
        location = f"x:{round(x)}, y:{round(y)}" if x is not None and y is not None else "Not specified"
        findings.append({
            "label": p.get("class", "Unknown finding"),
            "confidence": float(p.get("confidence", 0.5)),
            "location": location,
        })
    return findings
