"""
Generates a large pool of synthetic patient cases for the evaluation
harness, with ground truth (must_preserve / distractor_terms) derived
automatically from how each case was constructed -- so correctness of
the labels doesn't depend on hand-authoring hundreds of cases.

Run once to produce eval_cases_large.json:

    python -m src.eval.generate_cases --n 500

Then point run_eval.py at that file (see --dataset flag in run_eval.py).
"""

import argparse
import json
import random
from pathlib import Path

SPECIALTIES = ["primary care", "cardiology", "pediatrics", "oncology", "ED"]
MODES = ["clinician", "patient"]
GENDERS = ["Male", "Female", "Non-binary"]

# diagnosis -> (typical medications, typical specialty, plausible chief complaint)
CONDITIONS = {
    "Hypertension": (["Lisinopril 10 mg daily", "Amlodipine 5 mg daily"], "primary care", "Routine blood pressure check"),
    "Type 2 diabetes mellitus": (["Metformin 1000 mg twice daily", "Glipizide 5 mg daily"], "primary care", "Follow-up for blood sugar control"),
    "Iron deficiency anemia": (["Ferrous sulfate 325 mg daily"], "primary care", "Fatigue and occasional dizziness"),
    "Seasonal allergic rhinitis": (["Cetirizine 10 mg as needed"], "primary care", "Nasal congestion and sneezing"),
    "Acute sinusitis": (["Amoxicillin 500 mg three times daily"], "primary care", "Facial pressure and congestion"),
    "Congestive heart failure": (["Furosemide 40 mg daily", "Carvedilol 12.5 mg twice daily"], "cardiology", "Shortness of breath on exertion"),
    "Osteoarthritis": (["Acetaminophen as needed", "Naproxen 500 mg twice daily"], "primary care", "Joint pain and stiffness"),
    "Stable angina": (["Atorvastatin 40 mg daily", "Nitroglycerin as needed"], "cardiology", "Chest tightness on exertion"),
    "Hyperlipidemia": (["Atorvastatin 40 mg daily"], "cardiology", "Routine lipid panel follow-up"),
    "Acute otitis media": (["Amoxicillin 250 mg twice daily"], "pediatrics", "Ear pain and fever"),
    "Asthma": (["Albuterol inhaler as needed", "Fluticasone inhaler daily"], "pediatrics", "Wheezing and shortness of breath"),
    "Stage II breast cancer": (["Paclitaxel per protocol", "Ondansetron 8 mg as needed"], "oncology", "Follow-up after chemotherapy cycle"),
    "Osteoporosis": (["Alendronate 70 mg weekly", "Calcium/Vitamin D supplement"], "primary care", "Routine bone density follow-up"),
    "Chronic kidney disease stage 3": (["Losartan 50 mg daily"], "primary care", "Routine renal function follow-up"),
    "Atrial fibrillation": (["Apixaban 5 mg twice daily"], "cardiology", "Palpitations"),
    "Migraine": (["Sumatriptan 50 mg as needed"], "primary care", "Recurrent headaches"),
    "Depression": (["Sertraline 50 mg daily"], "primary care", "Low mood and fatigue"),
    "Generalized anxiety disorder": (["Escitalopram 10 mg daily"], "primary care", "Persistent worry and restlessness"),
    "Gastroesophageal reflux disease": (["Omeprazole 20 mg daily"], "primary care", "Heartburn after meals"),
    "Hypothyroidism": (["Levothyroxine 75 mcg daily"], "primary care", "Fatigue and weight gain"),
    "Acute appendicitis": (["Ceftriaxone 1 g IV", "Metronidazole 500 mg IV"], "ED", "Right lower quadrant abdominal pain"),
    "Community-acquired pneumonia": (["Azithromycin 500 mg daily"], "ED", "Cough and fever"),
    "Urinary tract infection": (["Nitrofurantoin 100 mg twice daily"], "primary care", "Burning with urination"),
    "Chronic obstructive pulmonary disease": (["Tiotropium inhaler daily", "Albuterol inhaler as needed"], "primary care", "Progressive shortness of breath"),
    "Rheumatoid arthritis": (["Methotrexate 15 mg weekly", "Folic acid 1 mg daily"], "primary care", "Joint swelling and morning stiffness"),
}

ALLERGY_POOL = ["Penicillin", "Sulfa drugs", "Latex", "Shellfish", "Peanuts", "Aspirin", "Codeine", "Iodine contrast"]

CONDITION_NAMES = list(CONDITIONS.keys())


def _drug_name(med_str: str) -> str:
    return med_str.split()[0]


def generate_case(rng: random.Random, idx: int) -> dict:
    n_dx = rng.choice([1, 1, 2, 2, 3])
    diagnoses = rng.sample(CONDITION_NAMES, n_dx)

    medications = []
    for dx in diagnoses:
        meds_for_dx, _, _ = CONDITIONS[dx]
        medications.append(rng.choice(meds_for_dx))

    n_allergies = rng.choice([0, 0, 1, 1, 2])
    allergies = rng.sample(ALLERGY_POOL, n_allergies)

    specialty = CONDITIONS[diagnoses[0]][1]
    chief_complaint = CONDITIONS[diagnoses[0]][2]
    mode = rng.choice(MODES)
    age = rng.randint(2, 95)
    gender = rng.choice(GENDERS)

    patient_json = {
        "patient_id": f"GEN{idx:04d}",
        "age": age,
        "gender": gender,
        "chief_complaint": chief_complaint,
        "diagnoses": diagnoses,
        "medications": medications,
        "allergies": allergies,
        "vitals": {
            "blood_pressure": f"{rng.randint(100,150)}/{rng.randint(60,95)}",
            "heart_rate": rng.randint(55, 100),
        },
        "assessment": f"Patient presents with {chief_complaint.lower()}, consistent with {diagnoses[0].lower()}."
    }

    # Distractors: sample condition/med/allergy names NOT used in this case.
    unused_conditions = [c for c in CONDITION_NAMES if c not in diagnoses]
    unused_allergies = [a for a in ALLERGY_POOL if a not in allergies]
    distractor_terms = rng.sample(unused_conditions, min(2, len(unused_conditions))) + \
        rng.sample(unused_allergies, min(1, len(unused_allergies)))

    return {
        "name": f"generated_{idx:04d}",
        "patient_json": patient_json,
        "specialty": specialty,
        "mode": mode,
        "must_preserve": {
            "diagnoses": diagnoses,
            "medications": [_drug_name(m) for m in medications],
            "allergies": allergies,
        },
        "distractor_terms": distractor_terms,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=str, default=None)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    cases = [generate_case(rng, i) for i in range(1, args.n + 1)]

    out_path = Path(args.out) if args.out else Path(__file__).with_name("eval_cases_large.json")
    out_path.write_text(json.dumps(cases, indent=2))
    print(f"Wrote {len(cases)} generated cases to {out_path}")


if __name__ == "__main__":
    main()