import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "osat_atmp_process_data.csv")
LIMIT_FILE = os.path.join(BASE_DIR, "config", "process_limits.csv")
OUT_DIR = os.path.join(BASE_DIR, "outputs", "monitoring_reports")
OUT_FILE = os.path.join(OUT_DIR, "process_monitoring_results.csv")
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(DATA_FILE)
limits = pd.read_csv(LIMIT_FILE)
statuses, abnormal_parameters = [], []

for _, row in df.iterrows():
    if not bool(row["is_processed"]):
        statuses.append("NOT_PROCESSED")
        abnormal_parameters.append("")
        continue
    out_of_range = []
    for _, limit in limits.iterrows():
        if limit["route"] not in ("ALL", row["packaging_route"]):
            continue
        value = row.get(limit["parameter"])
        if pd.isna(value):
            continue
        if value < limit["lower_limit"] or value > limit["upper_limit"]:
            out_of_range.append(limit["parameter"])
    statuses.append("ABNORMAL" if out_of_range else "NORMAL")
    abnormal_parameters.append(", ".join(out_of_range))

df["monitoring_status"] = statuses
df["abnormal_parameters"] = abnormal_parameters
df["is_abnormal"] = df["monitoring_status"].eq("ABNORMAL")
df.to_csv(OUT_FILE, index=False)
print(f"Monitoring records: {len(df):,}")
print(df["monitoring_status"].value_counts(dropna=False).to_string())
print(f"Saved: {OUT_FILE}")
