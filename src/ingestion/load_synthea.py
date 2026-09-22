import os, json
import pandas as pd
from pathlib import Path

def load_synthea(base_dir: str):
    base = Path(base_dir)
    tables = {}
    for name in [
        "patients","conditions","medications","observations","encounters",
        "allergies","procedures","careplans","immunizations","devices","supplies"
    ]:
        p = base / f"{name}.csv"
        if p.exists():
            tables[name] = pd.read_csv(p)
    return tables

def to_fhir_like(pid: str, t: dict) -> dict:
    P = t["patients"]; C=t.get("conditions"); M=t.get("medications")
    O=t.get("observations"); E=t.get("encounters"); A=t.get("allergies"); PR=t.get("procedures")
    patient_row = P[P["Id"]==pid].to_dict(orient="records")[0]

    def subset(df, key="PATIENT"):
        if df is None: return []
        return df[df[key]==pid].to_dict(orient="records")

    bundle = {
        "patient": {
            "id": pid,
            "gender": patient_row.get("GENDER"),
            "birthdate": patient_row.get("BIRTHDATE"),
            "race": patient_row.get("RACE"),
            "ethnicity": patient_row.get("ETHNICITY")
        },
        "problems": subset(C),
        "medications": subset(M),
        "observations": subset(O),
        "encounters": subset(E),
        "allergies": subset(A),
        "procedures": subset(PR),
        "notes": []
    }
    return bundle

def export_patients(tables: dict, out_dir: str, limit: int = 5):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    ids = list(tables["patients"]["Id"].head(limit))
    for pid in ids:
        b = to_fhir_like(pid, tables)
        (out / f"{pid}.json").write_text(json.dumps(b, indent=2))
    print(f"✅ Created {len(ids)} patient JSONs in {out}/")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthea_dir", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--limit", type=int, default=5)
    args = ap.parse_args()
    t = load_synthea(args.synthea_dir)
    export_patients(t, args.out_dir, args.limit)
