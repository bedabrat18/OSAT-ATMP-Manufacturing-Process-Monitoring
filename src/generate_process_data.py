import os
import random
import numpy as np
import pandas as pd


# ============================================================
# OSAT / ATMP MANUFACTURING PROCESS MONITORING
# Synthetic Data Generator
# ============================================================

random.seed(42)
np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_DIR = os.path.join(BASE_DIR, "config")
DATA_DIR = os.path.join(BASE_DIR, "data")

CLASSIFICATION_FILE = os.path.join(
    CONFIG_DIR, "process_classification.csv"
)

OUTPUT_FILE = os.path.join(
    DATA_DIR, "osat_atmp_process_data.csv"
)

os.makedirs(DATA_DIR, exist_ok=True)


# ------------------------------------------------------------
# 1. Load OSAT / ATMP process classification
# ------------------------------------------------------------

classification = pd.read_csv(CLASSIFICATION_FILE)

stages = classification["process_stage"].tolist()

operation_map = dict(
    zip(
        classification["process_stage"],
        classification["operation_type"]
    )
)

category_map = dict(
    zip(
        classification["process_stage"],
        classification["monitoring_category"]
    )
)


# ------------------------------------------------------------
# 2. Manufacturing configuration
# ------------------------------------------------------------

NUM_UNITS = 6000
NUM_LOTS = 40

units_per_lot = NUM_UNITS // NUM_LOTS

shifts = ["A", "B", "C"]

equipment_map = {
    "Wafer Inspection": ["WI-01", "WI-02"],
    "Wafer Sort": ["WS-01", "WS-02"],
    "Back Grinding": ["BG-01", "BG-02"],
    "Wafer Dicing": ["WD-01", "WD-02"],
    "Die Attach": ["DA-01", "DA-02"],
    "Wire Bonding": ["WB-01", "WB-02"],
    "Encapsulation / Molding": ["MO-01", "MO-02"],
    "Marking": ["MK-01", "MK-02"],
    "Singulation": ["SG-01", "SG-02"],
    "Package Inspection": ["PI-01", "PI-02"],
    "Burn-in": ["BI-01", "BI-02"],
    "ICT": ["ICT-01", "ICT-02"],
    "FCT": ["FCT-01", "FCT-02"],
    "EOL": ["EOL-01", "EOL-02"],
    "Final Inspection": ["FI-01", "FI-02"],
    "Packing / Dispatch": ["PK-01", "PK-02"]
}


# ------------------------------------------------------------
# 3. Parameter generation
# ------------------------------------------------------------

def generate_value(parameter):
    """
    Generate synthetic process parameter values.

    Most values are within the configured operating range.
    A small percentage are intentionally outside the range
    so that the monitoring system can demonstrate
    NORMAL / ABNORMAL conditions.
    """

    parameter_ranges = {

        "wafer_thickness_um": (700, 800),
        "ttv_um": (0, 5),
        "bow_um": (0, 50),
        "warp_um": (0, 50),
        "tape_thickness_um": (80, 120),

        "sort_current_a": (9.5, 10.5),

        "thickness_variation_um": (0, 5),

        "kerf_width_um": (45, 55),

        "attach_force_n": (8, 12),
        "attach_offset_um": (0, 50),

        "wire_bond_force_n": (60, 70),
        "bond_pull_strength_gf": (5, 10),

        "mold_temperature_c": (170, 190),
        "mold_cure_time_s": (100, 140),
        "void_percentage": (0, 5),

        "marking_quality_score": (90, 100),

        "singulation_damage_score": (0, 10),

        "package_dimension_mm": (9.8, 10.2),

        "burn_in_temperature_c": (120, 130),
        "burn_in_hours": (4, 8),

        "ict_current_a": (9.5, 10.5),

        "fct_voltage_v": (3.1, 3.5),

        "eol_temperature_c": (80, 100),

        "packaging_damage_score": (0, 10)
    }

    low, high = parameter_ranges[parameter]

    # 95% normal observations
    if random.random() < 0.95:

        value = np.random.uniform(low, high)

    else:

        # Generate an abnormal observation
        margin = (high - low) * 0.20

        if random.random() < 0.5:
            value = np.random.uniform(
                low - margin,
                low
            )
        else:
            value = np.random.uniform(
                high,
                high + margin
            )

    return round(value, 3)


# ------------------------------------------------------------
# 4. Stage-specific parameters
# ------------------------------------------------------------

stage_parameters = {

    "Wafer Inspection": [
        "wafer_thickness_um",
        "ttv_um",
        "bow_um",
        "warp_um",
        "tape_thickness_um"
    ],

    "Wafer Sort": [
        "sort_current_a"
    ],

    "Back Grinding": [
        "wafer_thickness_um",
        "thickness_variation_um"
    ],

    "Wafer Dicing": [
        "kerf_width_um"
    ],

    "Die Attach": [
        "attach_force_n",
        "attach_offset_um"
    ],

    "Wire Bonding": [
        "wire_bond_force_n",
        "bond_pull_strength_gf"
    ],

    "Encapsulation / Molding": [
        "mold_temperature_c",
        "mold_cure_time_s",
        "void_percentage"
    ],

    "Marking": [
        "marking_quality_score"
    ],

    "Singulation": [
        "singulation_damage_score"
    ],

    "Package Inspection": [
        "package_dimension_mm"
    ],

    "Burn-in": [
        "burn_in_temperature_c",
        "burn_in_hours"
    ],

    "ICT": [
        "ict_current_a"
    ],

    "FCT": [
        "fct_voltage_v"
    ],

    "EOL": [
        "eol_temperature_c"
    ],

    "Final Inspection": [
        "marking_quality_score",
        "package_dimension_mm"
    ],

    "Packing / Dispatch": [
        "packaging_damage_score"
    ]
}


