import pandas as pd

from modules.inventory_optimizer import (
    assign_abc_classification,
    assign_ved_classification,
    build_inventory_plan,
    calculate_eoq,
    calculate_reorder_point,
    calculate_safety_stock,
    simulate_lead_time_uncertainty,
)


def test_calculate_safety_stock_and_reorder_point():
    safety_stock = calculate_safety_stock(
        avg_daily_demand=12,
        demand_std=3,
        lead_time_days=5,
        lead_time_std_days=1.5,
        service_level=0.95,
    )

    reorder_point = calculate_reorder_point(
        avg_daily_demand=12,
        lead_time_days=5,
        safety_stock=safety_stock,
    )

    assert safety_stock >= 0
    assert reorder_point >= 12 * 5
    assert reorder_point >= safety_stock


def test_calculate_eoq():
    eoq = calculate_eoq(
        annual_demand=5000,
        ordering_cost=120,
        holding_cost_per_unit_year=8,
    )

    assert eoq > 0
    assert eoq == eoq  # simple sanity check


def test_assign_abc_and_ved_classification():
    df = pd.DataFrame(
        [
            {"sku": "SKU-001", "annual_dollar_usage": 1000, "criticality": "Vital"},
            {"sku": "SKU-002", "annual_dollar_usage": 600, "criticality": "Essential"},
            {"sku": "SKU-003", "annual_dollar_usage": 100, "criticality": "Desirable"},
        ]
    )

    abc_df = assign_abc_classification(df, value_col="annual_dollar_usage", sku_col="sku")
    ved_df = assign_ved_classification(df, criticality_col="criticality", sku_col="sku")

    assert set(abc_df["abc_class"].unique()) <= {"A", "B", "C"}
    assert set(ved_df["ved_class"].unique()) <= {"V", "E", "D"}


def test_simulate_lead_time_uncertainty_returns_valid_metrics():
    sim = simulate_lead_time_uncertainty(
        avg_daily_demand=18,
        demand_std=4,
        lead_time_mean=7,
        lead_time_std=2,
        reorder_point=180,
        n_simulations=1500,
        seed=42,
    )

    assert "stockout_probability" in sim
    assert "mean_lead_time" in sim
    assert "mean_demand_during_lt" in sim
    assert 0 <= sim["stockout_probability"] <= 1
    assert sim["mean_lead_time"] > 0


def test_build_inventory_plan_creates_operational_columns():
    processed_data = {
        "sku_summary": pd.DataFrame(
            [
                {
                    "sku": "SKU-001",
                    "product_name": "Widget A",
                    "category": "A",
                    "avg_daily_demand": 15,
                    "demand_std": 3,
                    "avg_lead_time_days": 7,
                    "lead_time_std_days": 1.6,
                    "avg_unit_price": 25,
                    "service_level_target": 0.95,
                    "criticality": "Vital",
                    "reorder_point": 120,
                    "annual_revenue_estimate": 1200,
                },
                {
                    "sku": "SKU-002",
                    "product_name": "Widget B",
                    "category": "B",
                    "avg_daily_demand": 8,
                    "demand_std": 2,
                    "avg_lead_time_days": 10,
                    "lead_time_std_days": 2.5,
                    "avg_unit_price": 18,
                    "service_level_target": 0.92,
                    "criticality": "Essential",
                    "reorder_point": 90,
                    "annual_revenue_estimate": 650,
                },
            ]
        )
    }

    plan = build_inventory_plan(processed_data, service_level=0.95)

    required_cols = {
        "sku",
        "abc_class",
        "ved_class",
        "safety_stock",
        "reorder_point",
        "eoq",
        "stockout_probability",
        "risk_score",
    }

    assert required_cols.issubset(set(plan.columns))
    assert not plan.empty
    assert plan["safety_stock"].ge(0).all()
    assert plan["reorder_point"].ge(0).all()
    assert plan["risk_score"].notna().all()
