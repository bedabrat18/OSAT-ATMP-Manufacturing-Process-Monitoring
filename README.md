# OSAT / ATMP Manufacturing Process Monitoring System

## Personal / Portfolio Project

A Python and Streamlit-based digital monitoring system designed to track semiconductor assembly, packaging, inspection, and testing operations across an OSAT/ATMP manufacturing flow.

The system monitors manufacturing records, process stages, equipment, shifts, units, lots, wafers, and selected process parameters. Configured process limits are used to classify monitored conditions as **NORMAL**, **ABNORMAL**, or **NOT_PROCESSED**.

---

## Project Overview

Semiconductor assembly and packaging involve multiple manufacturing stages, equipment, process parameters, inspection operations, and testing activities.

This project provides a centralized monitoring interface for an OSAT/ATMP manufacturing process.

The system represents a 16-stage manufacturing flow:

1. Wafer Inspection
2. Wafer Sort
3. Back Grinding
4. Wafer Dicing
5. Die Attach
6. Wire Bonding
7. Encapsulation / Molding
8. Marking
9. Singulation
10. Package Inspection
11. Burn-in
12. ICT
13. FCT
14. EOL
15. Final Inspection
16. Packing / Dispatch

---

## Objectives

The main objective is to develop a digital manufacturing monitoring system that can:

- Track semiconductor manufacturing process stages
- Monitor units, lots, wafers, and packages
- Track manufacturing equipment
- Monitor production shifts
- Monitor selected process parameters
- Compare parameters against configured monitoring limits
- Identify normal and abnormal conditions
- Identify records that have not yet been processed
- Generate structured monitoring reports
- Provide an interactive Streamlit dashboard
- Allow monitoring reports to be downloaded as CSV files

---

## OSAT and ATMP

### OSAT

OSAT stands for:

**Outsourced Semiconductor Assembly and Test**

OSAT operations generally cover semiconductor assembly, packaging, inspection, and testing activities performed after semiconductor fabrication.

### ATMP

ATMP stands for:

**Assembly, Testing, Marking and Packaging**

This project uses OSAT/ATMP as the manufacturing-operation categories represented within the monitoring system.

---

## Manufacturing Process Flow

```text
Wafer Inspection
       ↓
Wafer Sort
       ↓
Back Grinding
       ↓
Wafer Dicing
       ↓
Die Attach
       ↓
Wire Bonding
       ↓
Encapsulation / Molding
       ↓
Marking
       ↓
Singulation
       ↓
Package Inspection
       ↓
Burn-in
       ↓
ICT
       ↓
FCT
       ↓
EOL
       ↓
Final Inspection
       ↓
Packing / Dispatch
```

---

## System Architecture

```text
                 Manufacturing Process Data
                           │
                           ▼
              ┌─────────────────────────┐
              │ Data Generation Module  │
              │                         │
              │ generate_process_data   │
              │ .py                     │
              └────────────┬────────────┘
                           │
                           ▼
                 Manufacturing Dataset
                           │
                           ▼
              ┌─────────────────────────┐
              │ Monitoring Engine       │
              │                         │
              │ monitoring_engine.py    │
              │                         │
              │ Process status          │
              │ Parameter monitoring    │
              │ Configured limits       │
              └────────────┬────────────┘
                           │
                           ▼
                Monitoring Results CSV
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
   ┌─────────────────────┐    ┌─────────────────────┐
   │ Report Generation   │    │ Streamlit Dashboard │
   │                     │    │                     │
   │ Monitoring reports  │    │ Interactive view    │
   └──────────┬──────────┘    └──────────┬──────────┘
              │                          │
              ▼                          ▼
       CSV Reports              Manufacturing Monitoring
```

---

## Monitoring Methodology

The system uses configured process limits to monitor available process parameters.

```text
Manufacturing Record
        │
        ▼
Identify Process Stage
        │
        ▼
Check Available Parameter
        │
        ▼
Compare Against Configured Limit
        │
        ├───────────────┐
        ▼               ▼
 Within Limit       Outside Limit
        │               │
        ▼               ▼
     NORMAL          ABNORMAL
```

For records that have not yet reached a particular processing stage:

```text
NOT_PROCESSED
```

The system therefore uses three primary monitoring states:

- `NORMAL`
- `ABNORMAL`
- `NOT_PROCESSED`

---

## Process Parameters

The project dataset contains parameters associated with different manufacturing stages.

Examples include:

### Wafer-Level Parameters

- Wafer thickness
- TTV
- Bow
- Warp
- Thickness variation

### Assembly Parameters

- Attach force
- Attach offset
- Wire-bond force
- Bond pull strength

### Molding Parameters

- Mold temperature
- Mold cure time
- Void percentage

### Inspection / Packaging Parameters

- Marking quality score
- Singulation damage score
- Package dimension

### Testing Parameters

- Burn-in temperature
- Burn-in hours
- ICT current
- FCT voltage
- EOL temperature

---

## Dashboard Features

The Streamlit dashboard provides monitoring views for:

- Production monitoring
- Monitoring status
- OSAT/ATMP classification
- Process-flow monitoring
- Process-stage monitoring
- Process status by stage
- Wafer metrology monitoring
- Process-parameter monitoring
- Equipment monitoring
- Shift monitoring
- Abnormal conditions
- Recent processed records
- Monitoring reports

