from pathlib import Path
import shutil
import subprocess
import sys
import textwrap

ROOT = Path.cwd()
BACKUP = ROOT / "backup_before_three_routes"
SRC = ROOT / "src"
CONFIG = ROOT / "config"
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs" / "monitoring_reports"

for folder in (SRC, CONFIG, DATA, OUTPUTS):
    folder.mkdir(parents=True, exist_ok=True)

BACKUP.mkdir(exist_ok=True)
for rel in [
    "src/generate_process_data.py",
    "src/monitoring_engine.py",
    "src/generate_monitoring_report.py",
    "src/dashboard.py",
    "config/process_limits.csv",
    "config/process_classification.csv",
    "README.md",
]:
    p = ROOT / rel
    if p.exists():
        shutil.copy2(p, BACKUP / rel.replace("/", "__"))

files = {
"src/generate_process_data.py": r"""
import os
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
OUT = os.path.join(DATA_DIR, "osat_atmp_process_data.csv")

# Synthetic educational data only. These are separate packaging routes,
# not three sequential manufacturing stages and not TSAT production data.
ROUTES = ["Wire Bond", "Flip Chip", "Integrated Systems Packaging (ISP)"]
N_PER_ROUTE = 2000
rng = np.random.default_rng(42)
rows = []
start = pd.Timestamp("2026-01-01 06:00:00")

for route in ROUTES:
    for i in range(N_PER_ROUTE):
        unit_num = i + 1
        if route == "Wire Bond":
            wire_force = float(rng.normal(28, 4))
            bond_pull = float(rng.normal(7.5, 1.2))
            align_offset = np.nan
            bump_height = np.nan
            reflow_temp = np.nan
            equipment = f"WB-{rng.integers(1, 7):02d}"
        elif route == "Flip Chip":
            wire_force = np.nan
            bond_pull = np.nan
            align_offset = float(abs(rng.normal(5, 2)))
            bump_height = float(rng.normal(75, 8))
            reflow_temp = float(rng.normal(245, 8))
            equipment = f"FC-{rng.integers(1, 7):02d}"
        else:
            wire_force = np.nan
            bond_pull = np.nan
            align_offset = float(abs(rng.normal(6, 2.5)))
            bump_height = float(rng.normal(78, 9))
            reflow_temp = float(rng.normal(242, 10))
            equipment = f"ISP-{rng.integers(1, 7):02d}"

        package_warpage = float(rng.normal(0.09, 0.035))
        test_voltage = float(rng.normal(1.0, 0.05))
        processed = bool(rng.random() > 0.12)
        process_status = ("PASS" if rng.random() > 0.08 else "FAIL") if processed else "NOT_PROCESSED"

        rows.append({
            "timestamp": start + pd.Timedelta(minutes=int(rng.integers(0, 120000))),
            "unit_id": f"UNIT-{route[:2].upper().replace(' ', '')}-{unit_num:05d}",
            "lot_id": f"LOT-{route[:2].upper().replace(' ', '')}-{(unit_num-1)//50+1:03d}",
            "wafer_id": f"WAFER-{(unit_num-1)//25+1:04d}",
            "package_id": f"PKG-{route[:2].upper().replace(' ', '')}-{unit_num:05d}",
            "packaging_route": route,
            "equipment_id": equipment,
            "shift": ["Shift A", "Shift B", "Shift C"][int(rng.integers(0, 3))],
            "process_status": process_status,
            "wire_bond_force_n": wire_force,
            "bond_pull_strength_gf": bond_pull,
            "die_alignment_offset_um": align_offset,
            "bump_height_um": bump_height,
            "reflow_temperature_c": reflow_temp,
            "package_warpage_mm": package_warpage,
            "electrical_test_voltage_v": test_voltage,
            "is_processed": processed,
        })

df = pd.DataFrame(rows).sort_values("timestamp").reset_index(drop=True)
df.to_csv(OUT, index=False)
print(f"Generated {len(df):,} synthetic records: {OUT}")
print(df["packaging_route"].value_counts().to_string())
""",
"src/monitoring_engine.py": r"""
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
""",
"src/generate_monitoring_report.py": r"""
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(BASE_DIR, "outputs", "monitoring_reports")
SOURCE = os.path.join(REPORT_DIR, "process_monitoring_results.csv")
os.makedirs(REPORT_DIR, exist_ok=True)
df = pd.read_csv(SOURCE)

reports = {
    "route_monitoring_report.csv": df.groupby(["packaging_route", "monitoring_status"]).size().reset_index(name="records"),
    "equipment_monitoring_report.csv": df.groupby(["packaging_route", "equipment_id", "monitoring_status"]).size().reset_index(name="records"),
    "shift_monitoring_report.csv": df.groupby(["shift", "monitoring_status"]).size().reset_index(name="records"),
    "lot_monitoring_report.csv": df.groupby(["packaging_route", "lot_id", "monitoring_status"]).size().reset_index(name="records"),
    "abnormal_conditions_report.csv": df[df["monitoring_status"].eq("ABNORMAL")].copy(),
    "overall_monitoring_summary.csv": df.groupby("monitoring_status").size().reset_index(name="records"),
}
for filename, report in reports.items():
    report.to_csv(os.path.join(REPORT_DIR, filename), index=False)
    print(f"Created {filename}: {len(report):,} rows")
""",
"src/dashboard.py": r"""
import os
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "outputs", "monitoring_reports", "process_monitoring_results.csv")
REPORT_DIR = os.path.join(BASE_DIR, "outputs", "monitoring_reports")

st.set_page_config(page_title="OSAT / ATMP Three-Route Monitor", page_icon="🏭", layout="wide")
st.title("OSAT / ATMP Packaging Route Monitoring")
st.caption("Personal learning prototype using synthetic data — not a TSAT production system.")

if not os.path.exists(DATA_FILE):
    st.warning("Monitoring data not found. Run the data generator, monitoring engine and report generator first.")
    st.code("python src/generate_process_data.py\npython src/monitoring_engine.py\npython src/generate_monitoring_report.py")
    st.stop()

df = pd.read_csv(DATA_FILE)
routes = ["Wire Bond", "Flip Chip", "Integrated Systems Packaging (ISP)"]

st.info("This prototype presents three separate packaging route categories, not three consecutive steps in one production line. Process values and limits are illustrative synthetic values, not actual factory specifications.")

with st.sidebar:
    st.header("Filters")
    selected_routes = st.multiselect("Packaging route", routes, default=routes)
    shifts = sorted(df["shift"].dropna().unique().tolist())
    selected_shifts = st.multiselect("Shift", shifts, default=shifts)
    statuses = ["NORMAL", "ABNORMAL", "NOT_PROCESSED"]
    selected_status = st.multiselect("Monitoring status", statuses, default=statuses)

filtered = df[
    df["packaging_route"].isin(selected_routes)
    & df["shift"].isin(selected_shifts)
    & df["monitoring_status"].isin(selected_status)
].copy()

a, b, c, d = st.columns(4)
a.metric("Records in view", f"{len(filtered):,}")
b.metric("Normal", f"{(filtered.monitoring_status == 'NORMAL').sum():,}")
c.metric("Abnormal", f"{(filtered.monitoring_status == 'ABNORMAL').sum():,}")
d.metric("Not processed", f"{(filtered.monitoring_status == 'NOT_PROCESSED').sum():,}")

st.header("Three Packaging Routes")
columns = st.columns(3)
descriptions = {
    "Wire Bond": "Representative parameters: wire-bond force and bond-pull strength.",
    "Flip Chip": "Representative parameters: die-alignment offset, bump height and reflow temperature.",
    "Integrated Systems Packaging (ISP)": "High-level illustrative category; TSAT-specific internal details are not asserted."
}
for col, route in zip(columns, routes):
    sub = filtered[filtered["packaging_route"] == route]
    with col:
        st.subheader(route)
        st.metric("Records", f"{len(sub):,}")
        st.metric("Abnormal records", f"{(sub.monitoring_status == 'ABNORMAL').sum():,}")
        st.caption(descriptions[route])

st.header("Monitoring Status by Route")
if not filtered.empty:
    summary = filtered.groupby(["packaging_route", "monitoring_status"]).size().reset_index(name="records")
    pivot = summary.pivot(index="packaging_route", columns="monitoring_status", values="records").fillna(0)
    st.bar_chart(pivot)
else:
    st.info("No records match the selected filters.")

st.header("Parameter Monitoring")
parameter_columns = [
    "wire_bond_force_n", "bond_pull_strength_gf", "die_alignment_offset_um",
    "bump_height_um", "reflow_temperature_c", "package_warpage_mm",
    "electrical_test_voltage_v"
]
chosen = st.selectbox("Select parameter", parameter_columns)
visible_columns = ["packaging_route", "unit_id", "lot_id", "equipment_id", "shift", chosen, "monitoring_status"]
parameter_data = filtered[visible_columns].dropna(subset=[chosen])
st.dataframe(parameter_data.head(300), use_container_width=True, hide_index=True)

st.header("Equipment Monitoring")
equipment_summary = filtered.groupby(["packaging_route", "equipment_id", "monitoring_status"]).size().reset_index(name="records")
st.dataframe(equipment_summary, use_container_width=True, hide_index=True)

st.header("Abnormal Conditions")
abnormal = filtered[filtered["monitoring_status"] == "ABNORMAL"]
if abnormal.empty:
    st.success("No abnormal records in the current filtered view.")
else:
    cols = ["timestamp", "packaging_route", "unit_id", "lot_id", "equipment_id", "shift", "abnormal_parameters", "monitoring_status"]
    st.dataframe(abnormal[cols].head(500), use_container_width=True, hide_index=True)

st.header("Monitoring Reports")
report_names = [
    "overall_monitoring_summary.csv", "route_monitoring_report.csv",
    "equipment_monitoring_report.csv", "shift_monitoring_report.csv",
    "lot_monitoring_report.csv", "abnormal_conditions_report.csv"
]
for filename in report_names:
    path = os.path.join(REPORT_DIR, filename)
    if os.path.exists(path):
        with open(path, "rb") as f:
            st.download_button(f"Download {filename}", data=f.read(), file_name=filename, mime="text/csv")

st.caption("Educational prototype only. Synthetic records and illustrative limits must not be interpreted as real production specifications.")
""",
"config/process_classification.csv": r"""packaging_route,description
Wire Bond,Wire-bond interconnection packaging route represented for learning
Flip Chip,Flip-chip interconnection packaging route represented for learning
Integrated Systems Packaging (ISP),High-level integrated systems packaging category represented for learning
""",
"config/process_limits.csv": r"""parameter,lower_limit,upper_limit,unit,route
wire_bond_force_n,18,38,N,Wire Bond
bond_pull_strength_gf,4.5,10.5,gf,Wire Bond
die_alignment_offset_um,0,10,um,Flip Chip
bump_height_um,55,95,um,Flip Chip
reflow_temperature_c,220,265,C,Flip Chip
package_warpage_mm,0,0.16,mm,ALL
electrical_test_voltage_v,0.85,1.15,V,ALL
die_alignment_offset_um,0,12,um,Integrated Systems Packaging (ISP)
bump_height_um,55,100,um,Integrated Systems Packaging (ISP)
reflow_temperature_c,215,270,C,Integrated Systems Packaging (ISP)
""",
"README.md": r"""
# OSAT / ATMP Packaging Route Monitoring Prototype

## Personal learning / portfolio project

This prototype explores three semiconductor packaging route categories:
1. **Wire Bond**
2. **Flip Chip**
3. **Integrated Systems Packaging (ISP)**

These are represented as separate categories, not three consecutive manufacturing steps. This project does not claim to reproduce TSAT Jagiroad's internal production process.

## Objective

Explore how synthetic manufacturing records, representative parameters, equipment IDs, lots, shifts, and monitoring status can be organized in a dashboard.

## Features

- Three packaging route categories
- Synthetic records and illustrative configurable limits
- NORMAL / ABNORMAL / NOT_PROCESSED monitoring states
- Equipment, lot, and shift summaries
- Interactive Streamlit dashboard
- Downloadable CSV monitoring reports

## Data disclaimer

All records are generated synthetically for education and demonstration. Limits are illustrative only, not actual semiconductor process specifications. This is not TSAT/Tata Electronics production data and does not establish TSAT's exact process flow.

## Run

```powershell
python src\generate_process_data.py
python src\monitoring_engine.py
python src\generate_monitoring_report.py
python -m streamlit run src\dashboard.py
```

## Tools

Python, Pandas, NumPy, Streamlit, CSV, Git and GitHub.

## Scope

Monitoring only. No machine learning, failure prediction, yield prediction, root-cause analysis, predictive maintenance, or automated equipment control.
"""
}

for rel, content in files.items():
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")

for command in [
    [sys.executable, str(SRC / "generate_process_data.py")],
    [sys.executable, str(SRC / "monitoring_engine.py")],
    [sys.executable, str(SRC / "generate_monitoring_report.py")],
]:
    subprocess.run(command, cwd=ROOT, check=True)

print("\nCompleted: project now uses only three packaging route categories.")
print(f"Backups of replaced files are in: {BACKUP}")
print("Run: python -m streamlit run src/dashboard.py")
