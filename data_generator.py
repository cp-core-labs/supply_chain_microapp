from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List


def generate_supplier_master() -> pd.DataFrame:
    """
    Genera una tabla maestra de proveedores con perfiles realistas
    para lead time, costo y servicio.
    """
    suppliers = [
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
        {
            "supplier_code": "SUP-003",
            "supplier_name": "Sunrise Industrial Co.",
            "region": "Asia Pacific",
            "avg_lead_time_days": 14,
            "lead_time_std_days": 4.0,
            "service_level_target": 0.92,
            "on_time_delivery_rate": 0.90,
            "shipping_cost_per_unit": 0.65,
            "risk_factor": 0.42,
            "criticality": "Essential",
        },
        {
            "supplier_code": "SUP-004",
            "supplier_name": "Mercury Parts Group",
            "region": "North America",
            "avg_lead_time_days": 9,
            "lead_time_std_days": 2.8,
            "service_level_target": 0.95,
            "on_time_delivery_rate": 0.94,
            "shipping_cost_per_unit": 0.68,
            "risk_factor": 0.25,
            "criticality": "Vital",
        },
        {
            "supplier_code": "SUP-005",
            "supplier_name": "GreenLine Procurement",
            "region": "LATAM",
            "avg_lead_time_days": 17,
            "lead_time_std_days": 5.5,
            "service_level_target": 0.90,
            "on_time_delivery_rate": 0.88,
            "shipping_cost_per_unit": 0.78,
            "risk_factor": 0.55,
            "criticality": "Desirable",
        },
        {
            "supplier_code": "SUP-006",
            "supplier_name": "Atlas Distribution",
            "region": "Europe",
            "avg_lead_time_days": 6,
            "lead_time_std_days": 1.8,
            "service_level_target": 0.97,
            "on_time_delivery_rate": 0.98,
            "shipping_cost_per_unit": 0.9,
            "risk_factor": 0.18,
            "criticality": "Vital",
        },
    ]

    return pd.DataFrame(suppliers)


