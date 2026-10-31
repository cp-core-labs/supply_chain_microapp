from __future__ import annotations

import warnings
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
except Exception:  # pragma: no cover
    ExponentialSmoothing = None

try:
    from prophet import Prophet
except Exception:  # pragma: no cover
    Prophet = None

try:
    from xgboost import XGBRegressor
except Exception:  # pragma: no cover
    XGBRegressor = None


def _safe_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    denom = np.where(np.abs(y_true) > 1e-8, np.abs(y_true), 1.0)
    return float(np.mean(np.abs((y_true - y_pred) / denom)) * 100.0)


def _safe_mase(y_true: np.ndarray, y_pred: np.ndarray, train_series: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    train_series = np.asarray(train_series, dtype=float)

    mae = mean_absolute_error(y_true, y_pred)
    if len(train_series) < 2:
        return 0.0

    diffs = np.abs(np.diff(train_series))
    denom = np.mean(diffs) if np.mean(diffs) > 1e-8 else 1.0
    return float(mae / denom)


def _compute_metrics(
    y_true: np.ndarray, y_pred: np.ndarray, train_series: np.ndarray
) -> Dict[str, float]:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae = float(mean_absolute_error(y_true, y_pred))
    mape = _safe_mape(y_true, y_pred)
    mase = _safe_mase(y_true, y_pred, train_series)

    return {
        "mae": mae,
        "rmse": rmse,
        "mape": mape,
        "mase": mase,
    }


def _resolve_validation_split(series: pd.Series, horizon: int) -> Tuple[int, int]:
    n = len(series)
    default_val = max(14, min(60, n // 5))
    validation_size = min(default_val, max(horizon, 14))
    validation_size = min(validation_size, max(1, n - 2))
    train_size = n - validation_size
    return train_size, validation_size


def naive_forecast(train_series: pd.Series, horizon: int) -> np.ndarray:
    last_value = float(train_series.iloc[-1])
    return np.full(horizon, last_value, dtype=float)


def moving_average_forecast(train_series: pd.Series, horizon: int, window: int = 7) -> np.ndarray:
    s = train_series.astype(float).copy()
    window = max(2, min(window, len(s)))
    last_window = s.iloc[-window:].to_numpy(dtype=float)
    forecast_value = float(np.mean(last_window))
    return np.full(horizon, forecast_value, dtype=float)


def holt_winters_forecast(train_series: pd.Series, horizon: int) -> np.ndarray:
    if ExponentialSmoothing is None:
        return naive_forecast(train_series, horizon)

    s = train_series.astype(float).copy()
    if len(s) < 3:
        return naive_forecast(s, horizon)

    seasonal_period = min(7, max(2, len(s) // 3))
    seasonal_period = max(2, min(seasonal_period, len(s) // 2))

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = ExponentialSmoothing(
                s,
                trend="add",
                seasonal="add",
                seasonal_periods=seasonal_period,
                initialization_method="estimated",
            ).fit(optimized=True, use_brute=True)
        forecast = model.forecast(horizon)
        return np.asarray(forecast, dtype=float)
    except Exception:
        return naive_forecast(s, horizon)


def prophet_forecast(
    train_series: pd.Series, horizon: int, dates: Optional[pd.DatetimeIndex] = None
) -> np.ndarray:
    if Prophet is None:
        return naive_forecast(train_series, horizon)

    s = train_series.astype(float).copy()
    if len(s) < 10:
        return naive_forecast(s, horizon)

    if dates is None:
        start_date = pd.Timestamp("2023-01-01")
        dates = pd.date_range(start=start_date, periods=len(s), freq="D")

    df = pd.DataFrame(
        {
            "ds": dates[: len(s)],
            "y": s.to_numpy(),
        }
    )

    try:
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode="multiplicative",
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10.0,
        )
        model.fit(df)
        future = model.make_future_dataframe(periods=horizon, freq="D")
        predicted = model.predict(future)
        return predicted["yhat"].tail(horizon).to_numpy(dtype=float)
    except Exception:
        return naive_forecast(s, horizon)


def _prepare_xgb_features(history_values: pd.Series, future_date: pd.Timestamp) -> Dict[str, float]:
    values = history_values.astype(float).to_numpy()

    lag_1 = float(values[-1]) if len(values) >= 1 else 0.0
    lag_7 = (
        float(values[-7]) if len(values) >= 7 else float(values[-1]) if len(values) >= 1 else 0.0
    )
    lag_14 = (
        float(values[-14]) if len(values) >= 14 else float(values[-1]) if len(values) >= 1 else 0.0
    )
    lag_30 = (
        float(values[-30]) if len(values) >= 30 else float(values[-1]) if len(values) >= 1 else 0.0
    )

    rolling_3 = (
        float(np.mean(values[-3:]))
        if len(values) >= 3
        else float(np.mean(values)) if len(values) > 0 else 0.0
    )
    rolling_7 = (
        float(np.mean(values[-7:]))
        if len(values) >= 7
        else float(np.mean(values)) if len(values) > 0 else 0.0
    )
    rolling_14 = (
        float(np.mean(values[-14:]))
        if len(values) >= 14
        else float(np.mean(values)) if len(values) > 0 else 0.0
    )

    std_7 = float(np.std(values[-7:])) if len(values) >= 2 else 0.0
    std_14 = float(np.std(values[-14:])) if len(values) >= 2 else 0.0

    return {
        "lag_1": lag_1,
        "lag_7": lag_7,
        "lag_14": lag_14,
        "lag_30": lag_30,
        "rolling_mean_3": rolling_3,
        "rolling_mean_7": rolling_7,
        "rolling_mean_14": rolling_14,
        "rolling_std_7": std_7,
        "rolling_std_14": std_14,
        "day_of_week": float(future_date.day_of_week),
        "month": float(future_date.month),
        "day_of_year": float(future_date.day_of_year),
        "is_weekend": float(int(future_date.day_of_week >= 5)),
    }


def _build_xgb_training_matrix(series: pd.Series) -> Tuple[pd.DataFrame, pd.Series]:
    values = series.astype(float).to_numpy()
    rows = []
    targets = []

    for idx in range(1, len(values)):
        date = pd.Timestamp("2023-01-01") + pd.Timedelta(days=idx)
        row = _prepare_xgb_features(pd.Series(values[:idx]), date)
        rows.append(row)
        targets.append(float(values[idx]))

    if not rows:
        return pd.DataFrame(), pd.Series(dtype=float)

    X = pd.DataFrame(rows)
    y = pd.Series(targets, name="y")
    return X, y


def xgboost_forecast(train_series: pd.Series, horizon: int) -> np.ndarray:
    if XGBRegressor is None:
        return naive_forecast(train_series, horizon)

    s = train_series.astype(float).copy().reset_index(drop=True)
    if len(s) < 15:
        return naive_forecast(s, horizon)

    X_train, y_train = _build_xgb_training_matrix(s)
    if X_train.empty or y_train.empty:
        return naive_forecast(s, horizon)

    try:
        model = XGBRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="reg:squarederror",
            random_state=42,
            n_jobs=-1,
        )
        model.fit(X_train, y_train)

        history_values = s.to_list()
        last_date = pd.Timestamp("2023-01-01") + pd.Timedelta(days=len(s) - 1)
        forecast_values = []

        for step in range(1, horizon + 1):
            future_date = last_date + pd.Timedelta(days=step)
            feature_row = _prepare_xgb_features(pd.Series(history_values), future_date)
            pred = float(model.predict(pd.DataFrame([feature_row]))[0])
            pred = max(0.0, pred)
            history_values.append(pred)
            forecast_values.append(pred)

        return np.asarray(forecast_values, dtype=float)

    except Exception:
        return naive_forecast(s, horizon)


def _fit_model_and_predict(
    model_name: str, train_series: pd.Series, horizon: int, dates: Optional[pd.DatetimeIndex] = None
) -> np.ndarray:
    if model_name == "naive":
        return naive_forecast(train_series, horizon)
    if model_name == "moving_average":
        return moving_average_forecast(train_series, horizon, window=7)
    if model_name == "holt_winters":
        return holt_winters_forecast(train_series, horizon)
    if model_name == "prophet":
        return prophet_forecast(train_series, horizon, dates=dates)
    if model_name == "xgboost":
        return xgboost_forecast(train_series, horizon)
    raise ValueError(f"Modelo no soportado: {model_name}")


def evaluate_model_on_validation(
    model_name: str, series: pd.Series, horizon: int
) -> Dict[str, object]:
    series = pd.Series(series).astype(float).copy()
    if len(series) < 10:
        raise ValueError("La serie es demasiado corta para evaluación.")

    train_size, validation_size = _resolve_validation_split(series, horizon)
    train = series.iloc[:train_size].copy()
    valid = series.iloc[train_size : train_size + validation_size].copy()

    if valid.empty:
        raise ValueError("No se pudo crear una validación útil.")

    dates = pd.date_range(start="2023-01-01", periods=len(train), freq="D")
    forecast = _fit_model_and_predict(model_name, train, len(valid), dates=dates)

    if len(forecast) < len(valid):
        forecast = np.resize(forecast, len(valid))

    y_true = valid.to_numpy(dtype=float)
    y_pred = np.asarray(forecast[: len(valid)], dtype=float)
    metrics = _compute_metrics(y_true, y_pred, train.to_numpy(dtype=float))

    return {
        "model": model_name,
        "forecast": y_pred,
        "metrics": metrics,
        "train_length": len(train),
        "validation_length": len(valid),
    }


def select_best_model(
    series: pd.Series, horizon: int, candidate_models: Optional[List[str]] = None
) -> Dict[str, object]:
    if candidate_models is None:
        candidate_models = ["naive", "moving_average", "holt_winters"]
        if Prophet is not None:
            candidate_models.append("prophet")
        if XGBRegressor is not None:
            candidate_models.append("xgboost")

    results = []
    for model_name in candidate_models:
        try:
            evaluation = evaluate_model_on_validation(model_name, series, horizon)
            results.append(evaluation)
        except Exception:
            continue

    if not results:
        raise ValueError("No fue posible evaluar ningún modelo para esta serie.")

    selected = sorted(
        results,
        key=lambda r: (
            r["metrics"]["mape"],
            r["metrics"]["rmse"],
            r["metrics"]["mae"],
        ),
    )[0]

    return selected


def _build_confidence_intervals(
    forecast: np.ndarray, historical_series: pd.Series
) -> Tuple[np.ndarray, np.ndarray]:
    forecast = np.asarray(forecast, dtype=float)
    hist = historical_series.astype(float).to_numpy()

    if hist.size == 0:
        return forecast, forecast

    residuals = np.diff(hist)
    residual_std = (
        float(np.std(residuals, ddof=0)) if residuals.size > 0 else float(np.std(hist, ddof=0))
    )
    if residual_std < 1e-8:
        residual_std = float(np.std(hist, ddof=0)) if hist.size > 0 else 1.0
    if residual_std < 1e-8:
        residual_std = 1.0

    z_value = 1.2816
    lower = forecast - (z_value * residual_std)
    upper = forecast + (z_value * residual_std)

    lower = np.maximum(lower, 0.0)
    upper = np.maximum(upper, lower + 1e-6)

    return lower, upper


def generate_future_forecast(
    series: pd.Series, horizon: int, model_name: str, dates: Optional[pd.DatetimeIndex] = None
) -> Tuple[np.ndarray, pd.DatetimeIndex]:
    s = pd.Series(series).astype(float).copy()

    if dates is None:
        start = pd.Timestamp("2023-01-01")
        dates = pd.date_range(start=start, periods=len(s), freq="D")

    future_dates = pd.date_range(start=dates[-1] + pd.Timedelta(days=1), periods=horizon, freq="D")
    forecast = _fit_model_and_predict(model_name, s, horizon, dates=dates)

    if len(forecast) < horizon:
        forecast = np.resize(forecast, horizon)
    return np.asarray(forecast[:horizon], dtype=float), future_dates


def forecast_sku(
    sku_df: pd.DataFrame,
    horizon: int = 30,
    candidate_models: Optional[List[str]] = None,
) -> Dict[str, object]:
    sku_df = sku_df.copy()
    sku_df["date"] = pd.to_datetime(sku_df["date"], errors="coerce")
    sku_df = sku_df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)

    if sku_df.empty:
        raise ValueError("El DataFrame del SKU está vacío.")

    sku_code = str(sku_df["sku"].iloc[0]) if "sku" in sku_df.columns else "UNKNOWN_SKU"
    series = sku_df["units_sold"].astype(float).reset_index(drop=True)

    if candidate_models is None:
        candidate_models = ["naive", "moving_average", "holt_winters"]
        if Prophet is not None:
            candidate_models.append("prophet")
        if XGBRegressor is not None:
            candidate_models.append("xgboost")

    best = select_best_model(series, horizon=horizon, candidate_models=candidate_models)
    selected_model = best["model"]

    history_dates = pd.date_range(start="2023-01-01", periods=len(series), freq="D")
    future_forecast, future_dates = generate_future_forecast(
        series,
        horizon=horizon,
        model_name=selected_model,
        dates=history_dates,
    )

    lower, upper = _build_confidence_intervals(future_forecast, series)

    future_df = pd.DataFrame(
        {
            "date": future_dates,
            "sku": sku_code,
            "forecast_units": np.round(future_forecast, 2),
            "lower_bound": np.round(lower, 2),
            "upper_bound": np.round(upper, 2),
            "selected_model": selected_model,
        }
    )

    history_df = (
        sku_df[["date", "sku", "units_sold"]]
        .rename(columns={"units_sold": "forecast_units"})
        .copy()
    )
    history_df["lower_bound"] = np.nan
    history_df["upper_bound"] = np.nan
    history_df["selected_model"] = "historical"

    combined = pd.concat([history_df, future_df], ignore_index=True, sort=False)
    combined = combined.sort_values("date").reset_index(drop=True)

    evaluation_results = []
    for model_name in candidate_models:
        try:
            eval_result = evaluate_model_on_validation(model_name, series, horizon)
            evaluation_results.append(
                {
                    "model": model_name,
                    "metrics": eval_result["metrics"],
                }
            )
        except Exception:
            continue

    return {
        "sku": sku_code,
        "selected_model": selected_model,
        "forecast_df": combined,
        "metrics": best["metrics"],
        "confidence_interval": {
            "lower": lower,
            "upper": upper,
        },
        "all_model_evaluations": evaluation_results,
    }


def forecast_all_skus(
    daily_sales_df: pd.DataFrame,
    horizon: int = 30,
    candidate_models: Optional[List[str]] = None,
) -> pd.DataFrame:
    daily_sales_df = daily_sales_df.copy()
    daily_sales_df["date"] = pd.to_datetime(daily_sales_df["date"], errors="coerce")
    daily_sales_df = (
        daily_sales_df.dropna(subset=["date"]).sort_values(["sku", "date"]).reset_index(drop=True)
    )

    if daily_sales_df.empty:
        raise ValueError("No hay datos de ventas para forecast.")

    all_forecasts = []
    for sku in pd.unique(daily_sales_df["sku"].dropna()):
        sku_df = daily_sales_df[daily_sales_df["sku"] == sku].copy()
        result = forecast_sku(sku_df, horizon=horizon, candidate_models=candidate_models)
        forecast_df = result["forecast_df"].copy()
        forecast_df["selected_model"] = result["selected_model"]
        all_forecasts.append(forecast_df)

    if not all_forecasts:
        return pd.DataFrame()

    combined = pd.concat(all_forecasts, ignore_index=True)
    return combined.sort_values(["sku", "date"]).reset_index(drop=True)
