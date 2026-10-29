# Supply Chain & Inventory Optimization Platform

Production-ready Supply Chain & Inventory Optimization Platform featuring demand forecasting, ABC/VED analysis, Safety Stock, EOQ, and risk scenario evaluation.

## Overview

This application is designed to support supply chain decision-making through:
- Historical sales analysis
- Demand forecasting by SKU
- Inventory optimization
- ABC/VED classification
- Safety stock and reorder point planning
- Operational risk evaluation
- Scenario simulation

*Note: This is a decision-support analytic dashboard focused on inventory and operational intelligence.*

## Main Features

- **Demand Forecasting by SKU:** Predict future requirements accurately.
- **ABC/VED Segmentation:** Prioritize inventory based on financial value and operational criticality.
- **Safety Stock & EOQ Calculations:** Optimize reorder points and order quantities to balance carrying costs.
- **Operational Risk Alerts:** Proactively identify potential stockouts and supply disruptions.
- **What-if Scenario Analysis:** Simulate operational risk scenarios and supply variations.
- **CSV Export:** Download planning insights for external decision-making workflows.

## Tech Stack

- **Core Engine & Data Processing:** Python, Pandas, NumPy
- **Machine Learning & Forecasting:** Scikit-learn, Statsmodels, Prophet, XGBoost
- **Dashboard & Visualization:** Streamlit, Plotly
- **Testing & Quality Assurance:** Pytest, Ruff, Black, Mypy

## Project Structure

```text
supply_chain_microapp/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── workflows/
├── .gitignore
├── .env.example
├── .pre-commit-config.yaml
├── Dockerfile
├── LICENSE
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── app.py
├── data/
│   ├── historical_sales.csv
│   ├── suppliers_lead_time.csv
│   └── README.md
├── docs/
│   ├── architecture.md
│   ├── deployment.md
│   └── data_dictionary.md
├── modules/
│   ├── __init__.py
│   ├── data_processor.py
│   ├── forecaster.py
│   ├── inventory_optimizer.py
│   ├── risk_engine.py
│   ├── report_exporter.py
│   └── utils.py
├── scripts/
│   ├── run_local.sh
│   └── build_docker.sh
├── tests/
│   ├── test_data_processor.py
│   ├── test_forecaster.py
│   ├── test_inventory_optimizer.py
│   └── test_risk_engine.py
└── src/
    └── supply_chain_microapp/
        ├── __init__.py
        └── config.py