import pandas as pd

from ml.build_features import FEATURE_COLUMNS, MIN_HISTORY, build_features, feature_row
from ml.prepare_data import clean_incidents, month_to_number, monthly_counts


def test_month_to_number():
    assert month_to_number("January") == 1
    assert month_to_number("dec") == 12
    assert month_to_number(7) == 7
    assert pd.isna(month_to_number("nonsense"))
    assert pd.isna(month_to_number(13))


def _raw():
    return pd.DataFrame({
        "Record ID": [1, 2, 3, 4],
        "State": [" texas", "Texas", "Ohio", None],
        "Year": [2000, 2000, 2000, 2000],
        "Month": ["January", "March", "January", "May"],
    })


def test_clean_drops_missing_and_normalises_state():
    clean = clean_incidents(_raw())
    assert len(clean) == 3
    assert set(clean["state"]) == {"Texas", "Ohio"}


def test_monthly_counts_fills_gaps_with_zero():
    counts = monthly_counts(clean_incidents(_raw()))
    texas = counts[counts["state"] == "Texas"].set_index("month")["count"]
    assert texas[1] == 1 and texas[2] == 0 and texas[3] == 1
    # Both states cover the same complete grid
    assert counts.groupby("state").size().nunique() == 1


def test_feature_row_needs_history_and_uses_lags():
    assert feature_row([1] * (MIN_HISTORY - 1), 2001, 1, 0) is None
    history = list(range(1, 25))  # 1..24
    row = feature_row(history, 2002, 1, 3)
    assert row["lag_1"] == 24 and row["lag_12"] == 13
    assert set(FEATURE_COLUMNS) == set(row)


def test_build_features_targets_match_series():
    rows = []
    for i in range(30):
        rows.append({"state": "A", "year": 2000 + i // 12, "month": i % 12 + 1, "count": i})
    feats = build_features(pd.DataFrame(rows))
    first = feats.iloc[0]
    assert first["target"] == MIN_HISTORY and first["lag_1"] == MIN_HISTORY - 1
