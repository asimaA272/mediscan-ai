"""
routers/scan_router.py
Endpoint: POST /api/scan
This is the MAIN pipeline endpoint. It receives an uploaded X-ray file and
runs it through all 5 agents in order:
  Image Agent -> Detection Agent -> Differential Agent -> Evidence Agent -> Report Agent
Returns one combined ScanResult.
"""
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException

from agents.image_agent import preprocess_scan
from agents.detection_agent import detect_anomalies
from agents.differential_agent import rank_differentials
from agents.evidence_agent import gather_evidence
from agents.report_agent import draft_report
from agents.pipeline_state import reset_all
from schemas import ScanResult

router = APIRouter()


@router.post("/scan", response_model=ScanResult)
async def run_scan_pipeline(file: UploadFile = File(...)):
    """
    Upload an X-ray (.dcm, .png, or .jpg) and run it through the full
    multi-agent diagnostic pipeline. Returns findings, differentials,
    evidence, and a drafted report.
    """
    reset_all()  # fresh status for this new scan

    allowed_extensions = (".dcm", ".png", ".jpg", ".jpeg")
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {allowed_extensions}")

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    # Agent 1: Image Agent
    image_base64 = preprocess_scan(file_bytes, file.filename)

    # Agent 2: Detection Agent
    findings = detect_anomalies(image_base64)

    # Agent 3: Differential Agent
    differentials = rank_differentials(findings)

    # Agent 4: Evidence Agent
    evidence = gather_evidence(differentials)

    # Agent 5: Report Agent
    report = draft_report(findings, differentials, evidence)

    return ScanResult(
        scan_id=str(uuid.uuid4()),
        filename=file.filename,
        findings=findings,
        differentials=differentials,
        evidence=evidence,
        report=report,
    )
