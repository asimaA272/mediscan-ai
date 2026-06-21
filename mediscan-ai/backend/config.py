"""
config.py
Loads all API keys and settings from the .env file.
Every other file imports keys FROM HERE — never read os.getenv() elsewhere.

This project uses ONLY FREE APIs:
- Gemini (Google AI Studio) for chat, differential diagnosis, and report writing
- Roboflow (free tier) for the pre-trained chest X-ray detection model
- PubMed (NCBI E-utilities) for medical literature citations
"""
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "")
ROBOFLOW_MODEL_ID = os.getenv("ROBOFLOW_MODEL_ID", "")
PUBMED_API_KEY = os.getenv("PUBMED_API_KEY", "")
ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "http://localhost:5173")


# Fail loudly at startup if a required key is missing, instead of failing
# later inside a request (much easier to debug).
def check_keys():
    missing = []
    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")
    if not ROBOFLOW_API_KEY:
        missing.append("ROBOFLOW_API_KEY")
    if not ROBOFLOW_MODEL_ID:
        missing.append("ROBOFLOW_MODEL_ID")
    if missing:
        print(f"⚠️  WARNING: Missing keys in .env: {', '.join(missing)}")
        print("   Add them to backend/.env — the app will still start but those features will fail.")
