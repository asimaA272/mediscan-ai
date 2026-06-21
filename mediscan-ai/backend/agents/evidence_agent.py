"""
agents/evidence_agent.py
AGENT 4 of 5: Evidence Agent
Job: for each candidate diagnosis, search PubMed (NCBI E-utilities API)
and return a real citation supporting/discussing that condition.
"""
import requests
from config import PUBMED_API_KEY
from agents.pipeline_state import set_status

PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"


def gather_evidence(differentials: list[dict]) -> list[dict]:
    set_status("Evidence Agent", "active", "Searching PubMed for supporting literature...")

    evidence = []
    for item in differentials:
        diagnosis = item.get("diagnosis", "")
        try:
            citation = _search_pubmed(diagnosis)
            evidence.append(citation)
        except requests.exceptions.RequestException as e:
            evidence.append({
                "diagnosis": diagnosis,
                "citation": f"Could not retrieve literature ({e})",
                "url": None,
            })

    set_status("Evidence Agent", "done", f"Gathered evidence for {len(evidence)} diagnosis/diagnoses")
    return evidence


def _search_pubmed(diagnosis: str) -> dict:
    """Searches PubMed for one diagnosis, returns the top article as a citation."""
    params = {
        "db": "pubmed",
        "term": diagnosis,
        "retmax": 1,
        "sort": "relevance",
        "retmode": "json",
    }
    if PUBMED_API_KEY:
        params["api_key"] = PUBMED_API_KEY

    search_resp = requests.get(PUBMED_SEARCH_URL, params=params, timeout=15)
    search_resp.raise_for_status()
    ids = search_resp.json().get("esearchresult", {}).get("idlist", [])

    if not ids:
        return {"diagnosis": diagnosis, "citation": "No PubMed articles found", "url": None}

    pmid = ids[0]
    summary_resp = requests.get(
        PUBMED_SUMMARY_URL,
        params={"db": "pubmed", "id": pmid, "retmode": "json"},
        timeout=15,
    )
    summary_resp.raise_for_status()
    summary_data = summary_resp.json().get("result", {}).get(pmid, {})
    title = summary_data.get("title", "Untitled article")

    return {
        "diagnosis": diagnosis,
        "citation": title,
        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
    }
