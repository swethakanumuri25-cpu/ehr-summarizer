from typing import Dict, List, Union


def _desc(item: Union[Dict, str]) -> str:
    """Return a display string for either a plain string or Synthea-style dict."""
    if isinstance(item, dict):
        return item.get("DESCRIPTION", "")
    return str(item)


def build_context(patient_json: Dict) -> Dict:
    labs = sorted(
        patient_json.get("observations", []),
        key=lambda x: str(x.get("DATE", "")) if isinstance(x, dict) else ""
    )[-5:]

    meds = patient_json.get("medications", [])[:10]

    probs = (
        patient_json.get("problems")
        or patient_json.get("diagnoses")
        or []
    )[:10]

    encs = patient_json.get("encounters", [])[-5:]

    return {
        "labs": labs,
        "meds": meds,
        "problems": probs,
        "encounters": encs,
    }


def rule_checks(summary: str, patient_json: Dict) -> List[str]:
    issues = []

    allergies = [
        _desc(a).lower()
        for a in patient_json.get("allergies", [])
    ]

    if (
        any("penicillin" in a for a in allergies)
        and "penicillin" in summary.lower()
    ):
        issues.append(
            "⚠ Mentions penicillin despite recorded allergy."
        )

    return issues


def rule_based_summary(
    patient_json: Dict,
    specialty: str,
    mode: str
) -> str:

    ctx = build_context(patient_json)

    problems = ", ".join(
        {_desc(p) for p in ctx["problems"] if _desc(p)}
    ) or "None"

    meds = ", ".join(
        {_desc(m) for m in ctx["meds"] if _desc(m)}
    ) or "None"

    tone = (
        "clinical tone"
        if mode == "clinician"
        else "patient-friendly tone"
    )

    return (
        f"Specialty: {specialty}\n"
        f"Problems: {problems}\n"
        f"Meds: {meds}\n"
        f"Mode: {tone}\n"
        "Summary generated from structured fields."
    )


def summarize(
    patient_json: Dict,
    specialty: str = "primary care",
    mode: str = "clinician"
) -> Dict:

    # Always keep the rule-based version available as a fallback.
    fallback = rule_based_summary(
        patient_json,
        specialty,
        mode
    )

    issues = []

    # Try the LLM first.
    try:
        from src.model.llm import generate_summary

        llm_summary = generate_summary(
            patient_json=patient_json,
            specialty=specialty,
            mode=mode
        )

        if llm_summary and llm_summary.strip():
            summary = llm_summary.strip()
        else:
            summary = fallback
            issues.append(
                "⚠ AI summary unavailable; using structured fallback."
            )

    except Exception as e:
        summary = fallback

        issues.append(
            f"⚠ AI summary unavailable; using structured fallback. ({str(e)})"
        )

    # Run safety/rule checks on whichever summary was produced.
    issues.extend(
        rule_checks(summary, patient_json)
    )

    return {
        "summary": summary,
        "citations": [],
        "timeline": [],
        "issues": issues,
    }