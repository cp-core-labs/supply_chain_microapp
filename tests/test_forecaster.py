import pandas as pd

from modules.forecaster import forecast_sku, evaluate_model_on_validation


def build_sample_sku_series():
    dates = pd.date_range("2024-01-01", periods=60, freq="D")
    values = [30, 32, 35, 34, 38, 40, 42, 41, 45, 47,
              50, 49, 52, 54, 58, 60, 57, 55, 62, 64,
              66, 63, 68, 70, 73, 72, 75, 79, 80, 82,
              79, 78, 83, 86, 89, 91, 90, 88, 93, 95,
              98, 96, 100, 102, 106, 105, 110, 113, 116, 115,
              119, 122, 124, 123, 126, 129, 132, 130, 135, 137]

    df = pd.DataFrame({
        "date": dates,
        "sku": "SKU-001",
        "units_sold": values,
    })
    return df


def test_evaluate_model_on_validation_returns_metrics():
    series = pd.Series(build_sample_sku_series()["units_sold"].values)
    result = evaluate_model_on_validation("naive", series, horizon=14)

    assert "model" in result
    assert "forecast" in result
    assert "metrics" in result
    assert set(result["metrics"].keys()) >= {"mae", "rmse", "mape", "mase"}


def test_forecast_sku_returns_confidence_interval_and_model():
    sample = build_sample_sku_series()
    result = forecast_sku(sample, horizon=14)

    assert result["sku"] == "SKU-001"
    assert "selected_model" in result
    assert "forecast_df" in result
    assert "metrics" in result
    assert "confidence_interval" in result

    forecast_df = result["forecast_df"]
    assert "forecast_units" in forecast_df.columns
    assert "lower_bound" in forecast_df.columns
    assert "upper_bound" in forecast_df.columns
    assert forecast_df["forecast_units"].notna().all()