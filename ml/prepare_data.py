from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW_FILE = ROOT / "data" / "raw" / "US_Crime_DataSet.csv"
OUTPUT_DIR = ROOT / "data" / "processed"

CLEAN_FILE = OUTPUT_DIR / "incidents_clean.csv"
MONTHLY_FILE = OUTPUT_DIR / "state_monthly_counts.csv"

MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def main():
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"CSV not found: {RAW_FILE}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(RAW_FILE, low_memory=False)
    df.columns = df.columns.str.strip()

    required = {"Record ID", "State", "Year", "Month"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Missing CSV columns: {sorted(missing)}")

    original_count = len(df)

    df["Record ID"] = df["Record ID"].astype("string").str.strip()
    df["State"] = df["State"].astype("string").str.strip()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

    month_names = df["Month"].astype("string").str.strip().str.lower()
    df["month_number"] = month_names.map(MONTHS)

    df["Record ID"] = df["Record ID"].replace("", pd.NA)
    df["State"] = df["State"].replace("", pd.NA)

    df = df.dropna(
        subset=["Record ID", "State", "Year", "month_number"]
    ).copy()

    df["Year"] = df["Year"].astype(int)
    df["month_number"] = df["month_number"].astype(int)
    df = df[df["Year"].between(1900, 2100)].copy()

    df = df.drop_duplicates(subset=["Record ID"]).copy()

    df["month_start"] = pd.to_datetime(
        {
            "year": df["Year"],
            "month": df["month_number"],
            "day": 1,
        },
        errors="coerce",
    )

    df = df.dropna(subset=["month_start"]).copy()
    df.to_csv(CLEAN_FILE, index=False)

    # One cleaned record contributes one count.
    monthly = (
        df.groupby(["State", "month_start"], as_index=False)
        .size()
        .rename(columns={"size": "incident_count"})
        .sort_values(["State", "month_start"])
        .reset_index(drop=True)
    )

    monthly.to_csv(MONTHLY_FILE, index=False)

    print(f"Original records: {original_count:,}")
    print(f"Clean records: {len(df):,}")
    print(f"State-month rows: {len(monthly):,}")
    print(f"Saved: {CLEAN_FILE}")
    print(f"Saved: {MONTHLY_FILE}")
    print("\nCSV columns:", monthly.columns.tolist())
    print(monthly.head().to_string(index=False))


if __name__ == "__main__":
    main()