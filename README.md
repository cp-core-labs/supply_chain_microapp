# Supply Chain & Inventory Optimization Platform

Una micro-aplicación analítica en Python para logística, forecasting de demanda y optimización de inventarios.

## Objetivo

La app está orientada a:
- analizar ventas históricas
- pronosticar demanda por SKU
- calcular niveles críticos de inventario
- priorizar compras
- evaluar riesgo de ruptura de stock
- simular escenarios operativos

No está diseñada como SaaS completo ni incluye autenticación, pagos o pasarelas, porque su foco es análisis y apoyo a decisiones de negocio.

## Estructura del proyecto

```text
supply_chain_microapp/
├── data/
│   ├── historical_sales.csv
│   ├── suppliers_lead_time.csv
│   └── raw/
│
├── modules/
│   ├── __init__.py
│   ├── data_processor.py
│   ├── forecaster.py
│   ├── inventory_optimizer.py
│   ├── risk_engine.py
│   ├── report_exporter.py
│   └── utils.py
│
├── assets/
│   └── style.css
│
├── tests/
│   ├── test_data_processor.py
│   ├── test_inventory_optimizer.py
│   ├── test_forecaster.py
│   └── test_risk_engine.py
│
├── app.py
├── data_generator.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
├── pytest.ini
├── README.md
└── .env