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
