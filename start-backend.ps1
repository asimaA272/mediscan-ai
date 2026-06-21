# Run MediScan backend from project root (fixes "Could not import module main")
Set-Location "$PSScriptRoot\backend"
& ".\venv311\Scripts\Activate.ps1"
uvicorn main:app --reload
