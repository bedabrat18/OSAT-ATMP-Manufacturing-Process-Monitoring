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
