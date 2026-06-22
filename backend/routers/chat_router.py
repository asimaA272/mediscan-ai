"""
routers/chat_router.py
Endpoint: POST /api/chat
Powers the AI Chat page — answers medical/X-ray questions using Google
Gemini (FREE tier), and also returns a simple detected "emotion" label
based on the message, which the frontend displays in the top-right
mood indicator.
"""
from fastapi import APIRouter, HTTPException
from config import is_valid_gemini_key
from schemas import ChatRequest, ChatResponse
from agents import gemini_utils
from agents.gemini_utils import GeminiKeysExhaustedError

router = APIRouter()

SYSTEM_PROMPT = """You are MediScan AI, a friendly but professional medical imaging
assistant. You answer questions about X-rays, diseases, and radiology findings in
clear, simple language a patient or student can understand. You are NOT a substitute
for a real doctor — if a question sounds like a personal medical emergency or a request
for a diagnosis of a specific person, gently remind them to see a licensed physician.
Keep answers concise (under 150 words) unless asked for more detail."""

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

    if not is_valid_gemini_key():
        return ChatResponse(
            reply=(
                "The AI assistant isn't configured yet. "
                "Please contact the administrator to set up the service."
            )
        )

    try:
        reply = gemini_utils.generate_text(SYSTEM_PROMPT, req.message)
        return ChatResponse(reply=reply)
    except GeminiKeysExhaustedError:
        return ChatResponse(
            reply=(
                "I'm getting a lot of requests right now and have hit my usage limit. "
                "Please wait a few minutes and try again."
            )
        )
    except Exception:
        return ChatResponse(
            reply="Sorry, I ran into a problem answering that. Please try again in a moment."
        )


@router.get("/chat/emotion")
def detect_emotion(message: str):
    lower_msg = message.lower()
    for emotion, keywords in EMOTION_KEYWORDS.items():
        if any(keyword in lower_msg for keyword in keywords):
            return {"emotion": emotion}
    return {"emotion": "Neutral"}