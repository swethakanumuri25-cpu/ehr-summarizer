import pandas as pd, json, os
from pathlib import Path

BASE = "EHR"           # folder containing your 16 CSV files
OUT = "patient_jsons"  # folder where output JSONs will be saved
os.makedirs(OUT, exist_ok=True)

# Load all CSVs into a dictionary of DataFrames
tables = {f.replace(".csv",""): pd.read_csv(os.path.join(BASE,f))
          for f in os.listdir(BASE) if f.endswith(".csv")}

patients = tables["patients"]
patient_ids = list(patients["Id"].head(10))   # change head(10) to all if needed

def subset(df, pid_col="PATIENT", pid=None):
    if df is None or pid not in df[pid_col].values:
        return []
    return df[df[pid_col]==pid].to_dict(orient="records")

for pid in patient_ids:
    bundle = {
        "patient": patients[patients["Id"]==pid].to_dict(orient="records")[0],
        "conditions": subset(tables.get("conditions"), pid=pid),
        "medications": subset(tables.get("medications"), pid=pid),
        "observations": subset(tables.get("observations"), pid=pid),
        "encounters": subset(tables.get("encounters"), pid=pid),
        "procedures": subset(tables.get("procedures"), pid=pid),
        "allergies": subset(tables.get("allergies"), pid=pid),
        "careplans": subset(tables.get("careplans"), pid=pid),
        "immunizations": subset(tables.get("immunizations"), pid=pid),
        "devices": subset(tables.get("devices"), pid=pid),
        "supplies": subset(tables.get("supplies"), pid=pid)
    }
    with open(f"{OUT}/{pid}.json", "w") as f:
        json.dump(bundle, f, indent=2)

print(f"✅ Created {len(os.listdir(OUT))} patient files in {OUT}/")
