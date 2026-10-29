from __future__ import annotations

import pandas as pd
from pathlib import Path
from typing import Dict, Optional, Tuple


def _safe_pick_column(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    """
    Devuelve el nombre real de una columna si existe en el DataFrame.
    Busca entre varias opciones sin romper si alguna no existe.
    """
    normalized = {str(col).strip().lower(): col for col in df.columns}
    for name in candidates:
        if str(name).strip().lower() in normalized:
            return normalized[str(name).strip().lower()]
    return None


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza columnas a minúsculas y sin espacios para evitar colisiones.
    """
    out = df.copy()
    out.columns = [str(col).strip().lower() for col in out.columns]
    return out


def clean_supplier_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpieza tolerante: no rompe si faltan columnas opcionales.
    """
    out = _normalize_columns(df)

    # Campos esenciales mínimos
    required_cols = {"supplier_code"}
    missing_required = required_cols - set(out.columns)
    if missing_required:
        raise ValueError(f"Faltan columnas esenciales en proveedores: {missing_required}")

    # Campos opcionales: solo si existen, los convertimos
    numeric_like = [
        "avg_lead_time_days",
        "lead_time_std_days",
        "service_level_target",
        "on_time_delivery_rate",
        "shipping_cost_per_unit",
        "risk_factor",
    ]

    for col in numeric_like:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    # Normalizar strings solo si existen
    for col in ["supplier_name", "region", "criticality"]:
        if col in out.columns:
            out[col] = out[col].astype(str).str.strip()

    out = out.dropna(subset=["supplier_code"]).copy()
    out = out.drop_duplicates(subset=["supplier_code"]).reset_index(drop=True)
    return out


def clean_sales_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpieza tolerante para ventas.
    """
    out = _normalize_columns(df)

    if "date" in out.columns:
        out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out = out.dropna(subset=["date"]).copy()

    # Si no existe alguna columna de negocio crítica, crearla con default
    if "supplier_code" not in out.columns:
        out["supplier_code"] = "UNKNOWN"

    for col in ["sku", "product_name", "category", "supplier_code", "supplier_name", "region"]:
        if col in out.columns:
            out[col] = out[col].astype(str).str.strip()

    numeric_cols = [
        "units_sold",
        "unit_price",
        "unit_cost",
        "revenue",
        "gross_margin",
        "avg_daily_demand",
        "reorder_point",
        "service_level_target",
    ]

    for col in numeric_cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    # Reglas defensivas
    if "units_sold" in out.columns:
        out["units_sold"] = out["units_sold"].clip(lower=0)

    if "revenue" in out.columns:
        out["revenue"] = out["revenue"].fillna(0.0)

    if "gross_margin" in out.columns:
        out["gross_margin"] = out["gross_margin"].fillna(0.0)

    out = out.drop_duplicates().sort_values(["sku", "date"]).reset_index(drop=True)
    return out


def merge_supplier_context(
    sales_df: pd.DataFrame,
    supplier_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge tolerante a columnas faltantes o con sufijos.
    No asume que supplier_name/region existen en todos los CSVs.
    """
    sales = clean_sales_dataframe(sales_df)
    suppliers = clean_supplier_dataframe(supplier_df)

    # Renombrado seguro: solo para columnas existentes
    rename_map = {}
    alias_map = {
        "supplier_name": "supplier_name_supplier",
        "region": "region_supplier",
        "avg_lead_time_days": "avg_lead_time_days",
        "lead_time_std_days": "lead_time_std_days",
        "service_level_target": "service_level_target",
        "on_time_delivery_rate": "on_time_delivery_rate",
        "shipping_cost_per_unit": "shipping_cost_per_unit",
        "risk_factor": "risk_factor",
        "criticality": "criticality",
    }

    for src, dst in alias_map.items():
        if src in suppliers.columns:
            rename_map[src] = dst

    supplier_subset = suppliers.rename(columns=rename_map)

    merged = sales.merge(
        supplier_subset,
        on="supplier_code",
        how="left",
        suffixes=("_sales", "_supplier"),
    )

    # Normalizamos columnas del proveedor de forma segura
    final_cols = {
        "supplier_name": ["supplier_name", "supplier_name_supplier", "supplier_name_sales"],
        "region": ["region", "region_supplier", "region_sales"],
        "avg_lead_time_days": ["avg_lead_time_days"],
        "lead_time_std_days": ["lead_time_std_days"],
        "service_level_target": ["service_level_target"],
        "on_time_delivery_rate": ["on_time_delivery_rate"],
        "shipping_cost_per_unit": ["shipping_cost_per_unit"],
        "risk_factor": ["risk_factor"],
        "criticality": ["criticality"],
    }

    for target, candidates in final_cols.items():
        source_col = _safe_pick_column(merged, candidates)

        if source_col is None:
            merged[target] = pd.NA
        else:
            if source_col != target:
                merged = merged.rename(columns={source_col: target})

            # Reemplazar NaN por default solo si corresponde
            if target in ["supplier_name", "region"]:
                merged[target] = merged[target].fillna("Unknown")
            else:
                merged[target] = merged[target].fillna(pd.NA)

    # Normalizar nombre final para supplier_name/region
    merged["supplier_name"] = merged["supplier_name"].fillna("Unknown Supplier")
    merged["region"] = merged["region"].fillna("Unknown Region")

    # Asegurarse de que columnas numéricas existan
    for col in [
        "avg_lead_time_days",
        "lead_time_std_days",
        "service_level_target",
        "on_time_delivery_rate",
        "shipping_cost_per_unit",
        "risk_factor",
    ]:
        if col in merged.columns:
            merged[col] = pd.to_numeric(merged[col], errors="coerce")

    return merged.sort_values(["sku", "date"]).reset_index(drop=True)

def process_supply_chain_data(sales_path: str | Path, supplier_path: str | Path) -> dict:
    """
    Función principal que procesa los datos, realiza el merge seguro y calcula 
    el resumen por SKU con clasificación ABC compatible con app.py.
    """
    sales_df = pd.read_csv(sales_path)
    supplier_df = pd.read_csv(supplier_path)
    
    # Unir el contexto utilizando nuestra función blindada
    merged_data = merge_supplier_context(sales_df, supplier_df)
    
    # Crear un resumen por SKU con clasificación ABC basada en valor de ventas (Revenue)
    if "sku" in merged_data.columns:
        agg_dict = {
            "units_sold": "sum",
            "unit_price": "mean",
            "unit_cost": "mean",
        }
        for col in ["avg_lead_time_days", "lead_time_std_days", "service_level_target", "on_time_delivery_rate", "shipping_cost_per_unit", "risk_factor"]:
            if col in merged_data.columns:
                agg_dict[col] = "first"

        sku_summary = merged_data.groupby("sku").agg(agg_dict).reset_index()
        
        # Calcular ingresos totales por SKU para la clasificación ABC
        if "units_sold" in sku_summary.columns and "unit_price" in sku_summary.columns:
            sku_summary["total_revenue"] = sku_summary["units_sold"] * sku_summary["unit_price"]
        else:
            sku_summary["total_revenue"] = 1.0

        # Ordenar descendentemente por ingresos
        sku_summary = sku_summary.sort_values(by="total_revenue", ascending=False).reset_index(drop=True)
        
        # Asignar clasificación ABC estándar de forma explícita
        total_rev = sku_summary["total_revenue"].sum()
        if total_rev > 0:
            sku_summary["cum_percentage"] = sku_summary["total_revenue"].cumsum() / total_rev
            # Crear la columna asegurando nombre y tipo string
            sku_summary["abc_class"] = sku_summary["cum_percentage"].apply(
                lambda x: "A" if x <= 0.80 else ("B" if x <= 0.95 else "C")
            )
            sku_summary = sku_summary.drop(columns=["total_revenue", "cum_percentage"])
        else:
            sku_summary["abc_class"] = "B"
            if "total_revenue" in sku_summary.columns:
                sku_summary = sku_summary.drop(columns=["total_revenue"])
    else:
        sku_summary = merged_data.copy()
        sku_summary["abc_class"] = "B"

    # Forzar explícitamente que la columna sea de tipo string y tenga nombre válido
    sku_summary["abc_class"] = sku_summary["abc_class"].astype(str)

    # Retornar el diccionario completo con todas las llaves requeridas por el pipeline
    return {
        "daily_sales": merged_data,
        "merged_data": merged_data,
        "sku_summary": sku_summary
    }