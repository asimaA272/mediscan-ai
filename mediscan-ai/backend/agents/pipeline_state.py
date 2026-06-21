"""
pipeline_state.py
Simple in-memory store tracking what each agent is doing right now.
No database — this resets every time the server restarts, which is fine
for a demo/project. The /api/pipeline/status endpoint reads from here.
"""
from datetime import datetime

AGENT_NAMES = [
    "Image Agent",
    "Detection Agent",
    "Differential Agent",
    "Evidence Agent",
    "Report Agent",
]

# Mutable in-memory dict — this IS the "database" for this project
_state = {
    name: {"status": "idle", "last_message": "Waiting for a scan...", "updated_at": str(datetime.now())}
    for name in AGENT_NAMES
}


def set_status(agent_name: str, status: str, message: str):
    """Update one agent's status. Called by the agents themselves as they work."""
    if agent_name not in _state:
        return
    _state[agent_name] = {
        "status": status,
        "last_message": message,
        "updated_at": str(datetime.now()),
    }


def get_all_status():
    """Returns the current status of every agent, for the frontend pipeline page."""
    return [
        {"agent_name": name, **info}
        for name, info in _state.items()
    ]


def reset_all():
    """Reset every agent back to idle — called at the start of a new scan."""
    for name in AGENT_NAMES:
        set_status(name, "idle", "Waiting for a scan...")
