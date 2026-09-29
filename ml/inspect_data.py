from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW_FILE = ROOT / "data" / "raw" / "US_Crime_DataSet.csv"


def main():
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"CSV not found: {RAW_FILE}")

    df = pd.read_csv(RAW_FILE, low_memory=False)
    df.columns = df.columns.str.strip()

    print(f"File: {RAW_FILE}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nFirst five rows:")
    print(df.head().to_string(index=False))

    print("\nMissing values:")
    print(df.isna().sum().to_string())

    if "Year" in df.columns:
        years = pd.to_numeric(df["Year"], errors="coerce")
        print(f"\nYear range: {years.min()} to {years.max()}")

    if "Crime Type" in df.columns:
        print("\nCrime types:")
        print(df["Crime Type"].value_counts(dropna=False).to_string())


if __name__ == "__main__":
    main()