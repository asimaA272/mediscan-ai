"""
schemas.py
All Pydantic models (request/response shapes) live here so routers
and agents can import the same definitions without circular imports.
"""
from pydantic import BaseModel
from typing import List, Optional


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


class Finding(BaseModel):
    label: str
    confidence: float
    location: Optional[str] = None


class DifferentialItem(BaseModel):
    diagnosis: str
    probability: float
    reasoning: str


class EvidenceItem(BaseModel):
    diagnosis: str
    citation: str
    url: Optional[str] = None


class ScanResult(BaseModel):
    scan_id: str
    filename: str
    findings: List[Finding]
    differentials: List[DifferentialItem]
    evidence: List[EvidenceItem]
    report: str


class PipelineStatus(BaseModel):
    agent_name: str
    status: str  # "idle" | "active" | "busy" | "done" | "error"
    last_message: str
