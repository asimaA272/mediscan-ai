"""Shared Gemini helpers with automatic 3-key rotation (Key1 → Key2 → Key3 → Key1)."""
import base64
import threading

import requests

from config import GEMINI_API_KEYS

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"
_lock = threading.Lock()
_current_index = 0


class GeminiKeysExhaustedError(RuntimeError):
    """All configured Gemini keys failed (quota/auth)."""


def is_valid_gemini_key(key: str) -> bool:
    return bool(key and len(key) > 10 and (key.startswith("AIza") or key.startswith("AQ.")))


def has_gemini_keys() -> bool:
    return bool(_active_keys())


def _active_keys() -> list[str]:
    return [k for k in GEMINI_API_KEYS if is_valid_gemini_key(k)]


def _is_rotatable_error(status_code: int, body: str) -> bool:
    text = body.lower()
    if status_code in (401, 403, 429):
        return True
    return any(
        marker in text
        for marker in (
            "quota",
            "rate limit",
            "resource_exhausted",
            "limit exceeded",
            "unauthenticated",
            "permission denied",
        )
    )


def _extract_text(data: dict) -> str:
    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemini returned no candidates")
    parts = candidates[0].get("content", {}).get("parts") or []
    if not parts:
        raise RuntimeError("Gemini returned empty content")
    return parts[0].get("text", "").strip()


def _gemini_request(model: str, payload: dict) -> str:
    global _current_index
    keys = _active_keys()
    if not keys:
        raise ValueError(
            "No Gemini API keys configured — add GEMINI_API_KEY_1/2/3 to backend/.env"
        )

    last_error = None

    with _lock:
        start_index = _current_index

    for attempt in range(len(keys)):
        idx = (start_index + attempt) % len(keys)
        key = keys[idx]
        url = f"{GEMINI_BASE}/models/{model}:generateContent"

        try:
            resp = requests.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": key,
                },
                json=payload,
                timeout=90,
            )

            if resp.ok:
                with _lock:
                    _current_index = idx
                return _extract_text(resp.json())

            last_error = f"HTTP {resp.status_code}: {resp.text[:400]}"
            if _is_rotatable_error(resp.status_code, resp.text):
                continue
            resp.raise_for_status()

        except requests.RequestException as exc:
            last_error = str(exc)
            status = exc.response.status_code if exc.response is not None else 0
            body = exc.response.text if exc.response is not None else str(exc)
            if _is_rotatable_error(status, body):
                continue
            raise

    with _lock:
        _current_index = (start_index + 1) % len(keys)

    raise GeminiKeysExhaustedError(
        f"All {len(keys)} Gemini keys exhausted. Last error: {last_error}"
    )


def generate_text(system_prompt: str, user_prompt: str, model: str = "gemini-2.0-flash") -> str:
    payload = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
    }
    return _gemini_request(model, payload)


def analyze_image(
    system_prompt: str,
    image_base64: str,
    user_prompt: str,
    model: str = "gemini-2.0-flash",
) -> str:
    payload = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"inline_data": {"mime_type": "image/jpeg", "data": image_base64}},
                    {"text": user_prompt},
                ],
            }
        ],
    }
    return _gemini_request(model, payload)
