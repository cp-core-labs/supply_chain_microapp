<div align="left">

  <table>
    <tr>
      <td>
        <img src="https://img.shields.io/badge/Release-v1.0.0-orange?style=for-the-badge&logo=github&logoColor=white" alt="Release v1.0.0" />
      </td>
      <td>
        <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License MIT" />
      </td>
    </tr>
  </table>

</div>

<h1 align="left">
  <img src="https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/1f680.svg" width="32" alt="rocket" />
  Supply Chain & Inventory Intelligence Platform
</h1>

<p align="left">
  <strong>
    AI-powered inventory intelligence and predictive demand forecasting built for modern logistics and operational planning.
  </strong>
</p>

<p>
  Centralize sales, supplier, and inventory data, forecast demand by SKU, optimize reorder policies, and receive proactive risk alerts across your supply network.
</p>

<div align="left">
  <img src="https://img.shields.io/badge/Live%20Demo-Streamlit%20Cloud-red?style=for-the-badge" alt="Live Demo" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/ML%20Engine-Scikit%20Learn-purple?style=for-the-badge" alt="ML Engine" />
  <img src="https://img.shields.io/badge/Forecasting-Prophet-9cf?style=for-the-badge" alt="Prophet" />
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="MIT License" />
</div>

---

## Overview

This project helps teams:
- analyze historical sales and demand patterns
- forecast demand by SKU
- calculate safety stock, EOQ, and reorder points
- classify products with ABC/VED logic
- detect stockout risk and operational alerts
- simulate demand and lead time scenarios

## Key Features

- Demand forecasting with trend and seasonality analysis
- Inventory optimization using operational constraints
- Risk scoring and alerting for critical SKUs
- Streamlit dashboard for business decision support
- Exportable results for operational planning

## Tech Stack

- Python 3.10+
- Streamlit
- Pandas
- NumPy
- Scikit-learn
- Prophet
- Plotly
- XGBoost

## Getting Started

```bash
git clone https://github.com/crissnyx/supply_chain_microapp.git
cd supply_chain_microapp
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
streamlit run app.py
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