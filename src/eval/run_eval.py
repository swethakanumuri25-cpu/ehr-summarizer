"""
Evaluation harness for the EHR summarizer.

Run this from the project root (same folder as requirements.txt) with:

    python -m src.eval.run_eval

It calls pipeline.summarize() directly (no HTTP round trip needed) for
each case in eval_dataset.py, checks whether required facts survived
into the generated summary, checks whether any "distractor" term leaked
in (a sign of invented information), and prints + saves a metrics report.

IMPORTANT: if GROQ_API_KEY is not set (or the LLM call fails for any
reason), pipeline.summarize() silently falls back to the deterministic,
rule-based summary. That fallback just echoes the structured fields
directly, so it will score artificially close to 100% on every metric
here -- it is not a meaningful test of LLM summarization quality.
This script detects and reports which mode was actually used for each
case so you don't mistake fallback-mode numbers for real LLM results.
"""

"""
Evaluation harness for the EHR summarizer.

For the small hand-written 9-case set:
    python -m src.eval.run_eval

For a large generated set (build it first with generate_cases.py):
    python -m src.eval.generate_cases --n 500
    python -m src.eval.run_eval --dataset src/eval/eval_cases_large.json

It calls pipeline.summarize() directly (no HTTP round trip needed) for
each case, checks whether required facts survived into the generated
summary, checks whether any "distractor" term leaked in (a sign of
invented information), and prints + saves a metrics report.

For large runs, each case retries a couple of times with backoff if the
LLM call fails (e.g. Groq rate limiting), and progress prints every 25
cases so a 500-case run doesn't look hung.

IMPORTANT: if GROQ_API_KEY is not set (or the LLM call fails on every
retry), pipeline.summarize() silently falls back to the deterministic,
rule-based summary. That fallback just echoes the structured fields
directly, so it will score artificially close to 100% on every metric
here -- it is not a meaningful test of LLM summarization quality.
This script detects and reports which mode was actually used for each
case so you don't mistake fallback-mode numbers for real LLM results.
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.model.pipeline import summarize
from src.eval.eval_dataset import CASES as DEFAULT_CASES


def _contains(summary: str, term: str) -> bool:
    return term.lower() in summary.lower()


def evaluate_case(case: dict, retries: int = 2, retry_delay: float = 3.0) -> dict:
    result = None
    for attempt in range(retries + 1):
        result = summarize(case["patient_json"], case["specialty"], case["mode"])
        issues = result.get("issues", [])
        used_fallback = any("fallback" in str(i).lower() for i in issues) or \
            "fallback" in result.get("summary", "").lower()
        if not used_fallback or attempt == retries:
            break
        time.sleep(retry_delay)  # likely a transient rate-limit; back off and retry

    summary = result.get("summary", "")
    issues = result.get("issues", [])
    used_fallback = any("fallback" in str(i).lower() for i in issues) or \
        "fallback" in summary.lower()

    def preservation_rate(field):
        terms = case["must_preserve"].get(field, [])
        if not terms:
            return None  # no ground truth for this field in this case
        hits = sum(1 for t in terms if _contains(summary, t))
        return hits / len(terms)

    diag_rate = preservation_rate("diagnoses")
    med_rate = preservation_rate("medications")
    allergy_rate = preservation_rate("allergies")

    distractors_present = [t for t in case["distractor_terms"] if _contains(summary, t)]
    hallucination_rate = len(distractors_present) / len(case["distractor_terms"]) \
        if case["distractor_terms"] else 0.0

    return {
        "case": case["name"],
        "mode_used": "fallback (rule-based)" if used_fallback else "llm",
        "diagnosis_preservation": diag_rate,
        "medication_preservation": med_rate,
        "allergy_preservation": allergy_rate,
        "unsupported_info_rate": hallucination_rate,
        "distractor_terms_leaked": distractors_present,
        "issues_flagged": issues,
        "summary": summary,
    }


def _avg(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def _load_cases(dataset_arg: str | None):
    if not dataset_arg:
        return DEFAULT_CASES
    path = Path(dataset_arg)
    if not path.is_absolute():
        path = Path.cwd() / dataset_arg
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset", type=str, default=None,
        help="Path to a generated eval_cases_large.json. Defaults to the "
             "9-case hand-written set in eval_dataset.py."
    )
    parser.add_argument(
        "--sleep", type=float, default=0.0,
        help="Seconds to sleep between cases (helps avoid rate limits on large runs)."
    )
    args = parser.parse_args()

    cases = _load_cases(args.dataset)
    total = len(cases)
    results = []

    for i, c in enumerate(cases, start=1):
        results.append(evaluate_case(c))
        if total > 25 and i % 25 == 0:
            print(f"  ...evaluated {i}/{total} cases")
        if args.sleep:
            time.sleep(args.sleep)

    any_llm = any(r["mode_used"] == "llm" for r in results)
    any_fallback = any(r["mode_used"] != "llm" for r in results)

    print("=" * 70)
    print("EHR SUMMARIZER -- EVALUATION REPORT")
    print("=" * 70)

    if any_fallback:
        n_fallback = sum(1 for r in results if r["mode_used"] != "llm")
        print(
            f"\n⚠ WARNING: {n_fallback}/{total} case(s) ran on the RULE-BASED\n"
            "  FALLBACK, not the LLM (no GROQ_API_KEY, rate limiting, or the\n"
            "  LLM call failed on every retry). Fallback scores are not\n"
            "  representative of real LLM summarization quality.\n"
        )
    if any_llm:
        n_llm = sum(1 for r in results if r["mode_used"] == "llm")
        print(f"✓ {n_llm}/{total} case(s) ran on the live LLM.\n")

    # Per-case detail is skipped for large runs to keep the terminal readable;
    # full detail is always in eval_results.json.
    if total <= 25:
        for r in results:
            print(f"\n--- {r['case']} ({r['mode_used']}) ---")
            print(f"  Diagnosis preservation:  {_fmt(r['diagnosis_preservation'])}")
            print(f"  Medication preservation: {_fmt(r['medication_preservation'])}")
            print(f"  Allergy preservation:    {_fmt(r['allergy_preservation'])}")
            print(f"  Unsupported-info rate:   {_fmt(r['unsupported_info_rate'])}")
            if r["distractor_terms_leaked"]:
                print(f"  ⚠ Leaked distractor terms: {r['distractor_terms_leaked']}")
            if r["issues_flagged"]:
                print(f"  Issues flagged by app: {r['issues_flagged']}")

    print("\n" + "=" * 70)
    print("AGGREGATE (across all cases with ground truth for that field)")
    print("=" * 70)
    diag_avg = _avg([r["diagnosis_preservation"] for r in results])
    med_avg = _avg([r["medication_preservation"] for r in results])
    allergy_avg = _avg([r["allergy_preservation"] for r in results])
    halluc_avg = _avg([r["unsupported_info_rate"] for r in results])
    coverage_avg = _avg([v for v in (diag_avg, med_avg, allergy_avg) if v is not None])

    print(f"  Diagnosis preservation:      {_fmt(diag_avg)}")
    print(f"  Medication preservation:     {_fmt(med_avg)}")
    print(f"  Allergy preservation:        {_fmt(allergy_avg)}")
    print(f"  Key-field coverage (avg):    {_fmt(coverage_avg)}")
    print(f"  Hallucination rate:          {_fmt(halluc_avg)}")
    print(f"\n  n = {total} synthetic cases")
    print(
        "\n  NOTE: 'Factual consistency' (subtle distortions, tone, correct\n"
        "  clinical framing) is NOT measured here -- this harness only checks\n"
        "  keyword presence/absence. Don't report a 'factual consistency %'\n"
        "  based on this script alone; it would need a human or LLM-judge\n"
        "  review of each summary to claim that honestly."
    )

    out_path = Path(__file__).with_name("eval_results.json")
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nFull results written to {out_path}")


def _fmt(v):
    if v is None:
        return "n/a (no ground truth for this field)"
    return f"{v * 100:.1f}%"


if __name__ == "__main__":
    main()