"""
routers/pipeline_router.py
Endpoint: GET /api/pipeline/status
Returns the live status of all 5 agents (idle/active/busy/done/error) so
the frontend's "Multi-Agent Pipeline" page can show real-time updates
while a scan is being processed.
"""
from fastapi import APIRouter
from agents.pipeline_state import get_all_status

router = APIRouter()


@router.get("/pipeline/status")
def pipeline_status():
    return {"agents": get_all_status()}
