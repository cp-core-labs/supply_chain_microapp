import pandas as pd

from modules.data_processor import (
    clean_sales_dataframe,
    process_supply_chain_data,
)


def build_sample_sales_df():
    return pd.DataFrame(
        [
            {
                "date": "2024-01-01",
                "sku": "SKU-001",
                "product_name": "Widget A",
                "category": "A",
                "supplier_code": "SUP-001",
                "supplier_name": "NorthPort Logistics",
                "region": "North America",
                "units_sold": 120,
                "unit_price": 25.0,
                "unit_cost": 14.0,
                "revenue": 3000.0,
                "gross_margin": 1320.0,
                "avg_daily_demand": 120.0,
                "reorder_point": 500,
                "service_level_target": 0.95,
            },
            {
                "date": "2024-01-01",
                "sku": "SKU-001",
                "product_name": "Widget A",
                "category": "A",
                "supplier_code": "SUP-001",
                "supplier_name": "NorthPort Logistics",
                "region": "North America",
                "units_sold": 120,
                "unit_price": 25.0,
                "unit_cost": 14.0,
                "revenue": 3000.0,
                "gross_margin": 1320.0,
                "avg_daily_demand": 120.0,
                "reorder_point": 500,
                "service_level_target": 0.95,
            },
            {
                "date": "2024-01-02",
                "sku": "SKU-002",
                "product_name": "Widget B",
                "category": "B",
                "supplier_code": "SUP-002",
                "supplier_name": "Blue Harbor Supply",
                "region": "Europe",
                "units_sold": -10,  # inválido, debe corregirse
                "unit_price": 18.0,
                "unit_cost": 10.0,
                "revenue": 0.0,
                "gross_margin": 0.0,
                "avg_daily_demand": 40.0,
                "reorder_point": 150,
                "service_level_target": 0.92,
            },
            {
                "date": "bad-date",
                "sku": "SKU-003",
                "product_name": "Widget C",
                "category": "C",
                "supplier_code": "SUP-003",
                "supplier_name": "Sunrise Industrial Co.",
                "region": "Asia Pacific",
                "units_sold": 5,
                "unit_price": 12.0,
                "unit_cost": 7.0,
                "revenue": 60.0,
                "gross_margin": 25.0,
                "avg_daily_demand": 10.0,
                "reorder_point": 80,
                "service_level_target": 0.90,
            },
        ]
    )


def build_sample_supplier_df():
    return pd.DataFrame(
        [
            {
                "supplier_code": "SUP-001",
                "supplier_name": "NorthPort Logistics",
                "region": "North America",
                "avg_lead_time_days": 7,
                "lead_time_std_days": 2.2,
                "service_level_target": 0.96,
                "on_time_delivery_rate": 0.97,
                "shipping_cost_per_unit": 0.85,
                "risk_factor": 0.2,
                "criticality": "Vital",
            },
            {
                "supplier_code": "SUP-002",
                "supplier_name": "Blue Harbor Supply",
                "region": "Europe",
                "avg_lead_time_days": 11,
                "lead_time_std_days": 3.1,
                "service_level_target": 0.94,
                "on_time_delivery_rate": 0.93,
                "shipping_cost_per_unit": 0.72,
                "risk_factor": 0.35,
                "criticality": "Essential",
            },
        ]
    )


def test_clean_sales_dataframe_removes_invalid_rows_and_normalizes():
    df = build_sample_sales_df()

    cleaned = clean_sales_dataframe(df)

    assert isinstance(cleaned, pd.DataFrame)
    assert not cleaned.empty
    assert "date" in cleaned.columns
    assert "sku" in cleaned.columns
    assert cleaned["units_sold"].min() >= 0
    assert cleaned["date"].notna().all()
    assert cleaned["sku"].nunique() >= 2
    assert cleaned["reorder_point"].notna().all()


def test_process_supply_chain_data_generates_expected_outputs(tmp_path):
    sales_path = tmp_path / "historical_sales.csv"
    supplier_path = tmp_path / "suppliers.csv"

    build_sample_sales_df().to_csv(sales_path, index=False)
    build_sample_supplier_df().to_csv(supplier_path, index=False)

    result = process_supply_chain_data(sales_path, supplier_path)

    assert set(result.keys()) == {
        "sales_clean",
        "suppliers_clean",
        "merged",
        "daily_sales",
        "sku_summary",
    }

    assert not result["sales_clean"].empty
    assert not result["suppliers_clean"].empty
    assert not result["merged"].empty
    assert not result["daily_sales"].empty
    assert not result["sku_summary"].empty

    assert "date" in result["sales_clean"].columns
    assert "sku" in result["daily_sales"].columns
    assert "sku" in result["sku_summary"].columns