# ------------------------------------------------------------
# 5. Generate manufacturing records
# ------------------------------------------------------------

records = []

unit_counter = 1

for lot_number in range(1, NUM_LOTS + 1):

    lot_id = f"LOT{lot_number:03d}"

    for _ in range(units_per_lot):

        unit_id = f"UNIT{unit_counter:05d}"
        wafer_id = f"WAFER{unit_counter:04d}"
        package_id = f"PKG{unit_counter:05d}"

        shift = random.choice(shifts)

        unit_status = "PASS"

        for stage_number, stage in enumerate(stages, start=1):

            # Once a unit becomes failed, later stages are
            # still represented but marked NOT_PROCESSED.
            if unit_status == "FAIL":

                process_status = "NOT_PROCESSED"

                record = {
                    "unit_id": unit_id,
                    "lot_id": lot_id,
                    "wafer_id": wafer_id,
                    "package_id": package_id,
                    "stage_number": stage_number,
                    "process_stage": stage,
                    "operation_type": operation_map[stage],
                    "monitoring_category": category_map[stage],
                    "equipment_id": random.choice(
                        equipment_map[stage]
                    ),
                    "shift": shift,
                    "process_status": process_status,
                    "parameter_status": "NOT_PROCESSED"
                }

                records.append(record)

                continue

            equipment_id = random.choice(
                equipment_map[stage]
            )

            values = {}

            parameter_status = "NORMAL"

            for parameter in stage_parameters[stage]:

                value = generate_value(parameter)

                values[parameter] = value

            # Determine whether any generated parameter
            # is outside its normal operating range.
            limits = {
                "wafer_thickness_um": (700, 800),
                "ttv_um": (0, 5),
                "bow_um": (0, 50),
                "warp_um": (0, 50),
                "tape_thickness_um": (80, 120),
                "sort_current_a": (9.5, 10.5),
                "thickness_variation_um": (0, 5),
                "kerf_width_um": (45, 55),
                "attach_force_n": (8, 12),
                "attach_offset_um": (0, 50),
                "wire_bond_force_n": (60, 70),
                "bond_pull_strength_gf": (5, 10),
                "mold_temperature_c": (170, 190),
                "mold_cure_time_s": (100, 140),
                "void_percentage": (0, 5),
                "marking_quality_score": (90, 100),
                "singulation_damage_score": (0, 10),
                "package_dimension_mm": (9.8, 10.2),
                "burn_in_temperature_c": (120, 130),
                "burn_in_hours": (4, 8),
                "ict_current_a": (9.5, 10.5),
                "fct_voltage_v": (3.1, 3.5),
                "eol_temperature_c": (80, 100),
                "packaging_damage_score": (0, 10)
            }

            for parameter, value in values.items():

                low, high = limits[parameter]

                if value < low or value > high:

                    parameter_status = "ABNORMAL"
                    break

            process_status = (
                "FAIL"
                if parameter_status == "ABNORMAL"
                else "PASS"
            )

            if process_status == "FAIL":
                unit_status = "FAIL"

            record = {
                "unit_id": unit_id,
                "lot_id": lot_id,
                "wafer_id": wafer_id,
                "package_id": package_id,
                "stage_number": stage_number,
                "process_stage": stage,
                "operation_type": operation_map[stage],
                "monitoring_category": category_map[stage],
                "equipment_id": equipment_id,
                "shift": shift,
                "process_status": process_status,
                "parameter_status": parameter_status
            }

            record.update(values)

            records.append(record)

        unit_counter += 1


# ------------------------------------------------------------
# 6. Create dataframe
# ------------------------------------------------------------

df = pd.DataFrame(records)


# ------------------------------------------------------------
# 7. Add timestamp
# ------------------------------------------------------------

start_time = pd.Timestamp("2026-01-01 06:00:00")

df["timestamp"] = [
    start_time + pd.Timedelta(minutes=i)
    for i in range(len(df))
]


# ------------------------------------------------------------
# 8. Arrange important columns first
# ------------------------------------------------------------

first_columns = [
    "timestamp",
    "unit_id",
    "lot_id",
    "wafer_id",
    "package_id",
    "stage_number",
    "process_stage",
    "operation_type",
    "monitoring_category",
    "equipment_id",
    "shift",
    "process_status",
    "parameter_status"
]

remaining_columns = [
    col for col in df.columns
    if col not in first_columns
]

df = df[first_columns + remaining_columns]


# ------------------------------------------------------------
# 9. Save dataset
# ------------------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ------------------------------------------------------------
# 10. Display summary
# ------------------------------------------------------------

print("=" * 60)
print("OSAT / ATMP PROCESS MONITORING DATASET")
print("=" * 60)

print(f"Total records       : {len(df):,}")
print(f"Unique units        : {df['unit_id'].nunique():,}")
print(f"Unique lots         : {df['lot_id'].nunique():,}")
print(f"Unique wafers       : {df['wafer_id'].nunique():,}")

print("\nOperation Type:")
print(df["operation_type"].value_counts())

print("\nProcess Status:")
print(df["process_status"].value_counts())

print("\nParameter Status:")
print(df["parameter_status"].value_counts())

print("\nProcess Stages:")
print(df["process_stage"].value_counts())

print("\nDataset saved to:")
print(OUTPUT_FILE)

print("=" * 60)