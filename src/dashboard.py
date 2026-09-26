import os
import pandas as pd
import streamlit as st


# ============================================================
# OSAT / ATMP MANUFACTURING PROCESS MONITORING SYSTEM
# ============================================================
#
# Monitoring-only project
#
# Includes:
#   - OSAT / ATMP classification
#   - 16-stage process monitoring
#   - Process parameter monitoring
#   - Wafer metrology
#   - Equipment monitoring
#   - Shift monitoring
#   - Unit / lot / wafer monitoring
#   - Normal / abnormal status
#   - Current process-flow status
#
# Does NOT include:
#   - Machine learning
#   - Prediction
#   - Risk scoring
#   - Root-cause analysis
#   - Yield analysis
#
# ============================================================


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_FILE = os.path.join(
    BASE_DIR,
    "outputs",
    "monitoring_reports",
    "process_monitoring_results.csv"
)

LIMITS_FILE = os.path.join(
    BASE_DIR,
    "config",
    "process_limits.csv"
)

CLASSIFICATION_FILE = os.path.join(
    BASE_DIR,
    "config",
    "process_classification.csv"
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="OSAT / ATMP Process Monitoring",
    page_icon="🏭",
    layout="wide"
)


# ============================================================
# PROFESSIONAL DASHBOARD STYLING
# ============================================================

