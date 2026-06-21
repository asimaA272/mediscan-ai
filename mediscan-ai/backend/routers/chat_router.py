"""
routers/chat_router.py
Endpoint: POST /api/chat
Powers the AI Chat page — answers medical/X-ray questions using Google
Gemini (FREE tier), and also returns a simple detected "emotion" label
based on the message, which the frontend displays in the top-right
mood indicator.
"""
from google import genai
from google.genai import types
from fastapi import APIRouter, HTTPException
from config import GEMINI_API_KEY
from schemas import ChatRequest, ChatResponse

router = APIRouter()
client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """You are MediScan AI, a friendly but professional medical imaging
assistant. You answer questions about X-rays, diseases, and radiology findings in
clear, simple language a patient or student can understand. You are NOT a substitute
for a real doctor — if a question sounds like a personal medical emergency or a request
for a diagnosis of a specific person, gently remind them to see a licensed physician.
Keep answers concise (under 150 words) unless asked for more detail."""

# Simple keyword-based emotion detector — lightweight, no extra API call needed.
EMOTION_KEYWORDS = {
    "Concerned": ["worried", "scared", "afraid", "pain", "hurts", "emergency", "serious"],
    "Curious": ["what is", "what does", "explain", "how does", "why", "curious", "mean"],
    "Satisfied": ["thanks", "thank you", "got it", "makes sense", "perfect", "great"],
    "Frustrated": ["not working", "confused", "doesn't make sense", "ugh", "stuck"],
}


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=req.message,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        )
        return ChatResponse(reply=response.text)

    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {e}")


@router.get("/chat/emotion")
def detect_emotion(message: str):
    """Lightweight emotion detection based on keywords in the message."""
    lower_msg = message.lower()
    for emotion, keywords in EMOTION_KEYWORDS.items():
        if any(keyword in lower_msg for keyword in keywords):
            return {"emotion": emotion}
    return {"emotion": "Neutral"}
