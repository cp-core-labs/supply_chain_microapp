from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

try:
    import plotly.express as px
except Exception:
    px = None

from data_generator import generate_synthetic_supply_chain_data
from modules.data_processor import process_supply_chain_data
from modules.forecaster import forecast_all_skus
from modules.inventory_optimizer import build_inventory_plan
from modules.risk_engine import build_alerts, build_risk_summary, evaluate_what_if_scenario


st.set_page_config(
    page_title="Supply Chain Micro App",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# Premium CSS / compact & visible header
# ==========================================================
st.markdown(
    """
    <style>
        /* General premium background */
        html, body, [class*="css"] {
            background: #0b1220;
            color: #e2e8f0;
        }

        .main {
            background: linear-gradient(180deg, #0b1220 0%, #101827 100%);
        }

        .block-container {
            padding-top: 1.5rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
        }

        /* Visible and compact card header */
        .premium-header {
            background: rgba(15, 23, 42, 0.92);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(148, 163, 184, 0.2);
            box-shadow: 0 4px 20px rgba(2, 6, 23, 0.3);
            padding: 1rem 1.2rem;
            border-radius: 12px;
            margin-bottom: 1rem;
        }

        .premium-title {
            margin: 0;
            font-size: 1.6rem !important;
            line-height: 1.2;
            letter-spacing: -0.02em;
            font-weight: 700;
            color: #f8fafc;
        }

        .premium-subtitle {
            margin-top: 0.25rem;
            color: #cbd5e1;
            font-size: 0.88rem;
            font-weight: 400;
        }

        /* KPI Cards */
        [data-testid="metric-container"] {
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.96), rgba(17, 24, 39, 0.94));
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 16px;
            box-shadow: 0 18px 28px rgba(2, 6, 23, 0.18);
            padding: 1rem 1.1rem;
        }

        [data-testid="metric-container"] label {
            color: #cbd5e1 !important;
            font-size: 0.82rem !important;
            font-weight: 600 !important;
        }

        [data-testid="metric-container"] div {
            color: #f8fafc !important;
            font-size: 1.7rem !important;
            font-weight: 800 !important;
        }

        /* Tabs and tables */
        .stDataFrame {
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid rgba(148, 163, 184, 0.18);
            background: rgba(15, 23, 42, 0.7);
        }

        .stDataFrame > div {
            background: rgba(15, 23, 42, 0.7);
        }

        div[data-testid="stHorizontalBlock"] > div {
            background: transparent;
        }

        h1, h2, h3, h4, h5 {
            color: #f8fafc !important;
        }

        .stMarkdown {
            color: #e2e8f0;
        }

        .stAlert {
            border-radius: 12px;
        }

        .stSelectbox label, .stSlider label {
            color: #e2e8f0 !important;
            font-weight: 600;
        }

        .stSidebar {
            background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
            border-right: 1px solid rgba(148, 163, 184, 0.2);
        }

        .stSidebar .block-container {
            padding-top: 1rem !important;
        }

        .stSidebar label, .stSidebar .stMarkdown p {
            color: #e2e8f0 !important;
        }

        .stSidebar .stSlider [data-testid="stBaseSlider"] {
            background: rgba(15, 23, 42, 0.75);
        }

        .content-wrapper {
            padding-top: 0.3rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# Data loading
# ==========================================================
@st.cache_data
def load_or_generate_data() -> dict:
    sales_path = Path("data/historical_sales.csv")
    supplier_path = Path("data/suppliers_lead_time.csv")

    if not sales_path.exists() or not supplier_path.exists():
        generate_synthetic_supply_chain_data(
            output_dir="data",
            n_skus=40,
            n_days=730,
            seed=42,
        )

    return process_supply_chain_data(
        sales_path=sales_path,
        supplier_path=supplier_path,
    )


@st.cache_data
def compute_forecast_pipeline(daily_sales: pd.DataFrame, horizon: int = 30) -> pd.DataFrame:
    return forecast_all_skus(daily_sales, horizon=horizon)


@st.cache_data
def compute_inventory_pipeline(processed_data: dict, service_level: float = 0.95) -> pd.DataFrame:
    return build_inventory_plan(processed_data, service_level=service_level)


# ==========================================================
# Render sections
# ==========================================================
def render_overview(inventory_df: pd.DataFrame):
    st.subheader("Executive Overview")

    inventory_df = build_alerts(inventory_df)

    total_skus = inventory_df["sku"].nunique()
    avg_daily_demand = float(inventory_df["avg_daily_demand"].mean())
    annual_demand = float(inventory_df["annual_demand"].sum())
    avg_risk = float(inventory_df["risk_score"].mean())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("SKUs", total_skus)
    c2.metric("Avg Daily Demand", f"{avg_daily_demand:.1f}")
    c3.metric("Annual Demand", f"{annual_demand:,.0f}")
    c4.metric("Avg Risk Score", f"{avg_risk:.1f}")

    col_a, col_b = st.columns(2)

    abc_counts = (
        inventory_df["abc_class"]
        .value_counts()
        .reindex(["A", "B", "C"], fill_value=0)
        .reset_index()
    )
    abc_counts.columns = ["abc_class", "sku_count"]
    abc_counts["abc_class"] = abc_counts["abc_class"].astype(str)

    if px is not None:
        fig_abc = px.bar(
            abc_counts,
            x="abc_class",
            y="sku_count",
            color="abc_class",
            color_discrete_sequence=["#3b82f6", "#22c55e", "#f59e0b"],
            title="ABC Classification",
        )
        fig_abc.update_layout(
            paper_bgcolor="rgba(15, 23, 42, 0.8)",
            plot_bgcolor="rgba(15, 23, 42, 0.8)",
            font={"color": "#e2e8f0"},
            legend={"font": {"color": "#e2e8f0"}},
        )
        col_a.plotly_chart(fig_abc, use_container_width=True)
    else:
        col_a.dataframe(abc_counts, use_container_width=True)

    risk_summary = build_risk_summary(inventory_df)
    if not risk_summary.empty and px is not None:
        fig_risk = px.bar(
            risk_summary,
            x="alert_level",
            y="total_risk_score",
            color="alert_level",
            color_discrete_map={"Green": "#22c55e", "Yellow": "#f59e0b", "Red": "#ef4444", "Verde": "#22c55e", "Amarillo": "#f59e0b", "Rojo": "#ef4444"},
            title="Operational Risk by Alert Level",
        )
        fig_risk.update_layout(
            paper_bgcolor="rgba(15, 23, 42, 0.8)",
            plot_bgcolor="rgba(15, 23, 42, 0.8)",
            font={"color": "#e2e8f0"},
            legend={"font": {"color": "#e2e8f0"}},
        )
        col_b.plotly_chart(fig_risk, use_container_width=True)
    else:
        col_b.dataframe(risk_summary, use_container_width=True)

    st.markdown("### SKU Operating Plan")
    display_df = inventory_df[
        [
            "sku",
            "product_name",
            "category",
            "abc_class",
            "ved_class",
            "avg_daily_demand",
            "annual_dollar_usage",
            "safety_stock",
            "reorder_point",
            "eoq",
            "days_of_coverage",
            "stockout_probability",
            "alert_level",
            "risk_score",
        ]
    ].sort_values("risk_score", ascending=False)

    st.dataframe(display_df, use_container_width=True, height=420)


def render_forecast(processed_data: dict, forecast_df: pd.DataFrame):
    st.subheader("Demand Forecast")

    daily_sales = processed_data["daily_sales"]
    sku_list = sorted(daily_sales["sku"].unique())
    selected_sku = st.selectbox("Select a SKU", sku_list)

    sku_forecast = forecast_df[forecast_df["sku"] == selected_sku].sort_values("date")
    if sku_forecast.empty:
        st.warning("No forecast data available for this SKU.")
        return

    if px is not None:
        fig = px.line(
            sku_forecast,
            x="date",
            y=["forecast_units", "lower_bound", "upper_bound"],
            title=f"Forecast for {selected_sku}",
            labels={"date": "Date", "value": "Units"},
        )
        fig.update_layout(
            paper_bgcolor="rgba(15, 23, 42, 0.8)",
            plot_bgcolor="rgba(15, 23, 42, 0.8)",
            font={"color": "#e2e8f0"},
            legend={"font": {"color": "#e2e8f0"}},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.line_chart(sku_forecast.set_index("date")[["forecast_units", "lower_bound", "upper_bound"]])

    st.dataframe(
        sku_forecast.tail(15)[
            ["date", "sku", "forecast_units", "lower_bound", "upper_bound", "selected_model"]
        ],
        use_container_width=True,
    )


def render_inventory(inventory_df: pd.DataFrame):
    st.subheader("Inventory & Optimization")

    inventory_df = build_alerts(inventory_df)

    display_cols = [
        "sku",
        "product_name",
        "category",
        "abc_class",
        "ved_class",
        "avg_daily_demand",
        "annual_dollar_usage",
        "safety_stock",
        "reorder_point",
        "eoq",
        "days_of_coverage",
        "stockout_probability",
        "alert_level",
        "risk_score",
    ]

    st.dataframe(
        inventory_df[display_cols].sort_values("risk_score", ascending=False),
        use_container_width=True,
        height=520,
    )

    summary = (
        inventory_df.groupby("category", as_index=False)
        .agg(
            sku_count=("sku", "nunique"),
            avg_daily_demand=("avg_daily_demand", "mean"),
            total_safety_stock=("safety_stock", "sum"),
            total_reorder_point=("reorder_point", "sum"),
            avg_stockout_probability=("stockout_probability", "mean"),
        )
        .sort_values("avg_stockout_probability", ascending=False)
    )
    st.dataframe(summary, use_container_width=True)


def render_risk(alerts_df: pd.DataFrame):
    st.subheader("Operational Alerts")

    risk_summary = build_risk_summary(alerts_df)
    if not risk_summary.empty:
        st.dataframe(risk_summary, use_container_width=True)

    st.dataframe(
        alerts_df[
            [
                "sku",
                "product_name",
                "category",
                "abc_class",
                "ved_class",
                "risk_score",
                "stockout_probability",
                "days_of_coverage",
                "alert_level",
                "priority_label",
            ]
        ].sort_values("risk_score", ascending=False),
        use_container_width=True,
        height=500,
    )


def render_scenarios(inventory_df: pd.DataFrame):
    st.subheader("Scenario Analysis")

    col1, col2 = st.columns(2)
    demand_change_pct = col1.slider(
        "Demand Change (%)",
        min_value=-50,
        max_value=50,
        value=20,
        step=5,
    ) / 100.0

    lead_time_change_days = col2.slider(
        "Lead Time Change (days)",
        min_value=-10,
        max_value=20,
        value=3,
        step=1,
    )

    scenario_df = evaluate_what_if_scenario(
        inventory_df,
        demand_change_pct=demand_change_pct,
        lead_time_change_days=lead_time_change_days,
        service_level=0.95,
    )

    st.dataframe(
        scenario_df[
            [
                "sku",
                "product_name",
                "avg_daily_demand",
                "scenario_avg_daily_demand",
                "avg_lead_time_days",
                "scenario_lead_time_days",
                "scenario_reorder_point",
                "scenario_risk_score",
                "scenario_alert_level",
            ]
        ].sort_values("scenario_risk_score", ascending=False),
        use_container_width=True,
        height=500,
    )


def render_export(alerts_df: pd.DataFrame):
    st.subheader("Export")

    export_df = alerts_df[
        [
            "sku",
            "product_name",
            "category",
            "abc_class",
            "ved_class",
            "avg_daily_demand",
            "safety_stock",
            "reorder_point",
            "eoq",
            "stockout_probability",
            "risk_score",
            "alert_level",
            "priority_label",
        ]
    ]

    csv_data = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Inventory and Alerts (.csv)",
        data=csv_data,
        file_name="inventory_alerts.csv",
        mime="text/csv",
    )


# ==========================================================
# Main flow
# ==========================================================
def main():
    processed_data = load_or_generate_data()
    daily_sales = processed_data["daily_sales"]

    st.sidebar.title("Configuration")
    st.sidebar.caption("Supply Chain Monitoring")

    forecast_horizon = st.sidebar.slider(
        "Forecast Horizon (days)",
        min_value=7,
        max_value=180,
        value=30,
        step=7,
    )

    service_level = st.sidebar.slider(
        "Target Service Level",
        min_value=0.80,
        max_value=0.99,
        value=0.95,
        step=0.01,
    )

    if "active_section" not in st.session_state:
        st.session_state.active_section = "Overview"

    # Visible and structured header
    st.markdown(
        """
        <div class="premium-header">
            <div class="premium-title">Supply Chain &amp; Inventory Optimization Platform</div>
            <div class="premium-subtitle">Operational intelligence for demand planning, stock risk and inventory strategy</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sections = ["Overview", "Forecast", "Inventory", "Risk", "Scenarios", "Export"]
    cols = st.columns(len(sections))

    for i, item in enumerate(sections):
        with cols[i]:
            is_active = st.session_state.active_section == item
            btn_type = "primary" if is_active else "secondary"
            if st.button(item, use_container_width=True, type=btn_type):
                st.session_state.active_section = item
                st.rerun()

    active_section = st.session_state.active_section

    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)

    forecast_df = compute_forecast_pipeline(daily_sales, horizon=forecast_horizon)
    raw_inventory_df = compute_inventory_pipeline(processed_data, service_level=service_level)
    
    inventory_df = build_alerts(raw_inventory_df)
    alerts_df = inventory_df

    if active_section == "Overview":
        render_overview(inventory_df)
    elif active_section == "Forecast":
        render_forecast(processed_data, forecast_df)
    elif active_section == "Inventory":
        render_inventory(inventory_df)
    elif active_section == "Risk":
        render_risk(alerts_df)
    elif active_section == "Scenarios":
        render_scenarios(inventory_df)
    elif active_section == "Export":
        render_export(alerts_df)

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()