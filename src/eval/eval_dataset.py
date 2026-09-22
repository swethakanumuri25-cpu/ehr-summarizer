CASES = [
    {
        "name": "normal_case",
        "patient_json": {
            "patient_id": "EVAL001",
            "age": 34,
            "gender": "Male",
            "chief_complaint": "Annual physical, no acute complaints",
            "diagnoses": ["Seasonal allergic rhinitis"],
            "medications": ["Cetirizine 10 mg as needed"],
            "allergies": [],
            "vitals": {
                "blood_pressure": "118/76",
                "heart_rate": 68,
                "temperature": "98.4 F"
            },
            "assessment": "Healthy adult male, routine exam, no concerns."
        },
        "specialty": "primary care",
        "mode": "clinician",
        "must_preserve": {
            "diagnoses": ["Seasonal allergic rhinitis"],
            "medications": ["Cetirizine"],
            "allergies": []
        },
        "distractor_terms": ["diabetes", "hypertension", "penicillin"]
    },

    {
        "name": "medication_allergy_conflict",
        "patient_json": {
            "patient_id": "EVAL002",
            "age": 58,
            "gender": "Female",
            "chief_complaint": "Sinus infection",
            "diagnoses": ["Acute sinusitis"],
            "medications": ["Amoxicillin 500 mg three times daily"],
            "allergies": ["Penicillin"],
            "vitals": {
                "blood_pressure": "130/85",
                "heart_rate": 82,
                "temperature": "99.9 F"
            },
            "assessment": "Prescribed amoxicillin despite documented penicillin allergy -- flag for review."
        },
        "specialty": "primary care",
        "mode": "clinician",
        "must_preserve": {
            "diagnoses": ["Acute sinusitis"],
            "medications": ["Amoxicillin"],
            "allergies": ["Penicillin"]
        },
        "distractor_terms": ["diabetes", "asthma"]
    },

    {
        "name": "missing_information",
        "patient_json": {
            "patient_id": "EVAL003",
            "age": 27,
            "gender": "Non-binary",
            "chief_complaint": "Follow-up visit",
            "diagnoses": [],
            "medications": [],
            "allergies": []
        },
        "specialty": "primary care",
        "mode": "patient",
        "must_preserve": {
            "diagnoses": [],
            "medications": [],
            "allergies": []
        },
        "distractor_terms": [
            "hypertension",
            "diabetes",
            "penicillin",
            "asthma"
        ]
    },

    {
        "name": "multiple_diagnoses",
        "patient_json": {
            "patient_id": "EVAL004",
            "age": 67,
            "gender": "Male",
            "chief_complaint": "Fatigue, shortness of breath, joint pain",
            "diagnoses": [
                "Type 2 diabetes mellitus",
                "Congestive heart failure",
                "Osteoarthritis"
            ],
            "medications": [
                "Metformin 1000 mg twice daily",
                "Furosemide 40 mg daily",
                "Acetaminophen as needed"
            ],
            "allergies": ["Sulfa drugs"],
            "vitals": {
                "blood_pressure": "142/90",
                "heart_rate": 88,
                "temperature": "98.2 F"
            },
            "lab_results": {
                "a1c": "8.1%",
                "bnp": "450 pg/mL"
            },
            "assessment": "Multiple chronic conditions, mild volume overload noted on exam."
        },
        "specialty": "cardiology",
        "mode": "clinician",
        "must_preserve": {
            "diagnoses": [
                "Type 2 diabetes mellitus",
                "Congestive heart failure",
                "Osteoarthritis"
            ],
            "medications": [
                "Metformin",
                "Furosemide",
                "Acetaminophen"
            ],
            "allergies": ["Sulfa"]
        },
        "distractor_terms": ["penicillin", "asthma", "stroke"]
    },

    {
        "name": "clinician_vs_patient_mode",
        "patient_json": {
            "patient_id": "EVAL005",
            "age": 45,
            "gender": "Female",
            "chief_complaint": "Fatigue and occasional dizziness",
            "diagnoses": ["Hypertension", "Iron deficiency anemia"],
            "medications": [
                "Lisinopril 10 mg daily",
                "Ferrous sulfate 325 mg daily"
            ],
            "allergies": ["Penicillin"],
            "vitals": {
                "blood_pressure": "138/88",
                "heart_rate": 78,
                "temperature": "98.6 F"
            },
            "lab_results": {
                "hemoglobin": "10.8 g/dL",
                "ferritin": "12 ng/mL"
            },
            "assessment": "Fatigue likely associated with iron deficiency. Blood pressure remains mildly elevated."
        },
        "specialty": "primary care",
        "mode": "patient",
        "must_preserve": {
            "diagnoses": ["Hypertension", "Iron deficiency anemia"],
            "medications": ["Lisinopril", "Ferrous sulfate"],
            "allergies": ["Penicillin"]
        },
        "distractor_terms": ["diabetes", "asthma", "stroke"]
    },

    {
        "name": "pediatric_case",
        "patient_json": {
            "patient_id": "EVAL006",
            "age": 7,
            "gender": "Male",
            "chief_complaint": "Recurring ear pain",
            "diagnoses": ["Acute otitis media"],
            "medications": ["Amoxicillin 250 mg twice daily"],
            "allergies": [],
            "vitals": {
                "temperature": "100.9 F"
            },
            "assessment": "Right ear erythema and bulging tympanic membrane, consistent with acute otitis media."
        },
        "specialty": "pediatrics",
        "mode": "patient",
        "must_preserve": {
            "diagnoses": ["Acute otitis media"],
            "medications": ["Amoxicillin"],
            "allergies": []
        },
        "distractor_terms": ["penicillin", "asthma", "diabetes"]
    },

    {
        "name": "oncology_multiple_meds",
        "patient_json": {
            "patient_id": "EVAL007",
            "age": 61,
            "gender": "Female",
            "chief_complaint": "Follow-up after chemotherapy cycle 3",
            "diagnoses": [
                "Stage II breast cancer",
                "Chemotherapy-induced nausea"
            ],
            "medications": [
                "Paclitaxel per protocol",
                "Ondansetron 8 mg as needed",
                "Dexamethasone 4 mg daily"
            ],
            "allergies": ["Latex"],
            "vitals": {
                "blood_pressure": "112/70",
                "heart_rate": 74,
                "temperature": "98.1 F"
            },
            "assessment": "Tolerating chemotherapy with manageable nausea; no signs of infection."
        },
        "specialty": "oncology",
        "mode": "clinician",
        "must_preserve": {
            "diagnoses": [
                "Stage II breast cancer",
                "Chemotherapy-induced nausea"
            ],
            "medications": [
                "Paclitaxel",
                "Ondansetron",
                "Dexamethasone"
            ],
            "allergies": ["Latex"]
        },
        "distractor_terms": [
            "penicillin",
            "diabetes",
            "stage III",
            "metastatic"
        ]
    },

    {
        "name": "cardiology_no_allergy",
        "patient_json": {
            "patient_id": "EVAL008",
            "age": 72,
            "gender": "Male",
            "chief_complaint": "Chest tightness on exertion",
            "diagnoses": ["Stable angina", "Hyperlipidemia"],
            "medications": [
                "Atorvastatin 40 mg daily",
                "Nitroglycerin as needed"
            ],
            "allergies": [],
            "vitals": {
                "blood_pressure": "128/80",
                "heart_rate": 70
            },
            "lab_results": {
                "ldl": "142 mg/dL"
            },
            "assessment": "Symptoms consistent with stable angina; lipid panel elevated."
        },
        "specialty": "cardiology",
        "mode": "clinician",
        "must_preserve": {
            "diagnoses": ["Stable angina", "Hyperlipidemia"],
            "medications": ["Atorvastatin", "Nitroglycerin"],
            "allergies": []
        },
        "distractor_terms": [
            "penicillin",
            "diabetes",
            "unstable angina",
            "heart failure"
        ]
    },

    {
        "name": "elderly_polypharmacy",
        "patient_json": {
            "patient_id": "EVAL009",
            "age": 81,
            "gender": "Female",
            "chief_complaint": "Routine geriatric wellness visit",
            "diagnoses": [
                "Osteoporosis",
                "Chronic kidney disease stage 3",
                "Atrial fibrillation"
            ],
            "medications": [
                "Alendronate 70 mg weekly",
                "Apixaban 5 mg twice daily",
                "Calcium/Vitamin D supplement"
            ],
            "allergies": ["Sulfa drugs", "Shellfish"],
            "vitals": {
                "blood_pressure": "132/78",
                "heart_rate": 66
            },
            "assessment": "Stable on current regimen; renal function monitored quarterly."
        },
        "specialty": "primary care",
        "mode": "clinician",
        "must_preserve": {
            "diagnoses": [
                "Osteoporosis",
                "Chronic kidney disease",
                "Atrial fibrillation"
            ],
            "medications": [
                "Alendronate",
                "Apixaban"
            ],
            "allergies": ["Sulfa", "Shellfish"]
        },
        "distractor_terms": [
            "penicillin",
            "stage 4",
            "stage 5",
            "dialysis"
        ]
    }
]