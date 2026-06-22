"""
config.py
Loads all API keys and settings from the .env file.
Every other file imports keys FROM HERE — never read os.getenv() elsewhere.
"""
import os
from dotenv import load_dotenv

# load_dotenv disabled for render


def _strip_quotes(value: str) -> str:
    value = (value or "").strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def _load_gemini_keys() -> list[str]:
    keys: list[str] = []
    for i in range(1, 4):
        key = _strip_quotes(os.getenv(f"GEMINI_API_KEY_{i}", ""))
        if key and key not in keys:
            keys.append(key)

    if keys:
        return keys

    legacy = _strip_quotes(os.getenv("GEMINI_API_KEY", ""))
    if legacy:
        keys.append(legacy)

    combined = _strip_quotes(os.getenv("GEMINI_API_KEYS", ""))
    if combined:
        for key in combined.split(","):
            key = key.strip()
            if key and key not in keys:
                keys.append(key)

    return keys


def _key_valid(key: str) -> bool:
    return bool(key and len(key) > 10 and (key.startswith("AIza") or key.startswith("AQ")))


GEMINI_API_KEYS = _load_gemini_keys()
GEMINI_API_KEY = GEMINI_API_KEYS[0] if GEMINI_API_KEYS else ""
ROBOFLOW_API_KEY = _strip_quotes(os.getenv("ROBOFLOW_API_KEY", ""))
ROBOFLOW_MODEL_ID = _strip_quotes(os.getenv("ROBOFLOW_MODEL_ID", ""))
PUBMED_API_KEY = _strip_quotes(os.getenv("PUBMED_API_KEY", ""))
ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "http://localhost:5173")


def is_valid_gemini_key() -> bool:
    return any(_key_valid(k) for k in GEMINI_API_KEYS)


def check_keys():
    issues = []
    valid_keys = [k for k in GEMINI_API_KEYS if _key_valid(k)]
    if not valid_keys:
        issues.append("No valid Gemini keys — set GEMINI_API_KEY_1/2/3 in backend/.env")
    elif len(valid_keys) < len(GEMINI_API_KEYS):
        issues.append(f"Some Gemini keys look invalid ({len(valid_keys)}/{len(GEMINI_API_KEYS)} usable)")
    else:
        print(f"Gemini key rotation ready ({len(valid_keys)} keys loaded)")

    if not ROBOFLOW_API_KEY:
        issues.append("ROBOFLOW_API_KEY is missing")
    if not ROBOFLOW_MODEL_ID:
        issues.append("ROBOFLOW_MODEL_ID is missing")

    if issues:
        print("WARNING: API key issues in backend/.env:")
        for issue in issues:
            print(f"   - {issue}")
