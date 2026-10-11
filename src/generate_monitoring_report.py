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
