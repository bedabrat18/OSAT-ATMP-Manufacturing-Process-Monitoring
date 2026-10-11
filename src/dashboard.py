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
