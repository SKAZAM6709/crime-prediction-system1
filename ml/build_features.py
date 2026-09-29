from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = ROOT / "data" / "processed" / "state_monthly_counts.csv"
OUTPUT_FILE = ROOT / "data" / "processed" / "model_features.csv"

LAGS = [1, 2, 3, 12]


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Missing {INPUT_FILE}. Run prepare_data.py first."
        )

    monthly = pd.read_csv(INPUT_FILE)
    monthly.columns = monthly.columns.str.strip()

    required = {"State", "month_start", "incident_count"}
    missing = required - set(monthly.columns)

    if missing:
        raise ValueError(
            f"Missing columns: {sorted(missing)}. "
            f"Found: {monthly.columns.tolist()}. "
            "Run the updated prepare_data.py first."
        )

    monthly["month_start"] = pd.to_datetime(
        monthly["month_start"],
        errors="coerce",
    )
    monthly["incident_count"] = pd.to_numeric(
        monthly["incident_count"],
        errors="coerce",
    )

    monthly = monthly.dropna(
        subset=["State", "month_start", "incident_count"]
    ).copy()

    if monthly.duplicated(["State", "month_start"]).any():
        raise ValueError("Repeated state-month rows in input CSV.")

    features = monthly.rename(
        columns={"incident_count": "target_count"}
    ).copy()

    features["year"] = features["month_start"].dt.year
    features["month"] = features["month_start"].dt.month

    for lag in LAGS:
        past = monthly.rename(
            columns={"incident_count": f"lag_{lag}"}
        ).copy()

        past["month_start"] = (
            past["month_start"] + pd.DateOffset(months=lag)
        )

        features = features.merge(
            past,
            on=["State", "month_start"],
            how="left",
            validate="one_to_one",
        )

    input_rows = len(features)
    features = features.dropna(
        subset=[f"lag_{lag}" for lag in LAGS]
    ).copy()

    if features.empty:
        raise ValueError(
            "No rows have all four previous-month values. "
            "Share the output from prepare_data.py so we can "
            "adjust the lag months."
        )

    features = features.sort_values(
        ["month_start", "State"]
    ).reset_index(drop=True)

    features.to_csv(OUTPUT_FILE, index=False)

    print(f"Input state-month rows: {input_rows:,}")
    print(f"Feature rows: {len(features):,}")
    print(f"Saved: {OUTPUT_FILE}")
    print("\nColumns:", features.columns.tolist())
    print(features.head().to_string(index=False))


if __name__ == "__main__":
    main()