"""
OSAT / ATMP Manufacturing Process Monitoring
Monitoring Report Generator

Purpose:
    Generate CSV monitoring reports from the processed OSAT/ATMP
    manufacturing monitoring dataset.

This project focuses on:
    - Process monitoring
    - Stage monitoring
    - Parameter monitoring
    - Equipment monitoring
    - Shift monitoring
    - Operation classification
    - Abnormal-condition monitoring
    - Unit monitoring
    - Lot monitoring

Excluded:
    - Machine learning
    - Yield prediction
    - Failure prediction
    - Risk prediction
    - Root-cause analysis
    - Predictive analytics
"""

import os
import pandas as pd


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_FILE = os.path.join(
    BASE_DIR,
    "outputs",
    "monitoring_reports",
    "process_monitoring_results.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "monitoring_reports"
)


# ============================================================
# PARAMETER CONFIGURATION
# ============================================================

PARAMETER_COLUMNS = [
    "wafer_thickness_um",
    "ttv_um",
    "bow_um",
    "warp_um",
    "tape_thickness_um",
    "sort_current_a",
    "thickness_variation_um",
    "kerf_width_um",
    "attach_force_n",
    "attach_offset_um",
    "wire_bond_force_n",
    "bond_pull_strength_gf",
    "mold_temperature_c",
    "mold_cure_time_s",
    "void_percentage",
    "marking_quality_score",
    "singulation_damage_score",
    "package_dimension_mm",
    "burn_in_temperature_c",
    "burn_in_hours",
    "ict_current_a",
    "fct_voltage_v",
    "eol_temperature_c",
    "packaging_damage_score"
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_numeric(series):
    """
    Convert a pandas Series to numeric values.
    Invalid values are converted to NaN.
    """
    return pd.to_numeric(series, errors="coerce")


def count_status(df, column, value):
    """
    Count records having a particular status.
    """
    if column not in df.columns:
        return 0

    return int((df[column] == value).sum())


def save_report(df, filename):
    """
    Save a DataFrame as a CSV report.
    """
    output_path = os.path.join(OUTPUT_DIR, filename)

    df.to_csv(
        output_path,
        index=False
    )

    print("Generated:", filename)
    print("Records  :", len(df))
    print("Path     :", output_path)
    print("-" * 65)

    return output_path


# ============================================================
# LOAD DATA
# ============================================================

def load_monitoring_data():
    """
    Load the monitoring results CSV.
    """

    print()
    print("=" * 65)
    print("Loading monitoring data...")
    print("=" * 65)

    if not os.path.exists(INPUT_FILE):
        print()
        print("ERROR: Monitoring input file was not found.")
        print()
        print("Expected file:")
        print(INPUT_FILE)
        print()
        print("Please run:")
        print("python src\\monitoring_engine.py")
        print()

        raise FileNotFoundError(INPUT_FILE)

    df = pd.read_csv(INPUT_FILE)

    print()
    print("Monitoring records loaded:", f"{len(df):,}")
    print("Columns available        :", len(df.columns))

    return df


# ============================================================
# DATA PREPARATION
# ============================================================

def prepare_data(df):
    """
    Prepare data types and basic monitoring fields.
    """

    print()
    print("=" * 65)
    print("Preparing monitoring data...")
    print("=" * 65)

    # Timestamp
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

    # Numeric columns
    numeric_columns = [
        "stage_number",
        "wafer_thickness_um",
        "ttv_um",
        "bow_um",
        "warp_um",
        "tape_thickness_um",
        "sort_current_a",
        "thickness_variation_um",
        "kerf_width_um",
        "attach_force_n",
        "attach_offset_um",
        "wire_bond_force_n",
        "bond_pull_strength_gf",
        "mold_temperature_c",
        "mold_cure_time_s",
        "void_percentage",
        "marking_quality_score",
        "singulation_damage_score",
        "package_dimension_mm",
        "burn_in_temperature_c",
        "burn_in_hours",
        "ict_current_a",
        "fct_voltage_v",
        "eol_temperature_c",
        "packaging_damage_score"
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = safe_numeric(df[column])

    # Create monitoring_status if it does not already exist
    if "monitoring_status" not in df.columns:

        if "parameter_status" in df.columns:
            df["monitoring_status"] = df["parameter_status"]

        elif "process_status" in df.columns:

            df["monitoring_status"] = df["process_status"].replace(
                {
                    "PASS": "NORMAL",
                    "FAIL": "ABNORMAL",
                    "NOT_PROCESSED": "NOT_PROCESSED"
                }
            )

        else:
            df["monitoring_status"] = "NOT_PROCESSED"

    # Create monitored flag if missing
    if "monitored" not in df.columns:
        df["monitored"] = (
            df["monitoring_status"].isin(
                ["NORMAL", "ABNORMAL"]
            )
        )

    return df


# ============================================================
# GENERAL SUMMARY
# ============================================================

def generate_general_summary(df):
    """
    Display general monitoring statistics.
    """

    print()
    print("=" * 65)
    print("MONITORING SUMMARY")
    print("=" * 65)

    total_records = len(df)

    if "unit_id" in df.columns:
        unique_units = df["unit_id"].nunique()
    else:
        unique_units = 0

    if "lot_id" in df.columns:
        unique_lots = df["lot_id"].nunique()
    else:
        unique_lots = 0

    if "wafer_id" in df.columns:
        unique_wafers = df["wafer_id"].nunique()
    else:
        unique_wafers = 0

    normal_records = count_status(
        df,
        "monitoring_status",
        "NORMAL"
    )

    abnormal_records = count_status(
        df,
        "monitoring_status",
        "ABNORMAL"
    )

    not_processed_records = count_status(
        df,
        "monitoring_status",
        "NOT_PROCESSED"
    )

    print(
        f"Total records           : {total_records:,}"
    )

    print(
        f"Unique units            : {unique_units:,}"
    )

    print(
        f"Unique lots             : {unique_lots:,}"
    )

    print(
        f"Unique wafers           : {unique_wafers:,}"
    )

    print(
        f"Normal records          : {normal_records:,}"
    )

    print(
        f"Abnormal records        : {abnormal_records:,}"
    )

    print(
        f"Not processed records   : {not_processed_records:,}"
    )


# ============================================================
# 1. STAGE MONITORING REPORT
# ============================================================

def generate_stage_report(df):
    """
    Generate process-stage monitoring report.
    """

    print()
    print("=" * 65)
    print("1. STAGE MONITORING REPORT")
    print("=" * 65)

    group_columns = []

    for column in [
        "stage_number",
        "process_stage",
        "operation_type"
    ]:
        if column in df.columns:
            group_columns.append(column)

    if not group_columns:
        print("Required stage columns were not found.")
        return None

    report = (
        df.groupby(group_columns, dropna=False)
        .agg(
            total_records=(
                "monitoring_status",
                "size"
            ),
            normal_records=(
                "monitoring_status",
                lambda x: (x == "NORMAL").sum()
            ),
            abnormal_records=(
                "monitoring_status",
                lambda x: (x == "ABNORMAL").sum()
            ),
            not_processed_records=(
                "monitoring_status",
                lambda x: (x == "NOT_PROCESSED").sum()
            )
        )
        .reset_index()
    )

    report["processed_records"] = (
        report["normal_records"]
        + report["abnormal_records"]
    )

    report["monitoring_completion_percent"] = (
        report["processed_records"]
        / report["total_records"]
        * 100
    ).round(2)

    report["abnormal_record_percent"] = 0.0

    processed_mask = report["processed_records"] > 0

    report.loc[
        processed_mask,
        "abnormal_record_percent"
    ] = (
        report.loc[
            processed_mask,
            "abnormal_records"
        ]
        / report.loc[
            processed_mask,
            "processed_records"
        ]
        * 100
    ).round(2)

    report = report.sort_values(
        by=group_columns
    )

    return save_report(
        report,
        "stage_monitoring_report.csv"
    )


# ============================================================
# 2. PARAMETER MONITORING REPORT
# ============================================================

def generate_parameter_report(df):
    """
    Generate process parameter monitoring report.
    """

    print()
    print("=" * 65)
    print("2. PARAMETER MONITORING REPORT")
    print("=" * 65)

    available_parameters = []

    for parameter in PARAMETER_COLUMNS:
        if parameter in df.columns:
            available_parameters.append(parameter)

    rows = []

    for parameter in available_parameters:

        values = safe_numeric(df[parameter])

        valid_values = values.dropna()

        if len(valid_values) == 0:
            continue

        monitored_values = df.loc[
            values.notna()
        ]

        normal_count = 0
        abnormal_count = 0

        if "parameter_status" in monitored_values.columns:

            normal_count = int(
                (
                    monitored_values["parameter_status"]
                    == "NORMAL"
                ).sum()
            )

            abnormal_count = int(
                (
                    monitored_values["parameter_status"]
                    == "ABNORMAL"
                ).sum()
            )

        elif "monitoring_status" in monitored_values.columns:

            normal_count = int(
                (
                    monitored_values["monitoring_status"]
                    == "NORMAL"
                ).sum()
            )

            abnormal_count = int(
                (
                    monitored_values["monitoring_status"]
                    == "ABNORMAL"
                ).sum()
            )

        total_valid = len(valid_values)

        abnormal_percent = 0.0

        if total_valid > 0:
            abnormal_percent = (
                abnormal_count
                / total_valid
                * 100
            )

        row = {
            "parameter": parameter,
            "total_records": len(df),
            "valid_measurements": total_valid,
            "missing_measurements": len(df) - total_valid,
            "normal_records": normal_count,
            "abnormal_records": abnormal_count,
            "abnormal_percent": round(
                abnormal_percent,
                2
            ),
            "minimum": round(
                float(valid_values.min()),
                4
            ),
            "maximum": round(
                float(valid_values.max()),
                4
            ),
            "average": round(
                float(valid_values.mean()),
                4
            ),
            "median": round(
                float(valid_values.median()),
                4
            ),
            "standard_deviation": round(
                float(valid_values.std()),
                4
            )
        }

        rows.append(row)

    report = pd.DataFrame(rows)

    return save_report(
        report,
        "parameter_monitoring_report.csv"
    )


# ============================================================
# 3. EQUIPMENT MONITORING REPORT
# ============================================================

def generate_equipment_report(df):
    """
    Generate equipment monitoring report.
    """

    print()
    print("=" * 65)
    print("3. EQUIPMENT MONITORING REPORT")
    print("=" * 65)

    if "equipment_id" not in df.columns:
        print("equipment_id column not found.")
        return None

    report = (
        df.groupby("equipment_id", dropna=False)
        .agg(
            total_records=(
                "monitoring_status",
                "size"
            ),
            normal_records=(
                "monitoring_status",
                lambda x: (x == "NORMAL").sum()
            ),
            abnormal_records=(
                "monitoring_status",
                lambda x: (x == "ABNORMAL").sum()
            ),
            not_processed_records=(
                "monitoring_status",
                lambda x: (x == "NOT_PROCESSED").sum()
            )
        )
        .reset_index()
    )

    report["processed_records"] = (
        report["normal_records"]
        + report["abnormal_records"]
    )

    report["abnormal_percent"] = 0.0

    mask = report["processed_records"] > 0

    report.loc[
        mask,
        "abnormal_percent"
    ] = (
        report.loc[
            mask,
            "abnormal_records"
        ]
        / report.loc[
            mask,
            "processed_records"
        ]
        * 100
    ).round(2)

    report = report.sort_values(
        by="equipment_id"
    )

    return save_report(
        report,
        "equipment_monitoring_report.csv"
    )


# ============================================================
# 4. SHIFT MONITORING REPORT
# ============================================================

def generate_shift_report(df):
    """
    Generate shift monitoring report.
    """

    print()
    print("=" * 65)
    print("4. SHIFT MONITORING REPORT")
    print("=" * 65)

    if "shift" not in df.columns:
        print("shift column not found.")
        return None

    report = (
        df.groupby("shift", dropna=False)
        .agg(
            total_records=(
                "monitoring_status",
                "size"
            ),
            normal_records=(
                "monitoring_status",
                lambda x: (x == "NORMAL").sum()
            ),
            abnormal_records=(
                "monitoring_status",
                lambda x: (x == "ABNORMAL").sum()
            ),
            not_processed_records=(
                "monitoring_status",
                lambda x: (x == "NOT_PROCESSED").sum()
            )
        )
        .reset_index()
    )

    report["processed_records"] = (
        report["normal_records"]
        + report["abnormal_records"]
    )

    report["abnormal_percent"] = 0.0

    mask = report["processed_records"] > 0

    report.loc[
        mask,
        "abnormal_percent"
    ] = (
        report.loc[
            mask,
            "abnormal_records"
        ]
        / report.loc[
            mask,
            "processed_records"
        ]
        * 100
    ).round(2)

    report = report.sort_values(
        by="shift"
    )

    return save_report(
        report,
        "shift_monitoring_report.csv"
    )


# ============================================================
# 5. OPERATION MONITORING REPORT
# ============================================================

def generate_operation_report(df):
    """
    Generate OSAT / ATMP operation classification report.
    """

    print()
    print("=" * 65)
    print("5. OSAT / ATMP OPERATION REPORT")
    print("=" * 65)

    if "operation_type" not in df.columns:
        print("operation_type column not found.")
        return None

    report = (
        df.groupby("operation_type", dropna=False)
        .agg(
            total_records=(
                "monitoring_status",
                "size"
            ),
            normal_records=(
                "monitoring_status",
                lambda x: (x == "NORMAL").sum()
            ),
            abnormal_records=(
                "monitoring_status",
                lambda x: (x == "ABNORMAL").sum()
            ),
            not_processed_records=(
                "monitoring_status",
                lambda x: (x == "NOT_PROCESSED").sum()
            )
        )
        .reset_index()
    )

    report["processed_records"] = (
        report["normal_records"]
        + report["abnormal_records"]
    )

    report["abnormal_percent"] = 0.0

    mask = report["processed_records"] > 0

    report.loc[
        mask,
        "abnormal_percent"
    ] = (
        report.loc[
            mask,
            "abnormal_records"
        ]
        / report.loc[
            mask,
            "processed_records"
        ]
        * 100
    ).round(2)

    report = report.sort_values(
        by="operation_type"
    )

    return save_report(
        report,
        "operation_monitoring_report.csv"
    )


# ============================================================
# 6. ABNORMAL CONDITIONS REPORT
# ============================================================

def generate_abnormal_report(df):
    """
    Generate report containing abnormal monitoring records.
    """

    print()
    print("=" * 65)
    print("6. ABNORMAL CONDITIONS REPORT")
    print("=" * 65)

    if "monitoring_status" not in df.columns:
        print("monitoring_status column not found.")
        return None

    abnormal_df = df[
        df["monitoring_status"] == "ABNORMAL"
    ].copy()

    if abnormal_df.empty:
        print("No abnormal records found.")

        report = pd.DataFrame(
            columns=df.columns
        )

    else:

        preferred_columns = [
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
            "parameter_status",
            "monitoring_status"
        ]

        selected_columns = []

        for column in preferred_columns:
            if column in abnormal_df.columns:
                selected_columns.append(column)

        # Add parameter columns
        for column in PARAMETER_COLUMNS:
            if column in abnormal_df.columns:
                if column not in selected_columns:
                    selected_columns.append(column)

        # Include remaining useful columns
        for column in abnormal_df.columns:
            if column not in selected_columns:
                selected_columns.append(column)

        report = abnormal_df[selected_columns].copy()

        if "timestamp" in report.columns:
            report = report.sort_values(
                by="timestamp",
                ascending=False
            )

    return save_report(
        report,
        "abnormal_conditions_report.csv"
    )


# ============================================================
# 7. UNIT MONITORING REPORT
# ============================================================

def generate_unit_report(df):
    """
    Generate unit-level monitoring report.
    """

    print()
    print("=" * 65)
    print("7. UNIT MONITORING REPORT")
    print("=" * 65)

    if "unit_id" not in df.columns:
        print("unit_id column not found.")
        return None

    group_columns = ["unit_id"]

    for column in [
        "lot_id",
        "wafer_id",
        "package_id",
        "operation_type"
    ]:
        if column in df.columns:
            group_columns.append(column)

    report = (
        df.groupby(group_columns, dropna=False)
        .agg(
            total_stage_records=(
                "monitoring_status",
                "size"
            ),
            normal_records=(
                "monitoring_status",
                lambda x: (x == "NORMAL").sum()
            ),
            abnormal_records=(
                "monitoring_status",
                lambda x: (x == "ABNORMAL").sum()
            ),
            not_processed_records=(
                "monitoring_status",
                lambda x: (x == "NOT_PROCESSED").sum()
            )
        )
        .reset_index()
    )

    report["processed_records"] = (
        report["normal_records"]
        + report["abnormal_records"]
    )

    report["current_monitoring_status"] = "NOT_PROCESSED"

    normal_mask = (
        report["processed_records"] > 0
    ) & (
        report["abnormal_records"] == 0
    )

    abnormal_mask = (
        report["abnormal_records"] > 0
    )

    report.loc[
        normal_mask,
        "current_monitoring_status"
    ] = "NORMAL"

    report.loc[
        abnormal_mask,
        "current_monitoring_status"
    ] = "ABNORMAL"

    report = report.sort_values(
        by="unit_id"
    )

    return save_report(
        report,
        "unit_monitoring_report.csv"
    )


# ============================================================
# 8. LOT MONITORING REPORT
# ============================================================

def generate_lot_report(df):
    """
    Generate lot-level monitoring report.
    """

    print()
    print("=" * 65)
    print("8. LOT MONITORING REPORT")
    print("=" * 65)

    if "lot_id" not in df.columns:
        print("lot_id column not found.")
        return None

    group_columns = ["lot_id"]

    for column in [
        "operation_type",
        "shift"
    ]:
        if column in df.columns:
            group_columns.append(column)

    report = (
        df.groupby(group_columns, dropna=False)
        .agg(
            total_records=(
                "monitoring_status",
                "size"
            ),
            normal_records=(
                "monitoring_status",
                lambda x: (x == "NORMAL").sum()
            ),
            abnormal_records=(
                "monitoring_status",
                lambda x: (x == "ABNORMAL").sum()
            ),
            not_processed_records=(
                "monitoring_status",
                lambda x: (x == "NOT_PROCESSED").sum()
            ),
            unique_units=(
                "unit_id",
                "nunique"
            ) if "unit_id" in df.columns else (
                "monitoring_status",
                "size"
            ),
            unique_wafers=(
                "wafer_id",
                "nunique"
            ) if "wafer_id" in df.columns else (
                "monitoring_status",
                "size"
            )
        )
        .reset_index()
    )

    report["processed_records"] = (
        report["normal_records"]
        + report["abnormal_records"]
    )

    report["abnormal_percent"] = 0.0

    mask = report["processed_records"] > 0

    report.loc[
        mask,
        "abnormal_percent"
    ] = (
        report.loc[
            mask,
            "abnormal_records"
        ]
        / report.loc[
            mask,
            "processed_records"
        ]
        * 100
    ).round(2)

    report = report.sort_values(
        by="lot_id"
    )

    return save_report(
        report,
        "lot_monitoring_report.csv"
    )


# ============================================================
# FINAL SUMMARY REPORT
# ============================================================

def generate_summary_report(df):
    """
    Generate a compact overall monitoring summary CSV.
    """

    print()
    print("=" * 65)
    print("GENERATING OVERALL SUMMARY")
    print("=" * 65)

    total_records = len(df)

    normal_records = count_status(
        df,
        "monitoring_status",
        "NORMAL"
    )

    abnormal_records = count_status(
        df,
        "monitoring_status",
        "ABNORMAL"
    )

    not_processed_records = count_status(
        df,
        "monitoring_status",
        "NOT_PROCESSED"
    )

    processed_records = (
        normal_records
        + abnormal_records
    )

    monitoring_completion = 0.0

    if total_records > 0:
        monitoring_completion = (
            processed_records
            / total_records
            * 100
        )

    abnormal_percent = 0.0

    if processed_records > 0:
        abnormal_percent = (
            abnormal_records
            / processed_records
            * 100
        )

    unique_units = 0
    unique_lots = 0
    unique_wafers = 0
    unique_equipment = 0

    if "unit_id" in df.columns:
        unique_units = df["unit_id"].nunique()

    if "lot_id" in df.columns:
        unique_lots = df["lot_id"].nunique()

    if "wafer_id" in df.columns:
        unique_wafers = df["wafer_id"].nunique()

    if "equipment_id" in df.columns:
        unique_equipment = df["equipment_id"].nunique()

    summary = pd.DataFrame(
        [
            {
                "metric": "Total Records",
                "value": total_records
            },
            {
                "metric": "Unique Units",
                "value": unique_units
            },
            {
                "metric": "Unique Lots",
                "value": unique_lots
            },
            {
                "metric": "Unique Wafers",
                "value": unique_wafers
            },
            {
                "metric": "Unique Equipment",
                "value": unique_equipment
            },
            {
                "metric": "Normal Records",
                "value": normal_records
            },
            {
                "metric": "Abnormal Records",
                "value": abnormal_records
            },
            {
                "metric": "Not Processed Records",
                "value": not_processed_records
            },
            {
                "metric": "Processed Records",
                "value": processed_records
            },
            {
                "metric": "Monitoring Completion Percent",
                "value": round(
                    monitoring_completion,
                    2
                )
            },
            {
                "metric": "Abnormal Record Percent",
                "value": round(
                    abnormal_percent,
                    2
                )
            }
        ]
    )

    return save_report(
        summary,
        "overall_monitoring_summary.csv"
    )


# ============================================================
# DISPLAY STAGE SUMMARY
# ============================================================

def display_stage_summary(df):
    """
    Display a simple stage-by-stage summary in the terminal.
    """

    if "process_stage" not in df.columns:
        return

    print()
    print("=" * 65)
    print("STAGE-BY-STAGE MONITORING SUMMARY")
    print("=" * 65)

    stage_group = (
        df.groupby("process_stage")
        .agg(
            total_records=(
                "monitoring_status",
                "size"
            ),
            normal_records=(
                "monitoring_status",
                lambda x: (x == "NORMAL").sum()
            ),
            abnormal_records=(
                "monitoring_status",
                lambda x: (x == "ABNORMAL").sum()
            ),
            not_processed_records=(
                "monitoring_status",
                lambda x: (x == "NOT_PROCESSED").sum()
            )
        )
        .reset_index()
    )

    if "stage_number" in df.columns:

        stage_numbers = (
            df.groupby("process_stage")["stage_number"]
            .min()
            .reset_index()
        )

        stage_group = stage_group.merge(
            stage_numbers,
            on="process_stage",
            how="left"
        )

        stage_group = stage_group.sort_values(
            by="stage_number"
        )

    for _, row in stage_group.iterrows():

        stage_name = row["process_stage"]

        total = int(
            row["total_records"]
        )

        normal = int(
            row["normal_records"]
        )

        abnormal = int(
            row["abnormal_records"]
        )

        not_processed = int(
            row["not_processed_records"]
        )

        print()
        print(
            f"{stage_name}"
        )

        print(
            f"  Total        : {total:,}"
        )

        print(
            f"  Normal       : {normal:,}"
        )

        print(
            f"  Abnormal     : {abnormal:,}"
        )

        print(
            f"  Not processed: {not_processed:,}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 65)
    print("OSAT / ATMP MONITORING REPORT GENERATOR")
    print("=" * 65)

    # Create output directory if required
    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    # Load data
    df = load_monitoring_data()

    # Prepare data
    df = prepare_data(df)

    # General summary
    generate_general_summary(df)

    # Stage summary in terminal
    display_stage_summary(df)

    # Generate all reports
    generate_stage_report(df)

    generate_parameter_report(df)

    generate_equipment_report(df)

    generate_shift_report(df)

    generate_operation_report(df)

    generate_abnormal_report(df)

    generate_unit_report(df)

    generate_lot_report(df)

    generate_summary_report(df)

    # Final message
    print()
    print("=" * 65)
    print("REPORT GENERATION COMPLETE")
    print("=" * 65)

    print()
    print("Reports saved in:")
    print(OUTPUT_DIR)

    print()
    print("Generated reports:")

    report_files = [
        "stage_monitoring_report.csv",
        "parameter_monitoring_report.csv",
        "equipment_monitoring_report.csv",
        "shift_monitoring_report.csv",
        "operation_monitoring_report.csv",
        "abnormal_conditions_report.csv",
        "unit_monitoring_report.csv",
        "lot_monitoring_report.csv",
        "overall_monitoring_summary.csv"
    ]

    for index, filename in enumerate(
        report_files,
        start=1
    ):
        full_path = os.path.join(
            OUTPUT_DIR,
            filename
        )

        if os.path.exists(full_path):
            print(
                f"{index}. {filename}"
            )

    print()
    print("=" * 65)
    print("OSAT / ATMP MONITORING REPORT GENERATION FINISHED")
    print("=" * 65)


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()