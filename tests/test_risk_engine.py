import pandas as pd

from modules.risk_engine import build_alerts, evaluate_what_if_scenario, build_risk_summary


def build_inventory_sample():
    return pd.DataFrame(
        [
            {
                "sku": "SKU-001",
                "product_name": "Widget A",
                "category": "A",
                "avg_daily_demand": 120,
                "demand_std": 24,
                "avg_lead_time_days": 9,
                "lead_time_std_days": 2,
                "stockout_probability": 0.35,
                "risk_score": 65,
                "days_of_coverage": 1.5,
            },
            {
                "sku": "SKU-002",
                "product_name": "Widget B",
                "category": "B",
                "avg_daily_demand": 60,
                "demand_std": 12,
                "avg_lead_time_days": 6,
                "lead_time_std_days": 1.5,
                "stockout_probability": 0.12,
                "risk_score": 28,
                "days_of_coverage": 4.2,
            },
        ]
    )


def test_build_alerts_assigns_levels():
    sample = build_inventory_sample()
    alerts = build_alerts(sample)

    assert "alert_level" in alerts.columns
    assert "priority_score" in alerts.columns
    assert set(alerts["alert_level"].unique()) <= {"Verde", "Amarillo", "Rojo"}


def test_evaluate_what_if_scenario_creates_scenario_output():
    sample = build_inventory_sample()
    scenario = evaluate_what_if_scenario(
        sample,
        demand_change_pct=0.2,
        lead_time_change_days=3,
        service_level=0.95,
    )

    assert "scenario_risk_score" in scenario.columns
    assert "scenario_alert_level" in scenario.columns
    assert "scenario_reorder_point" in scenario.columns


def test_build_risk_summary_is_valid():
    alerts = build_alerts(build_inventory_sample())
    summary = build_risk_summary(alerts)

    assert not summary.empty
    assert "alert_level" in summary.columns
    assert "sku_count" in summary.columns