st.markdown("""
<style>
    .main-title {
        font-size: 2.15rem;
        font-weight: 700;
        margin-bottom: 0.15rem;
    }
    .main-subtitle {
        font-size: 1rem;
        opacity: 0.78;
        margin-bottom: 1.1rem;
    }
    .section-note {
        padding: 0.65rem 0.9rem;
        border-left: 4px solid #4b78a8;
        background: rgba(127,127,127,0.08);
        border-radius: 0.35rem;
        margin-bottom: 0.8rem;
    }
    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,0.22);
        border-radius: 0.65rem;
        padding: 0.75rem 0.9rem;
        background: rgba(128,128,128,0.035);
    }
    .status-banner {
        padding: 0.75rem 1rem;
        border-radius: 0.55rem;
        border: 1px solid rgba(128,128,128,0.22);
        margin: 0.4rem 0 1rem 0;
    }
    .small-label {
        font-size: 0.78rem;
        opacity: 0.68;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_monitoring_data():

    df = pd.read_csv(DATA_FILE)

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    return df


@st.cache_data
def load_limits():

    return pd.read_csv(
        LIMITS_FILE
    )


@st.cache_data
def load_classification():

    return pd.read_csv(
        CLASSIFICATION_FILE
    )


df = load_monitoring_data()
limits_df = load_limits()
classification_df = load_classification()


# ============================================================
# PROCESS FLOW
# ============================================================

PROCESS_FLOW = [
    "Wafer Inspection",
    "Wafer Sort",
    "Back Grinding",
    "Wafer Dicing",
    "Die Attach",
    "Wire Bonding",
    "Encapsulation / Molding",
    "Marking",
    "Singulation",
    "Package Inspection",
    "Burn-in",
    "ICT",
    "FCT",
    "EOL",
    "Final Inspection",
    "Packing / Dispatch"
]


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="main-title">🏭 OSAT / ATMP Manufacturing Process Monitoring System</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="main-subtitle">Digital monitoring of semiconductor assembly, packaging, inspection, testing and wafer metrology operations.</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-note"><b>Monitoring scope:</b> Process status, parameter conditions, equipment, units, lots, wafers and shifts. This dashboard is monitoring-only and does not perform prediction, yield analysis, risk scoring or root-cause analysis.</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header(
    "🔎 Monitoring Filters"
)


# ------------------------------------------------------------
# Operation Type
# ------------------------------------------------------------

operation_options = sorted(
    df["operation_type"]
    .dropna()
    .unique()
    .tolist()
)

selected_operation = st.sidebar.multiselect(
    "Operation Type",
    operation_options,
    default=operation_options
)


# ------------------------------------------------------------
# Process Stage
# ------------------------------------------------------------

stage_options = [
    stage
    for stage in PROCESS_FLOW
    if stage in df["process_stage"].unique()
]

selected_stage = st.sidebar.multiselect(
    "Process Stage",
    stage_options,
    default=stage_options
)


# ------------------------------------------------------------
# Shift
# ------------------------------------------------------------

shift_options = sorted(
    df["shift"]
    .dropna()
    .unique()
    .tolist()
)

selected_shift = st.sidebar.multiselect(
    "Shift",
    shift_options,
    default=shift_options
)


# ------------------------------------------------------------
# Equipment
# ------------------------------------------------------------

equipment_options = sorted(
    df["equipment_id"]
    .dropna()
    .unique()
    .tolist()
)

selected_equipment = st.sidebar.multiselect(
    "Equipment",
    equipment_options,
    default=equipment_options
)


# ------------------------------------------------------------
# Monitoring Status
# ------------------------------------------------------------

status_options = [
    "NORMAL",
    "ABNORMAL",
    "NOT_PROCESSED"
]

selected_status = st.sidebar.multiselect(
    "Monitoring Status",
    status_options,
    default=status_options
)


# ============================================================
# DASHBOARD STATUS LEGEND
# ============================================================

st.sidebar.divider()
st.sidebar.caption("STATUS LEGEND")
st.sidebar.markdown(
    "**NORMAL** — within configured monitoring limits  \n"
    "\n\n**ABNORMAL** — outside configured monitoring limits  \n"
    "\n\n**NOT_PROCESSED** — stage has not yet been processed"
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df[
    df["operation_type"].isin(
        selected_operation
    )
    &
    df["process_stage"].isin(
        selected_stage
    )
    &
    df["shift"].isin(
        selected_shift
    )
    &
    df["equipment_id"].isin(
        selected_equipment
    )
    &
    df["monitoring_status"].isin(
        selected_status
    )
].copy()


# ============================================================
# 1. PRODUCTION MONITORING
# ============================================================

st.header(
    "📊 Production Monitoring"
)

col1, col2, col3, col4, col5, col6 = st.columns(6)

normal_total = int((filtered_df["monitoring_status"] == "NORMAL").sum())
abnormal_total = int((filtered_df["monitoring_status"] == "ABNORMAL").sum())
not_processed_total = int((filtered_df["monitoring_status"] == "NOT_PROCESSED").sum())
processed_total = normal_total + abnormal_total
processed_pct = (processed_total / len(filtered_df) * 100) if len(filtered_df) else 0
abnormal_pct = (abnormal_total / processed_total * 100) if processed_total else 0

with col1:
    st.metric("Units", f"{filtered_df['unit_id'].nunique():,}")

with col2:
    st.metric("Lots", f"{filtered_df['lot_id'].nunique():,}")

with col3:
    st.metric("Wafers", f"{filtered_df['wafer_id'].nunique():,}")

with col4:
    st.metric("Process Records", f"{len(filtered_df):,}")

with col5:
    st.metric("Processed", f"{processed_pct:.1f}%")

with col6:
    st.metric("Abnormal", f"{abnormal_pct:.1f}%")

if not filtered_df.empty:
    min_time = filtered_df["timestamp"].min()
    max_time = filtered_df["timestamp"].max()
    st.caption(
        f"Monitoring records in selected scope: {min_time:%d %b %Y %H:%M} → {max_time:%d %b %Y %H:%M}"
    )


# ============================================================
# 2. MONITORING STATUS
# ============================================================

st.header(
    "🚦 Monitoring Status"
)

status_counts = (
    filtered_df["monitoring_status"]
    .value_counts()
)


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("NORMAL", f"{status_counts.get('NORMAL', 0):,}")

with col2:
    st.metric("ABNORMAL", f"{status_counts.get('ABNORMAL', 0):,}")

with col3:
    st.metric("NOT PROCESSED", f"{status_counts.get('NOT_PROCESSED', 0):,}")

with col4:
    st.metric("Monitored Records", f"{processed_total:,}")

status_chart = pd.DataFrame({
    "Records": [
        status_counts.get("NORMAL", 0),
        status_counts.get("ABNORMAL", 0),
        status_counts.get("NOT_PROCESSED", 0)
    ]
}, index=["NORMAL", "ABNORMAL", "NOT_PROCESSED"])

st.bar_chart(status_chart)


# ============================================================
# 3. OSAT / ATMP CLASSIFICATION
# ============================================================

st.header(
    "🏭 OSAT / ATMP Operation Classification"
)


operation_counts = (
    filtered_df["operation_type"]
    .value_counts()
)


col1, col2 = st.columns(2)


with col1:

    st.subheader(
        "Operation Distribution"
    )

    st.bar_chart(
        operation_counts
    )


with col2:

    st.subheader(
        "Operation Summary"
    )

    operation_summary = (
        filtered_df
        .groupby(
            "operation_type"
        )
        .agg(
            records=(
                "operation_type",
                "size"
            ),
            units=(
                "unit_id",
                "nunique"
            ),
            lots=(
                "lot_id",
                "nunique"
            ),
            wafers=(
                "wafer_id",
                "nunique"
            )
        )
        .reset_index()
    )

    st.dataframe(
        operation_summary,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# 4. OSAT / ATMP PROCESS FLOW MONITORING
# ============================================================

st.header(
    "🔄 OSAT / ATMP Process Flow Monitoring"
)

st.caption(
    "Current monitoring status of the 16 semiconductor "
    "assembly, packaging, inspection and testing stages."
)


# ------------------------------------------------------------
# Determine CURRENT status of every stage
# ------------------------------------------------------------

flow_data = []


for stage in PROCESS_FLOW:

    stage_data = filtered_df[
        filtered_df["process_stage"] == stage
    ].copy()

    if stage_data.empty:

        stage_status = "NO DATA"
        abnormal_count = 0
        normal_count = 0
        processed_count = 0
        latest_time = None

    else:

        # Historical abnormal count
        abnormal_count = (
            stage_data["monitoring_status"]
            == "ABNORMAL"
        ).sum()

        normal_count = (
            stage_data["monitoring_status"]
            == "NORMAL"
        ).sum()

        # Only processed records are considered
        processed_stage_data = stage_data[
            stage_data["monitoring_status"]
            != "NOT_PROCESSED"
        ].copy()

        processed_count = len(
            processed_stage_data
        )

        if processed_stage_data.empty:

            stage_status = "NOT PROCESSED"
            latest_time = None

        else:

            # Sort by time
            processed_stage_data = (
                processed_stage_data
                .sort_values(
                    "timestamp",
                    ascending=False
                )
            )

            # Latest processed record
            latest_record = (
                processed_stage_data
                .iloc[0]
            )

            stage_status = (
                latest_record[
                    "monitoring_status"
                ]
            )

            latest_time = (
                latest_record[
                    "timestamp"
                ]
            )

    flow_data.append(
        {
            "stage": stage,
            "status": stage_status,
            "abnormal_count": abnormal_count,
            "normal_count": normal_count,
            "processed_count": processed_count,
            "latest_time": latest_time
        }
    )


# ------------------------------------------------------------
# Display current process-flow status
# ------------------------------------------------------------

for start in range(
    0,
    len(flow_data),
    4
):

    group = flow_data[
        start:start + 4
    ]

    columns = st.columns(
        len(group)
    )

    for column, item in zip(
        columns,
        group
    ):

        with column:

            # NORMAL
            if item["status"] == "NORMAL":

                st.success(
                    f"🟢 {item['stage']}"
                )

                st.write(
                    "**Current Status:** NORMAL"
                )

            # ABNORMAL
            elif item["status"] == "ABNORMAL":

                st.error(
                    f"🔴 {item['stage']}"
                )

                st.write(
                    "**Current Status:** ABNORMAL"
                )

            # NOT PROCESSED
            elif item["status"] == "NOT PROCESSED":

                st.warning(
                    f"⚪ {item['stage']}"
                )

                st.write(
                    "**Current Status:** NOT PROCESSED"
                )

            # NO DATA
            else:

                st.info(
                    f"⚫ {item['stage']}"
                )

                st.write(
                    "**Current Status:** NO DATA"
                )

            st.caption(
                f"Processed: "
                f"{item['processed_count']:,}"
            )

            st.caption(
                f"Normal records: "
                f"{item['normal_count']:,}"
            )

            st.caption(
                f"Abnormal records: "
                f"{item['abnormal_count']:,}"
            )


# ============================================================
# 5. PROCESS STAGE MONITORING
# ============================================================

st.header(
    "⚙️ Process Stage Monitoring"
)


stage_monitoring = (
    filtered_df
    .groupby(
        [
            "stage_number",
            "process_stage",
            "operation_type"
        ],
        dropna=False
    )
    .agg(
        records=(
            "process_stage",
            "size"
        ),
        normal_records=(
            "monitoring_status",
            lambda x:
                (x == "NORMAL").sum()
        ),
        abnormal_records=(
            "monitoring_status",
            lambda x:
                (x == "ABNORMAL").sum()
        ),
        not_processed=(
            "monitoring_status",
            lambda x:
                (x == "NOT_PROCESSED").sum()
        )
    )
    .reset_index()
    .sort_values(
        "stage_number"
    )
)


st.dataframe(
    stage_monitoring,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 6. PROCESS STATUS BY STAGE
# ============================================================

st.subheader(
    "Process Status by Stage"
)


process_status_table = (
    filtered_df
    .groupby(
        "process_stage"
    )[
        "process_status"
    ]
    .value_counts()
    .unstack(
        fill_value=0
    )
    .reset_index()
)


st.dataframe(
    process_status_table,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 7. WAFER METROLOGY MONITORING
# ============================================================

st.header(
    "🔬 Wafer Metrology Monitoring"
)

st.caption(
    "Monitoring of wafer geometry and wafer/tape "
    "measurement parameters."
)


metrology_parameters = {

    "wafer_thickness_um":
        "Wafer Thickness",

    "ttv_um":
        "Total Thickness Variation (TTV)",

    "bow_um":
        "Bow",

    "warp_um":
        "Warp",

    "tape_thickness_um":
        "Tape Thickness"
}


def get_limit(parameter):

    matches = limits_df[
        limits_df["parameter"] == parameter
    ]

    if matches.empty:

        return None, None, None

    return (
        matches[
            "lower_limit"
        ].iloc[0],

        matches[
            "upper_limit"
        ].iloc[0],

        matches[
            "unit"
        ].iloc[0]
    )


for parameter, display_name in (
    metrology_parameters.items()
):

    if parameter not in filtered_df.columns:

        continue

    parameter_data = filtered_df[
        filtered_df[parameter].notna()
    ].copy()

    if parameter_data.empty:

        continue

    lower_limit, upper_limit, unit = (
        get_limit(parameter)
    )

    if lower_limit is None:

        continue

    normal_count = (
        (
            parameter_data[parameter]
            >= lower_limit
        )
        &
        (
            parameter_data[parameter]
            <= upper_limit
        )
    ).sum()

    abnormal_count = (
        (
            parameter_data[parameter]
            < lower_limit
        )
        |
        (
            parameter_data[parameter]
            > upper_limit
        )
    ).sum()

    average_value = (
        parameter_data[parameter]
        .mean()
    )

    minimum_value = (
        parameter_data[parameter]
        .min()
    )

    maximum_value = (
        parameter_data[parameter]
        .max()
    )

    st.subheader(
        display_name
    )

    col1, col2, col3, col4, col5 = (
        st.columns(5)
    )

    with col1:

        st.metric(
            "Average",
            f"{average_value:.2f} {unit}"
        )

    with col2:

        st.metric(
            "Minimum",
            f"{minimum_value:.2f} {unit}"
        )

    with col3:

        st.metric(
            "Maximum",
            f"{maximum_value:.2f} {unit}"
        )

    with col4:

        st.metric(
            "NORMAL",
            f"{normal_count:,}"
        )

    with col5:

        st.metric(
            "ABNORMAL",
            f"{abnormal_count:,}"
        )

    st.caption(
        f"Configured monitoring range: "
        f"{lower_limit} – {upper_limit} {unit}"
    )

    st.divider()


# ============================================================
# 8. PROCESS PARAMETER MONITORING
# ============================================================

st.header(
    "📈 Process Parameter Monitoring"
)

st.caption(
    "Select a process parameter to inspect its "
    "configured operating range and current measurements."
)


available_parameters = []


for parameter in limits_df[
    "parameter"
].unique():

    if parameter in filtered_df.columns:

        if filtered_df[
            parameter
        ].notna().any():

            available_parameters.append(
                parameter
            )


if available_parameters:

    selected_parameter = st.selectbox(
        "Select Parameter",
        available_parameters
    )

    selected_limits = limits_df[
        limits_df[
            "parameter"
        ] == selected_parameter
    ]

    parameter_data = filtered_df[
        filtered_df[
            selected_parameter
        ].notna()
    ].copy()

    if not selected_limits.empty:

        lower_limit = (
            selected_limits[
                "lower_limit"
            ].iloc[0]
        )

        upper_limit = (
            selected_limits[
                "upper_limit"
            ].iloc[0]
        )

        unit = (
            selected_limits[
                "unit"
            ].iloc[0]
        )

        normal_count = (
            (
                parameter_data[
                    selected_parameter
                ] >= lower_limit
            )
            &
            (
                parameter_data[
                    selected_parameter
                ] <= upper_limit
            )
        ).sum()

        abnormal_count = (
            (
                parameter_data[
                    selected_parameter
                ] < lower_limit
            )
            |
            (
                parameter_data[
                    selected_parameter
                ] > upper_limit
            )
        ).sum()

        average_value = (
            parameter_data[
                selected_parameter
            ].mean()
        )

        minimum_value = (
            parameter_data[
                selected_parameter
            ].min()
        )

        maximum_value = (
            parameter_data[
                selected_parameter
            ].max()
        )

        col1, col2, col3, col4, col5 = (
            st.columns(5)
        )

        with col1:

            st.metric(
                "Average",
                f"{average_value:.3f} {unit}"
            )

        with col2:

            st.metric(
                "Minimum",
                f"{minimum_value:.3f} {unit}"
            )

        with col3:

            st.metric(
                "Maximum",
                f"{maximum_value:.3f} {unit}"
            )

        with col4:

            st.metric(
                "NORMAL",
                f"{normal_count:,}"
            )

        with col5:

            st.metric(
                "ABNORMAL",
                f"{abnormal_count:,}"
            )

        st.info(
            f"Configured range: "
            f"{lower_limit} – {upper_limit} {unit}"
        )

        parameter_view = parameter_data[
            [
                "timestamp",
                "unit_id",
                "lot_id",
                "wafer_id",
                "process_stage",
                "operation_type",
                "equipment_id",
                "shift",
                selected_parameter
            ]
        ].copy()

        parameter_view[
            "parameter_status"
        ] = parameter_view[
            selected_parameter
        ].apply(
            lambda x:
                "NORMAL"
                if lower_limit <= x <= upper_limit
                else "ABNORMAL"
        )

        st.subheader(
            "Parameter Measurements"
        )

        st.dataframe(
            parameter_view
            .sort_values(
                "timestamp",
                ascending=False
            )
            .head(200),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# 9. EQUIPMENT MONITORING
# ============================================================

st.header(
    "🛠️ Equipment Monitoring"
)


equipment_monitoring = (
    filtered_df
    .groupby(
        [
            "equipment_id",
            "process_stage"
        ]
    )
    .agg(
        records=(
            "equipment_id",
            "size"
        ),
        units=(
            "unit_id",
            "nunique"
        ),
        normal=(
            "monitoring_status",
            lambda x:
                (x == "NORMAL").sum()
        ),
        abnormal=(
            "monitoring_status",
            lambda x:
                (x == "ABNORMAL").sum()
        ),
        not_processed=(
            "monitoring_status",
            lambda x:
                (x == "NOT_PROCESSED").sum()
        )
    )
    .reset_index()
)


st.dataframe(
    equipment_monitoring,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 10. SHIFT MONITORING
# ============================================================

st.header(
    "🕐 Shift Monitoring"
)


shift_monitoring = (
    filtered_df
    .groupby(
        "shift"
    )
    .agg(
        records=(
            "shift",
            "size"
        ),
        units=(
            "unit_id",
            "nunique"
        ),
        normal=(
            "monitoring_status",
            lambda x:
                (x == "NORMAL").sum()
        ),
        abnormal=(
            "monitoring_status",
            lambda x:
                (x == "ABNORMAL").sum()
        ),
        not_processed=(
            "monitoring_status",
            lambda x:
                (x == "NOT_PROCESSED").sum()
        )
    )
    .reset_index()
)


st.dataframe(
    shift_monitoring,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 11. ABNORMAL CONDITIONS
# ============================================================

st.header(
    "⚠️ Abnormal Conditions"
)


abnormal_df = filtered_df[
    filtered_df[
        "monitoring_status"
    ] == "ABNORMAL"
].copy()


if abnormal_df.empty:

    st.success(
        "No abnormal conditions detected "
        "for the selected filters."
    )

else:

    abnormal_columns = [

        "timestamp",
        "unit_id",
        "lot_id",
        "wafer_id",
        "process_stage",
        "operation_type",
        "equipment_id",
        "shift",
        "abnormal_parameter_count",
        "abnormal_parameters"
    ]

    available_columns = [
        col
        for col in abnormal_columns
        if col in abnormal_df.columns
    ]

    st.dataframe(
        abnormal_df[
            available_columns
        ]
        .sort_values(
            "timestamp",
            ascending=False
        )
        .head(200),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# 12. RECENT PROCESSED MONITORING RECORDS
# ============================================================

st.header(
    "🧾 Recent Processed Monitoring Records"
)

st.caption(
    "Latest records that were actually processed. "
    "NOT_PROCESSED stages are excluded from this view."
)


recent_processed = filtered_df[
    filtered_df[
        "monitoring_status"
    ] != "NOT_PROCESSED"
].copy()


recent_columns = [

    "timestamp",
    "unit_id",
    "lot_id",
    "wafer_id",
    "process_stage",
    "operation_type",
    "equipment_id",
    "shift",
    "process_status",
    "monitoring_status"
]


available_recent_columns = [
    col
    for col in recent_columns
    if col in recent_processed.columns
]


if recent_processed.empty:

    st.info(
        "No processed records are available "
        "for the selected filters."
    )

else:

    st.dataframe(
        recent_processed[
            available_recent_columns
        ]
        .sort_values(
            "timestamp",
            ascending=False
        )
        .head(100),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# 13. MONITORING REPORT EXPLORER
# ============================================================

st.header(
    "📑 Monitoring Reports Explorer"
)

st.caption(
    "View and download the monitoring reports generated by "
    "generate_monitoring_report.py."
)

REPORT_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "monitoring_reports"
)

REPORT_FILES = {
    "Overall Monitoring Summary": "overall_monitoring_summary.csv",
    "Stage Monitoring": "stage_monitoring_report.csv",
    "Parameter Monitoring": "parameter_monitoring_report.csv",
    "Equipment Monitoring": "equipment_monitoring_report.csv",
    "Shift Monitoring": "shift_monitoring_report.csv",
    "OSAT / ATMP Operation Monitoring": "operation_monitoring_report.csv",
    "Abnormal Conditions": "abnormal_conditions_report.csv",
    "Unit Monitoring": "unit_monitoring_report.csv",
    "Lot Monitoring": "lot_monitoring_report.csv"
}


@st.cache_data
def load_report(report_path):
    return pd.read_csv(report_path)


available_reports = []

for report_name, report_filename in REPORT_FILES.items():

    report_path = os.path.join(
        REPORT_DIR,
        report_filename
    )

    if os.path.exists(report_path):
        available_reports.append(report_name)


if not available_reports:

    st.warning(
        "No monitoring reports were found. "
        "Run 'python src\\generate_monitoring_report.py' "
        "to generate the reports."
    )

else:

    report_col1, report_col2 = st.columns(
        [2, 1]
    )

    with report_col1:

        selected_report = st.selectbox(
            "Select Monitoring Report",
            available_reports
        )

    selected_report_file = REPORT_FILES[
        selected_report
    ]

    selected_report_path = os.path.join(
        REPORT_DIR,
        selected_report_file
    )

    report_df = load_report(
        selected_report_path
    )

    with report_col2:

        st.metric(
            "Report Records",
            f"{len(report_df):,}"
        )

    st.subheader(
        f"📄 {selected_report}"
    )

    st.caption(
        f"Source file: {selected_report_file}"
    )

    # --------------------------------------------------------
    # Report-specific information
    # --------------------------------------------------------

    if selected_report == "Overall Monitoring Summary":

        st.dataframe(
            report_df,
            use_container_width=True,
            hide_index=True
        )

    elif selected_report == "Stage Monitoring":

        if "process_stage" in report_df.columns:

            selected_report_stages = st.multiselect(
                "Filter Report by Process Stage",
                sorted(
                    report_df[
                        "process_stage"
                    ].dropna().unique().tolist()
                ),
                default=sorted(
                    report_df[
                        "process_stage"
                    ].dropna().unique().tolist()
                ),
                key="report_stage_filter"
            )

            report_view = report_df[
                report_df[
                    "process_stage"
                ].isin(
                    selected_report_stages
                )
            ].copy()

        else:

            report_view = report_df.copy()

        st.dataframe(
            report_view,
            use_container_width=True,
            hide_index=True
        )

    elif selected_report == "Parameter Monitoring":

        if "parameter" in report_df.columns:

            selected_parameters = st.multiselect(
                "Filter Parameters",
                sorted(
                    report_df[
                        "parameter"
                    ].dropna().unique().tolist()
                ),
                default=sorted(
                    report_df[
                        "parameter"
                    ].dropna().unique().tolist()
                ),
                key="report_parameter_filter"
            )

            report_view = report_df[
                report_df[
                    "parameter"
                ].isin(
                    selected_parameters
                )
            ].copy()

        else:

            report_view = report_df.copy()

        st.dataframe(
            report_view,
            use_container_width=True,
            hide_index=True
        )

    elif selected_report == "Equipment Monitoring":

        if "equipment_id" in report_df.columns:

            selected_report_equipment = st.multiselect(
                "Filter Equipment",
                sorted(
                    report_df[
                        "equipment_id"
                    ].dropna().unique().tolist()
                ),
                default=sorted(
                    report_df[
                        "equipment_id"
                    ].dropna().unique().tolist()
                ),
                key="report_equipment_filter"
            )

            report_view = report_df[
                report_df[
                    "equipment_id"
                ].isin(
                    selected_report_equipment
                )
            ].copy()

        else:

            report_view = report_df.copy()

        st.dataframe(
            report_view,
            use_container_width=True,
            hide_index=True
        )

    elif selected_report == "Shift Monitoring":

        if "shift" in report_df.columns:

            selected_report_shifts = st.multiselect(
                "Filter Shift",
                sorted(
                    report_df[
                        "shift"
                    ].dropna().unique().tolist()
                ),
                default=sorted(
                    report_df[
                        "shift"
                    ].dropna().unique().tolist()
                ),
                key="report_shift_filter"
            )

            report_view = report_df[
                report_df[
                    "shift"
                ].isin(
                    selected_report_shifts
                )
            ].copy()

        else:

            report_view = report_df.copy()

        st.dataframe(
            report_view,
            use_container_width=True,
            hide_index=True
        )

    elif selected_report == "OSAT / ATMP Operation Monitoring":

        if "operation_type" in report_df.columns:

            selected_report_operations = st.multiselect(
                "Filter Operation Type",
                sorted(
                    report_df[
                        "operation_type"
                    ].dropna().unique().tolist()
                ),
                default=sorted(
                    report_df[
                        "operation_type"
                    ].dropna().unique().tolist()
                ),
                key="report_operation_filter"
            )

            report_view = report_df[
                report_df[
                    "operation_type"
                ].isin(
                    selected_report_operations
                )
            ].copy()

        else:

            report_view = report_df.copy()

        st.dataframe(
            report_view,
            use_container_width=True,
            hide_index=True
        )

    elif selected_report == "Abnormal Conditions":

        st.warning(
            "This report contains records with "
            "ABNORMAL monitoring status."
        )

        report_view = report_df.copy()

        if "process_stage" in report_view.columns:

            abnormal_stage_options = sorted(
                report_view[
                    "process_stage"
                ].dropna().unique().tolist()
            )

            selected_abnormal_stages = st.multiselect(
                "Filter Abnormal Conditions by Stage",
                abnormal_stage_options,
                default=abnormal_stage_options,
                key="report_abnormal_stage_filter"
            )

            report_view = report_view[
                report_view[
                    "process_stage"
                ].isin(
                    selected_abnormal_stages
                )
            ].copy()

        st.dataframe(
            report_view.head(1000),
            use_container_width=True,
            hide_index=True
        )

        if len(report_view) > 1000:

            st.caption(
                "Showing the first 1,000 filtered abnormal "
                "records in the dashboard. Download the CSV "
                "for the complete report."
            )

    elif selected_report == "Unit Monitoring":

        report_view = report_df.copy()

        if "current_monitoring_status" in report_view.columns:

            unit_status_options = sorted(
                report_view[
                    "current_monitoring_status"
                ].dropna().unique().tolist()
            )

            selected_unit_status = st.multiselect(
                "Filter Unit Monitoring Status",
                unit_status_options,
                default=unit_status_options,
                key="report_unit_status_filter"
            )

            report_view = report_view[
                report_view[
                    "current_monitoring_status"
                ].isin(
                    selected_unit_status
                )
            ].copy()

        st.dataframe(
            report_view.head(1000),
            use_container_width=True,
            hide_index=True
        )

        if len(report_view) > 1000:

            st.caption(
                "Showing the first 1,000 unit records in the "
                "dashboard. Download the CSV for the complete report."
            )

    elif selected_report == "Lot Monitoring":

        report_view = report_df.copy()

        if "operation_type" in report_view.columns:

            lot_operation_options = sorted(
                report_view[
                    "operation_type"
                ].dropna().unique().tolist()
            )

            selected_lot_operations = st.multiselect(
                "Filter Lot Operation Type",
                lot_operation_options,
                default=lot_operation_options,
                key="report_lot_operation_filter"
            )

            report_view = report_view[
                report_view[
                    "operation_type"
                ].isin(
                    selected_lot_operations
                )
            ].copy()

        st.dataframe(
            report_view,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.dataframe(
            report_df,
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # Download selected report
    # --------------------------------------------------------

    report_download_data = report_df.to_csv(
        index=False
    ).encode(
        "utf-8"
    )

    st.download_button(
        label="⬇️ Download Selected Report CSV",
        data=report_download_data,
        file_name=selected_report_file,
        mime="text/csv",
        key="download_selected_monitoring_report"
    )

    st.divider()


# ============================================================
# 14. OSAT / ATMP PROCESS CLASSIFICATION REFERENCE
# ============================================================

st.header(
    "📋 OSAT / ATMP Process Classification"
)


st.dataframe(
    classification_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Synthetic manufacturing-monitoring dataset. "
    "Process limits are project configuration values "
    "for demonstration and are not actual production "
    "specifications."
)

st.caption(
    "Project scope: OSAT / ATMP manufacturing process "
    "monitoring and wafer metrology. "
    "No machine-learning prediction, risk scoring, "
    "root-cause analysis or yield prediction is used."
)