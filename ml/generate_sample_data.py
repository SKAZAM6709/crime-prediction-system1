"""Create a SYNTHETIC stand-in for US_Crime_DataSet.csv so the project runs end to end.

Replace data/raw/US_Crime_DataSet.csv with the real file for real results.
Usage:  python -m ml.generate_sample_data
"""
import numpy as np
import pandas as pd

from app.config import RAW_FILE

STATES = {
    "California": 900, "Texas": 700, "Florida": 500, "New York": 480, "Michigan": 300,
    "Illinois": 320, "Georgia": 260, "Ohio": 230, "Pennsylvania": 260, "Louisiana": 200,
    "Arizona": 170, "Washington": 110,
}
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def main(seed: int = 42) -> None:
    rng = np.random.default_rng(seed)
    rows = []
    for state, base in STATES.items():
        scale = base / 12 / 20  # scale so file stays small
        for year in range(1995, 2015):
            trend = 1.0 - 0.012 * (year - 1995)
            for m, month in enumerate(MONTHS):
                season = 1.0 + 0.12 * np.sin((m - 3) / 12 * 2 * np.pi)
                n = rng.poisson(max(scale * trend * season * 12, 1))
                for _ in range(n):
                    rows.append((state, year, month))
    df = pd.DataFrame(rows, columns=["State", "Year", "Month"])
    df.insert(0, "Record ID", np.arange(1, len(df) + 1))
    df["City"] = df["State"] + " City"
    df["Incident"] = 1
    df["Crime Type"] = rng.choice(["Murder or Manslaughter", "Manslaughter by Negligence"], len(df), p=[0.97, 0.03])
    df["Crime Solved"] = rng.choice(["Yes", "No"], len(df), p=[0.65, 0.35])
    df["Victim Sex"] = rng.choice(["Male", "Female"], len(df), p=[0.77, 0.23])
    df["Victim Age"] = rng.integers(1, 90, len(df))
    df["Weapon"] = rng.choice(["Handgun", "Knife", "Blunt Object", "Firearm", "Rifle"], len(df))
    RAW_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_FILE, index=False)
    print(f"Wrote synthetic sample: {RAW_FILE} ({len(df):,} rows)")


if __name__ == "__main__":
    main()
