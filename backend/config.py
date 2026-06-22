import os

GEMINI_API_KEYS = []
for i in range(1, 4):
    key = os.getenv(f"GEMINI_API_KEY_{i}", "").strip()
    if key:
        GEMINI_API_KEYS.append(key)

legacy = os.getenv("GEMINI_API_KEY", "").strip()
if legacy and legacy not in GEMINI_API_KEYS:
    GEMINI_API_KEYS.append(legacy)

GEMINI_API_KEY = GEMINI_API_KEYS[0] if GEMINI_API_KEYS else ""
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "").strip()
ROBOFLOW_MODEL_ID = os.getenv("ROBOFLOW_MODEL_ID", "").strip()
PUBMED_API_KEY = os.getenv("PUBMED_API_KEY", "").strip()
ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "http://localhost:5173")

def is_valid_gemini_key():
    return len(GEMINI_API_KEYS) > 0

def check_keys():
    if GEMINI_API_KEYS:
        print(f"Gemini key rotation ready ({len(GEMINI_API_KEYS)} keys loaded)")
    else:
        print("WARNING: No Gemini keys found")
