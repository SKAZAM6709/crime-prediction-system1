from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


ROOT = Path(__file__).resolve().parents[2]

FEATURE_FILE = ROOT / "data" / "processed" / "model_features.csv"
ARTIFACT_DIR = ROOT / "backend" / "ml" / "artifacts"
RESULTS_DIR = ROOT / "data" / "processed"

MODEL_FILE = ARTIFACT_DIR / "monthly_forecast_model.joblib"
METADATA_FILE = ARTIFACT_DIR / "model_metadata.json"
PREDICTIONS_FILE = RESULTS_DIR / "test_predictions.csv"

FEATURE_COLUMNS = [
    "State",
    "month",
    "lag_1",
    "lag_2",
    "lag_3",
    "lag_12",
]

TARGET_COLUMN = "target_count"


def calculate_metrics(actual, predicted):
    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))

    return {
        "mae": round(float(mae), 3),
        "rmse": round(float(rmse), 3),
    }


def main():
    if not FEATURE_FILE.exists():
        raise FileNotFoundError(
            f"Missing {FEATURE_FILE}\n"
            "Run backend/ml/build_features.py first."
        )

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(FEATURE_FILE)
    df.columns = df.columns.str.strip()

    required = set(
        ["month_start", TARGET_COLUMN] + FEATURE_COLUMNS
    )
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing columns in model_features.csv: {sorted(missing)}"
        )

    df["month_start"] = pd.to_datetime(
        df["month_start"],
        errors="coerce",
    )

    for column in [
        "month",
        "lag_1",
        "lag_2",
        "lag_3",
        "lag_12",
        TARGET_COLUMN,
    ]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df = df.dropna(
        subset=["month_start"] + FEATURE_COLUMNS + [TARGET_COLUMN]
    ).copy()

    df = df.sort_values(
        ["month_start", "State"]
    ).reset_index(drop=True)

    # Split by calendar month, rather than randomly splitting rows.
    unique_months = sorted(df["month_start"].unique())

    if len(unique_months) < 12:
        raise ValueError(
            f"Only {len(unique_months)} usable months were found. "
            "We need at least 12 to make a useful time-based split."
        )

    test_month_count = max(1, int(len(unique_months) * 0.20))
    test_start = unique_months[-test_month_count]

    train_df = df[df["month_start"] < test_start].copy()
    test_df = df[df["month_start"] >= test_start].copy()

    if train_df.empty or test_df.empty:
        raise ValueError("The training or test set is empty.")

    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET_COLUMN]

    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET_COLUMN]

    # Turn state names into numeric columns. Unknown states at
    # prediction time will not crash the encoder.
    preprocessing = ColumnTransformer(
        transformers=[
            (
                "state",
                OneHotEncoder(handle_unknown="ignore"),
                ["State"],
            ),
            (
                "numbers",
                "passthrough",
                [
                    "month",
                    "lag_1",
                    "lag_2",
                    "lag_3",
                    "lag_12",
                ],
            ),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocessing", preprocessing),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=100,
                    min_samples_leaf=3,
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    print("Training model...")
    model.fit(X_train, y_train)

    # The baseline simply repeats the previous month's count.
    baseline_predictions = X_test["lag_1"].to_numpy()

    # Incident counts cannot be negative; round for display.
    model_predictions = np.clip(
        model.predict(X_test),
        a_min=0,
        a_max=None,
    )

    baseline_metrics = calculate_metrics(
        y_test,
        baseline_predictions,
    )
    model_metrics = calculate_metrics(
        y_test,
        model_predictions,
    )

    results = test_df[
        ["State", "month_start", TARGET_COLUMN]
    ].copy()

    results["baseline_prediction"] = baseline_predictions
    results["model_prediction"] = np.round(
        model_predictions,
        2,
    )

    results.to_csv(PREDICTIONS_FILE, index=False)
    model.fit(df[FEATURE_COLUMNS], df[TARGET_COLUMN])
    joblib.dump(model, MODEL_FILE)

    metadata = {
        "target": "monthly reported incident count by state",
        "feature_columns": FEATURE_COLUMNS,
        "training_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "training_end": str(
            train_df["month_start"].max().date()
        ),
        "test_start": str(
            test_df["month_start"].min().date()
        ),
        "test_end": str(
            test_df["month_start"].max().date()
        ),
        "baseline_metrics": baseline_metrics,
        "model_metrics": model_metrics,
    }

    with METADATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)

    print(f"\nTraining rows: {len(train_df):,}")
    print(f"Test rows: {len(test_df):,}")
    print(
        "Training ends: "
        f"{train_df['month_start'].max().date()}"
    )
    print(
        "Test period: "
        f"{test_df['month_start'].min().date()} to "
        f"{test_df['month_start'].max().date()}"
    )

    print("\nBASELINE")
    print(f"MAE:  {baseline_metrics['mae']}")
    print(f"RMSE: {baseline_metrics['rmse']}")

    print("\nRANDOM FOREST MODEL")
    print(f"MAE:  {model_metrics['mae']}")
    print(f"RMSE: {model_metrics['rmse']}")

    print(f"\nSaved model: {MODEL_FILE}")
    print(f"Saved metadata: {METADATA_FILE}")
    print(f"Saved test predictions: {PREDICTIONS_FILE}")


if __name__ == "__main__":
    main()