### Interactive Filters

Users can filter monitoring information using parameters such as:

- Operation Type
- Process Stage
- Shift
- Equipment
- Monitoring Status

---

## Monitoring Reports

The system generates the following reports:

| Report | Description |
|---|---|
| Overall Monitoring Summary | Overall monitoring statistics |
| Stage Monitoring | Monitoring information by process stage |
| Parameter Monitoring | Process-parameter monitoring |
| Equipment Monitoring | Equipment-level monitoring |
| Shift Monitoring | Shift-level monitoring |
| Operation Monitoring | OSAT/ATMP operation monitoring |
| Abnormal Conditions | Records classified as abnormal |
| Unit Monitoring | Unit-level monitoring |
| Lot Monitoring | Lot-level monitoring |

All reports are generated in CSV format.

---

## Current Project Scale

| Item | Value |
|---|---:|
| Monitoring Records | 96,000 |
| Units | 6,000 |
| Lots | 40 |
| Wafers | 6,000 |
| Process Stages | 16 |
| Configured Monitoring Limits | 27 |
| Monitoring Reports | 9 |

> The dataset used by this project is generated for demonstration purposes and does not represent confidential semiconductor manufacturing data.

---

## Technology Stack

### Programming

- Python 3.8+

### Data Processing

- Pandas

### Dashboard

- Streamlit

### Data Storage

- CSV

### Configuration

- CSV-based process classification and monitoring limits

---

## Project Structure

```text
OSAT-ATMP-Manufacturing-Process-Monitoring/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── config/
│   ├── process_classification.csv
│   └── process_limits.csv
│
├── data/
│   └── osat_atmp_process_data.csv
│
├── src/
│   ├── generate_process_data.py
│   ├── monitoring_engine.py
│   ├── generate_monitoring_report.py
│   └── dashboard.py
│
├── outputs/
│   └── monitoring_reports/
│       ├── process_monitoring_results.csv
│       ├── overall_monitoring_summary.csv
│       ├── stage_monitoring_report.csv
│       ├── parameter_monitoring_report.csv
│       ├── equipment_monitoring_report.csv
│       ├── shift_monitoring_report.csv
│       ├── operation_monitoring_report.csv
│       ├── abnormal_conditions_report.csv
│       ├── unit_monitoring_report.csv
│       └── lot_monitoring_report.csv
│
└── screenshots/
    ├── dashboard_overview.png
    ├── process_flow.png
    ├── parameter_monitoring.png
    └── reports.png
```

---

# Installation

## 1. Clone the repository

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
```

Move into the project directory:

```bash
cd OSAT-ATMP-Manufacturing-Process-Monitoring
```

---

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Generate the manufacturing dataset

```bash
python src/generate_process_data.py
```

---

## 4. Run the monitoring engine

```bash
python src/monitoring_engine.py
```

This generates the monitoring results:

```text
outputs/monitoring_reports/process_monitoring_results.csv
```

---

## 5. Generate monitoring reports

```bash
python src/generate_monitoring_report.py
```

This generates the monitoring report CSV files.

---

## 6. Start the Streamlit dashboard

```bash
python -m streamlit run src/dashboard.py
```

The dashboard will normally be available at:

```text
http://localhost:8501
```

---

# Example Monitoring Logic

A simplified example of the monitoring concept:

```text
Process Parameter
       │
       ▼
Configured Lower Limit
       │
       ▼
Actual Process Value
       │
       ▼
Configured Upper Limit
       │
       ├── Within Limits ──► NORMAL
       │
       └── Outside Limits ─► ABNORMAL
```

---

# Key Skills Demonstrated

This project demonstrates practical skills in:

- Python
- Pandas
- Data processing
- CSV data handling
- Manufacturing process monitoring
- Semiconductor manufacturing concepts
- OSAT/ATMP process understanding
- Process parameter monitoring
- Equipment monitoring
- Production data organization
- Rule-based monitoring
- Streamlit dashboard development
- Report generation
- Data visualization
- Technical documentation

---

# Project Scope

This project is intentionally focused on **manufacturing process monitoring**.

The current implementation does not include:

- Machine learning
- Failure prediction
- Yield prediction
- Risk scoring
- Root-cause analysis
- Predictive maintenance
- Automated equipment control

These can be considered separate future development areas rather than current project functionality.

---

# Future Enhancements

Potential future enhancements include:

- Integration with real manufacturing databases
- Integration with factory equipment data sources
- Real-time data ingestion
- MES integration
- Automated dashboard refresh
- User authentication
- Role-based dashboard access
- Historical trend visualization
- Additional process parameters
- Integration with industrial communication systems

---

# Project Purpose

This project was developed as a **personal semiconductor manufacturing portfolio project** to demonstrate practical understanding of OSAT/ATMP operations, manufacturing data handling, process monitoring, and dashboard development.

---

## Author

**Bedabrat Bharali**

B.Tech — Electronics & Instrumentation

Interested in:

- Semiconductor Manufacturing
- OSAT / ATMP
- Process Engineering
- Equipment Engineering
- Instrumentation
- Automation
- Electronics
- Manufacturing Data Systems
