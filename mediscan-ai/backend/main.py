"""
main.py
THIS IS THE FILE YOU RUN: uvicorn main:app --reload
Sets up the FastAPI app, CORS (so the React frontend can call it), and
plugs in all 3 routers (scan, chat, pipeline).
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import check_keys, ALLOWED_ORIGIN
from routers import scan_router, chat_router, pipeline_router

check_keys()

app = FastAPI(title="MediScan AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan_router.router, prefix="/api", tags=["scan"])
app.include_router(chat_router.router, prefix="/api", tags=["chat"])
app.include_router(pipeline_router.router, prefix="/api", tags=["pipeline"])


@app.get("/")
def root():
    return {"message": "MediScan AI backend is running. See /docs for API documentation."}


@app.get("/health")
def health():
    return {"status": "ok"}
