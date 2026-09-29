"""Metrics and baselines. Imported by train.py; can also be run to re-score a saved model.
Usage:  python -m ml.evaluate
"""
import json

import joblib
import numpy as np
import pandas as pd

from app.config import META_FILE, MODEL_FILE, MONTHLY_FILE
from ml.build_features import FEATURE_COLUMNS, build_features


def regression_metrics(y_true, y_pred) -> dict:
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    err = y_pred - y_true
    ss_res, ss_tot = float((err ** 2).sum()), float(((y_true - y_true.mean()) ** 2).sum())
    return {
        "mae": round(float(np.abs(err).mean()), 3),
        "rmse": round(float(np.sqrt((err ** 2).mean())), 3),
        "r2": round(1 - ss_res / ss_tot, 4) if ss_tot else None,
    }


def evaluate_frame(test: pd.DataFrame, predictions) -> dict:
    """Score the model against two naive baselines on the same rows."""
    return {
        "model": regression_metrics(test["target"], predictions),
        "baseline_last_month": regression_metrics(test["target"], test["lag_1"]),
        "baseline_same_month_last_year": regression_metrics(test["target"], test["lag_12"]),
    }


def per_state_rmse(test: pd.DataFrame, predictions) -> dict:
    d = test.assign(err=(np.asarray(predictions) - test["target"].to_numpy()) ** 2)
    return {s: round(float(np.sqrt(g["err"].mean())), 3) for s, g in d.groupby("state")}


def main() -> None:
    meta = json.loads(META_FILE.read_text())
    model = joblib.load(MODEL_FILE)
    feats = build_features(pd.read_csv(MONTHLY_FILE), meta["state_codes"])
    feats["period"] = feats["year"] * 12 + feats["month"]
    test = feats[feats["period"] > feats["period"].max() - meta["test_months"]]
    preds = np.clip(model.predict(test[FEATURE_COLUMNS].to_numpy()), 0, None)
    print(json.dumps(evaluate_frame(test, preds), indent=2))
    print("(Note: the saved model was refit on all data, so these scores are optimistic. "
          "See meta.json for held-out scores.)")


if __name__ == "__main__":
    main()
