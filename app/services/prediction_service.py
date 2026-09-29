from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]

MONTHLY_FILE = (
    PROJECT_ROOT / "data" / "processed" / "state_monthly_counts.csv"
)

MODEL_FILE = (
    PROJECT_ROOT
    / "backend"
    / "ml"
    / "artifacts"
    / "monthly_forecast_model.joblib"
)


def available_states() -> list[str]:
    if not MONTHLY_FILE.exists():
        raise FileNotFoundError(
            "state_monthly_counts.csv is missing. "
            "Run prepare_data.py."
        )

    df = pd.read_csv(MONTHLY_FILE, usecols=["State"])
    return sorted(df["State"].dropna().unique().tolist())


def forecast_next_month(state: str) -> dict:
    if not MONTHLY_FILE.exists():
        raise FileNotFoundError(
            "Monthly data is missing. Run prepare_data.py."
        )

    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            "Trained model is missing. Run train.py."
        )

    monthly = pd.read_csv(MONTHLY_FILE)
    monthly["month_start"] = pd.to_datetime(
        monthly["month_start"]
    )

    state_data = monthly[
        monthly["State"].str.casefold() == state.casefold()
    ].copy()

    if state_data.empty:
        raise ValueError(f"State not found: {state}")

    state_data = state_data.sort_values("month_start")
    state_name = str(state_data["State"].iloc[0])

    latest_month = state_data["month_start"].max()
    forecast_month = latest_month + pd.DateOffset(months=1)

    # Look up counts by actual calendar month.
    counts_by_month = state_data.set_index(
        "month_start"
    )["incident_count"]

    lags = {}

    for months_back in [1, 2, 3, 12]:
        required_month = (
            forecast_month - pd.DateOffset(months=months_back)
        )

        if required_month not in counts_by_month.index:
            raise ValueError(
                f"Cannot forecast {state_name}: historical "
                f"month {required_month:%Y-%m} is missing."
            )

        lags[f"lag_{months_back}"] = int(
            counts_by_month.loc[required_month]
        )

    model_input = pd.DataFrame(
        [
            {
                "State": state_name,
                "month": int(forecast_month.month),
                **lags,
            }
        ]
    )

    model = joblib.load(MODEL_FILE)
    raw_prediction = float(model.predict(model_input)[0])

    return {
        "state": state_name,
        "latest_data_month": latest_month.strftime("%Y-%m"),
        "forecast_month": forecast_month.strftime("%Y-%m"),
        "predicted_incidents": max(0, round(raw_prediction)),
        "previous_month_incidents": lags["lag_1"],
    }