import os
import pandas as pd


# ============================================================
# OSAT / ATMP MANUFACTURING MONITORING ENGINE
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_FILE = os.path.join(
    BASE_DIR,
    "data",
    "osat_atmp_process_data.csv"
)

LIMITS_FILE = os.path.join(
    BASE_DIR,
    "config",
    "process_limits.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "monitoring_reports"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "process_monitoring_results.csv"
)


# ------------------------------------------------------------
# 1. Load data
# ------------------------------------------------------------

print("=" * 60)
print("OSAT / ATMP PROCESS MONITORING ENGINE")
print("=" * 60)

print("\nLoading manufacturing data...")

df = pd.read_csv(DATA_FILE)

print(f"Manufacturing records loaded: {len(df):,}")


# ------------------------------------------------------------
# 2. Load process limits
# ------------------------------------------------------------

print("\nLoading process limits...")

limits_df = pd.read_csv(LIMITS_FILE)

print(f"Configured monitoring limits: {len(limits_df)}")


# ------------------------------------------------------------
# 3. Create lookup dictionary
# ------------------------------------------------------------

limits_lookup = {}

for _, row in limits_df.iterrows():

    key = (
        row["process_stage"],
        row["parameter"]
    )

    limits_lookup[key] = {
        "lower": row["lower_limit"],
        "upper": row["upper_limit"],
        "unit": row["unit"]
    }


# ------------------------------------------------------------
# 4. Parameter columns
# ------------------------------------------------------------

parameter_columns = limits_df["parameter"].unique().tolist()


# ------------------------------------------------------------
# 5. Monitor each manufacturing record
# ------------------------------------------------------------

monitoring_status = []
abnormal_parameters = []
abnormal_count = []


for _, row in df.iterrows():

    stage = row["process_stage"]

    # NOT_PROCESSED records are not monitored
    if row["process_status"] == "NOT_PROCESSED":

        monitoring_status.append("NOT_PROCESSED")
        abnormal_parameters.append("")
        abnormal_count.append(0)

        continue

    abnormal_list = []

    for parameter in parameter_columns:

        key = (stage, parameter)

        # Parameter is not applicable to this stage
        if key not in limits_lookup:
            continue

        value = row.get(parameter)

        # Missing value is ignored
        if pd.isna(value):
            continue

        limits = limits_lookup[key]

        lower = limits["lower"]
        upper = limits["upper"]

        if value < lower or value > upper:

            abnormal_list.append(
                f"{parameter}={value}"
            )

    if len(abnormal_list) == 0:

        monitoring_status.append("NORMAL")
        abnormal_parameters.append("")
        abnormal_count.append(0)

    else:

        monitoring_status.append("ABNORMAL")
        abnormal_parameters.append(
            "; ".join(abnormal_list)
        )
        abnormal_count.append(
            len(abnormal_list)
        )


# ------------------------------------------------------------
# 6. Add monitoring results
# ------------------------------------------------------------

df["monitoring_status"] = monitoring_status

df["abnormal_parameter_count"] = abnormal_count

df["abnormal_parameters"] = abnormal_parameters


# ------------------------------------------------------------
# 7. Create monitoring summary fields
# ------------------------------------------------------------

df["is_monitored"] = (
    df["monitoring_status"] != "NOT_PROCESSED"
)

df["is_abnormal"] = (
    df["monitoring_status"] == "ABNORMAL"
)


# ------------------------------------------------------------
# 8. Save monitoring results
# ------------------------------------------------------------

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ------------------------------------------------------------
# 9. Display monitoring summary
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("MONITORING SUMMARY")
print("=" * 60)

print("\nMonitoring Status:")

print(
    df["monitoring_status"].value_counts()
)


print("\nMonitored records:")

print(
    df["is_monitored"].value_counts()
)


print("\nAbnormal records:")

print(
    df["is_abnormal"].value_counts()
)


print("\nAbnormal records by process stage:")

abnormal_stage = (
    df[df["monitoring_status"] == "ABNORMAL"]
    ["process_stage"]
    .value_counts()
)

print(abnormal_stage)


print("\nOSAT / ATMP classification:")

print(
    df["operation_type"].value_counts()
)


print("\nOutput saved to:")

print(OUTPUT_FILE)

print("=" * 60)