def generate_synthetic_supply_chain_data(
    output_dir: str | Path = "data",
    n_skus: int = 40,
    n_days: int = 730,
    seed: int = 42,
) -> Dict[str, pd.DataFrame]:
    """
    Genera datos sintéticos realistas para una microaplicación de supply chain:
    - ventas históricas por SKU por día
    - proveedores y lead times
    - atributos por producto y proveedor
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(seed)

    # -----------------------------
    # 1) Proveedores y catalogación
    # -----------------------------
    supplier_df = generate_supplier_master()

    # Generar una mezcla de categorías de productos
    categories = ["A", "B", "C"]
    category_weights = [0.45, 0.35, 0.20]

    # Cada SKU tendrá un proveedor principal
    supplier_codes = supplier_df["supplier_code"].tolist()
    product_names = [
        "Widget",
        "Panel",
        "Sensor",
        "Motor",
        "Valve",
        "Controller",
        "Cable",
        "Pump",
        "Filter",
        "Battery",
        "Circuit",
        "Gear",
        "Switch",
        "Bracket",
        "Actuator",
        "Seal",
        "Charger",
        "Nozzle",
        "Connector",
        "Relay",
        "Adapter",
        "Latch",
        "Scanner",
        "Display",
        "Transmitter",
        "Diode",
        "Thermostat",
        "Compressor",
        "Regulator",
        "Harness",
        "Housing",
        "Encoder",
        "Lubricant",
        "Bushing",
        "Coupling",
        "Drum",
        "Mount",
        "Fuse",
        "Sprayer",
        "Vent",
    ]

    # -----------------------------
    # 2) Prepara fechas base
    # -----------------------------
    start_date = pd.Timestamp("2023-01-01")
    dates = pd.date_range(start=start_date, periods=n_days, freq="D")

    sales_rows: List[dict] = []

    # Definir estacionalidad semanal y mensual
    weekly_pattern = {
        0: 1.02,  # Monday
        1: 1.08,  # Tuesday
        2: 1.15,  # Wednesday
        3: 1.12,  # Thursday
        4: 1.20,  # Friday
        5: 0.88,  # Saturday
        6: 0.76,  # Sunday
    }

    monthly_pattern = {
        1: 0.82,
        2: 0.89,
        3: 0.95,
        4: 1.02,
        5: 1.08,
        6: 1.15,
        7: 1.20,
        8: 1.12,
        9: 1.06,
        10: 1.18,
        11: 1.28,
        12: 1.35,
    }

    # Definir promociones por mes / fechas puntuales
    promo_windows = [
        ("2023-02-15", "2023-02-25"),
        ("2023-05-10", "2023-05-18"),
        ("2023-07-20", "2023-07-30"),
        ("2023-10-15", "2023-10-25"),
        ("2024-01-05", "2024-01-20"),
    ]

    promo_intervals = []
    for start_str, end_str in promo_windows:
        start = pd.Timestamp(start_str)
        end = pd.Timestamp(end_str)
        promo_intervals.append((start, end))

    # -----------------------------
    # 3) Generación por SKU
    # -----------------------------
    for sku_idx in range(n_skus):
        category = rng.choice(categories, p=category_weights)
        supplier_code = rng.choice(supplier_codes)
        supplier_meta = supplier_df[supplier_df["supplier_code"] == supplier_code].iloc[0]

        product_base = product_names[sku_idx % len(product_names)]
        sku_code = f"SKU-{sku_idx + 1:03d}"

        # Parámetros realistas por SKU
        base_demand = float(rng.uniform(20, 260))
        trend_rate = float(rng.uniform(-0.02, 0.05))  # crecimiento o decrecimiento
        annual_seasonality = float(rng.uniform(0.7, 1.5))
        noise_sigma = float(rng.uniform(0.05, 0.22))
        unit_price = float(rng.uniform(7.5, 90.0))
        unit_cost = max(2.0, unit_price * rng.uniform(0.38, 0.82))
        reorder_point = int(rng.uniform(25, 220))
        target_service_level = float(rng.uniform(0.88, 0.99))

        # Variación por SKU
        for date in dates:
            day_index = (date - start_date).days

            # Trend general
            trend_factor = 1 + (trend_rate * day_index / max(1, n_days))

            # Estacionalidad mensual
            monthly_factor = monthly_pattern.get(date.month, 1.0) * annual_seasonality

            # Estacionalidad semanal
            weekday_factor = weekly_pattern.get(date.dayofweek, 1.0)

            # Promociones
            promo_factor = 1.0
            for promo_start, promo_end in promo_intervals:
                if promo_start <= date <= promo_end:
                    promo_factor = float(rng.uniform(1.35, 2.10))
                    break

            # Ruido aleatorio
            noise = rng.normal(0, noise_sigma)
            demand = base_demand * trend_factor * monthly_factor * weekday_factor * promo_factor * (1 + noise)

            # Evita demanda negativa
            demand = max(0.0, demand)

            # A veces se producen picos o caídas por eventos extraordinarios
            if rng.random() < 0.08:
                demand *= rng.uniform(1.2, 2.2)

            units_sold = max(0, int(round(demand)))

            if units_sold == 0 and rng.random() < 0.2:
                units_sold = 1

            revenue = round(units_sold * unit_price, 2)
            gross_margin = round((unit_price - unit_cost) * units_sold, 2)

            sales_rows.append(
                {
                    "date": date,
                    "sku": sku_code,
                    "product_name": product_base,
                    "category": category,
                    "supplier_code": supplier_code,
                    "supplier_name": supplier_meta["supplier_name"],
                    "region": supplier_meta["region"],
                    "units_sold": units_sold,
                    "unit_price": round(unit_price, 2),
                    "unit_cost": round(unit_cost, 2),
                    "revenue": revenue,
                    "gross_margin": gross_margin,
                    "avg_daily_demand": round(base_demand, 2),
                    "reorder_point": reorder_point,
                    "service_level_target": round(target_service_level, 3),
                }
            )

    # -----------------------------
    # 4) Construcción del DataFrame
    # -----------------------------
    sales_df = pd.DataFrame(sales_rows)
    sales_df = sales_df[
        [
            "date",
            "sku",
            "product_name",
            "category",
            "supplier_code",
            "supplier_name",
            "region",
            "units_sold",
            "unit_price",
            "unit_cost",
            "revenue",
            "gross_margin",
            "avg_daily_demand",
            "reorder_point",
            "service_level_target",
        ]
    ].copy()

    # Asegurar orden temporal
    sales_df = sales_df.sort_values(["sku", "date"]).reset_index(drop=True)

    # -----------------------------
    # 5) Guardar archivos
    # -----------------------------
    sales_path = output_dir / "historical_sales.csv"
    supplier_path = output_dir / "suppliers_lead_time.csv"

    sales_df.to_csv(sales_path, index=False)
    supplier_df.to_csv(supplier_path, index=False)

    return {
        "sales": sales_df,
        "suppliers": supplier_df,
    }


if __name__ == "__main__":
    # Ejemplo de ejecución standalone
    output = generate_synthetic_supply_chain_data(
        output_dir="data",
        n_skus=40,
        n_days=730,
        seed=42,
    )

    print("Archivos generados:")
    print("- data/historical_sales.csv")
    print("- data/suppliers_lead_time.csv")
    print("")
    print("Ventas generadas:", len(output["sales"]))
    print("SKUs:", output["sales"]["sku"].nunique())
    print("Proveedores:", output["suppliers"]["supplier_code"].nunique())