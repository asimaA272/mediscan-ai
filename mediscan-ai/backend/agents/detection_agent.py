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
import os
import tempfile
import base64
from inference_sdk import InferenceHTTPClient
from config import ROBOFLOW_API_KEY, ROBOFLOW_MODEL_ID
from agents.pipeline_state import set_status

ROBOFLOW_API_URL = "https://serverless.roboflow.com"

_client = None


def _get_client():
    """Lazily create the Roboflow client (only once the keys are confirmed present)."""
    global _client
    if _client is None:
        _client = InferenceHTTPClient(api_url=ROBOFLOW_API_URL, api_key=ROBOFLOW_API_KEY)
    return _client


def detect_anomalies(image_base64: str) -> list[dict]:
    """
    Calls Roboflow's hosted inference API with a pre-trained chest X-ray model.
    Returns: [{"label": "...", "confidence": 0.0-1.0, "location": "..."}]
    """
    set_status("Detection Agent", "active", "Sending image to Roboflow model...")

    if not ROBOFLOW_API_KEY or not ROBOFLOW_MODEL_ID:
        set_status("Detection Agent", "error", "ROBOFLOW_API_KEY or ROBOFLOW_MODEL_ID missing in .env")
        return _fallback_findings()

    temp_path = None
    try:
        # inference-sdk expects a file path or PIL image, so we write the
        # base64 image to a temporary JPEG file first.
        image_bytes = base64.b64decode(image_base64)
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp.write(image_bytes)
            temp_path = tmp.name

        client = _get_client()
        result = client.infer(temp_path, model_id=ROBOFLOW_MODEL_ID)

        findings = _parse_roboflow_response(result)
        set_status("Detection Agent", "done", f"Detected {len(findings)} finding(s)")
        return findings

    except Exception as e:
        set_status("Detection Agent", "error", f"Roboflow API call failed: {e}")
        return _fallback_findings()

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def _parse_roboflow_response(data: dict) -> list[dict]:
    """
    Converts Roboflow's raw response into our standard finding format.
    Roboflow object-detection models return a "predictions" list, each with
    "class" (label), "confidence" (0-1), and bounding box coordinates (x, y).
    """
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
    return findings if findings else _fallback_findings()


def _fallback_findings() -> list[dict]:
    """Used only if the Roboflow keys are missing or the call fails, so the
    pipeline can still demo end-to-end without crashing."""
    return [
        {"label": "Unable to reach detection model", "confidence": 0.0, "location": "N/A"}
    ]
