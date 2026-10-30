<div align="left">
  <table>
    <tr>
      <td>
        <a href="https://github.com/crissnyx/supply_chain_microapp/releases">
          <img src="https://img.shields.io/badge/Release-v1.0.0-orange?style=for-the-badge&logo=github&logoColor=white" alt="Release v1.0.0" />
        </a>
      </td>
      <td>
        <a href="https://github.com/crissnyx/supply_chain_microapp/blob/main/LICENSE">
          <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License MIT" />
        </a>
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
    AI-powered inventory intelligence, predictive demand forecasting, and operational planning built for modern logistics.
  </strong>
</p>

<p>
  Production-ready Supply Chain & Inventory Optimization Platform featuring demand forecasting, ABC/VED analysis, Safety Stock, EOQ, and risk scenario evaluation. Centralize sales, supplier, and inventory data to make data-driven logistics decisions.
</p>

<div align="left">
  <a href="https://your-streamlit-cloud-url.streamlit.app/">
    <img src="https://img.shields.io/badge/LIVE_DEMO-Streamlit%20Cloud-red?style=for-the-badge" alt="Live Demo" />
  </a>

  <a href="https://streamlit.io/">
    <img src="https://img.shields.io/badge/Streamlit-Cloud-orange?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  </a>

  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+" />
  </a>

  <a href="https://scikit-learn.org/stable/">
    <img src="https://img.shields.io/badge/ML_Engine-Scikit%20Learn-purple?style=for-the-badge" alt="Scikit Learn" />
  </a>

  <a href="https://facebook.github.io/prophet/">
    <img src="https://img.shields.io/badge/Forecasting-Prophet-9cf?style=for-the-badge" alt="Prophet" />
  </a>

  <a href="https://github.com/crissnyx/supply_chain_microapp/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="MIT License" />
  </a>
</div>

---

## Overview

This application is designed to support supply chain decision-making through:
- Historical sales and demand pattern analysis
- Demand forecasting by SKU
- Inventory optimization and reorder policies
- ABC/VED classification logic
- Safety stock and economic order quantity (EOQ) planning
- Operational risk evaluation and proactive alerting
- Scenario and lead time simulation

*Note: This is a decision-support analytic dashboard focused on inventory and operational intelligence.*

## Main Features

- **Demand Forecasting by SKU:** Predict future requirements accurately using machine learning.
- **ABC/VED Segmentation:** Prioritize inventory based on financial value and operational criticality.
- **Safety Stock & EOQ Calculations:** Optimize reorder points and order quantities to balance holding and stockout costs.
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
│   ️├── deployment.md
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