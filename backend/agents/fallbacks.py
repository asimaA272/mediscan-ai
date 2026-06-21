"""Local fallback outputs when external APIs are unavailable or keys are invalid."""


def demo_findings() -> list[dict]:
    return [
        {"label": "Hazy opacity, right lower lobe", "confidence": 0.72, "location": "x:420, y:380"},
        {"label": "Mild interstitial markings", "confidence": 0.55, "location": "bilateral bases"},
    ]


def demo_differentials(findings: list[dict]) -> list[dict]:
    labels = ", ".join(f["label"] for f in findings if f.get("confidence", 0) > 0)
    context = labels or "non-specific chest X-ray findings"
    return [
        {
            "diagnosis": "Community-acquired pneumonia",
            "probability": 0.68,
            "reasoning": f"Lower-lobe opacity pattern ({context}) is most consistent with infectious consolidation.",
        },
        {
            "diagnosis": "Atelectasis",
            "probability": 0.42,
            "reasoning": "Plate-like or basilar opacity can reflect subsegmental collapse rather than infection.",
        },
        {
            "diagnosis": "Pulmonary edema",
            "probability": 0.28,
            "reasoning": "Interstitial markings raise fluid overload or heart failure in the differential.",
        },
    ]


def demo_report(findings: list[dict], differentials: list[dict], evidence: list[dict]) -> str:
    findings_text = "\n".join(f"- {f['label']} ({f['confidence']:.0%})" for f in findings)
    diff_text = "\n".join(
        f"- {d['diagnosis']} ({d['probability']:.0%}): {d['reasoning']}" for d in differentials
    )
    evidence_text = "\n".join(
        f"- {e.get('diagnosis', 'Reference')}: {e.get('citation', 'See PubMed')}" for e in evidence
    ) or "- Supporting literature retrieved from PubMed where available."

    return f"""FINDINGS:
{findings_text}

IMPRESSION:
{diff_text}

RECOMMENDATION:
Correlate clinically. Consider follow-up chest imaging in 4–6 weeks if symptoms persist, or earlier if the patient deteriorates. Pulmonary consultation may be warranted for unresolved opacity.

Supporting literature:
{evidence_text}

This report was AI-assisted and requires review by a licensed radiologist before clinical use."""
