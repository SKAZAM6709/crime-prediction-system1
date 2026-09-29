from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.monthly_count import MonthlyCount as M


def _filters(state: Optional[str], start_year: Optional[int], end_year: Optional[int]) -> list:
    conds = []
    if state and state.upper() != "ALL":
        conds.append(M.state == state)
    if start_year is not None:
        conds.append(M.year >= start_year)
    if end_year is not None:
        conds.append(M.year <= end_year)
    return conds


def get_range(db: Session) -> dict:
    lo, hi = db.execute(select(func.min(M.year), func.max(M.year))).one()
    states = db.scalars(select(M.state).distinct().order_by(M.state)).all()
    return {"min_year": lo or 0, "max_year": hi or 0, "states": list(states)}


def get_trend(db: Session, state=None, start_year=None, end_year=None) -> list[dict]:
    q = (
        select(M.year, M.month, func.sum(M.count))
        .where(*_filters(state, start_year, end_year))
        .group_by(M.year, M.month)
        .order_by(M.year, M.month)
    )
    return [
        {"period": f"{y}-{m:02d}", "year": y, "month": m, "count": int(c)}
        for y, m, c in db.execute(q).all()
    ]


def get_summary(db: Session, state=None, start_year=None, end_year=None) -> dict:
    trend = get_trend(db, state, start_year, end_year)
    if not trend:
        return {"total_incidents": 0, "months_covered": 0, "average_per_month": 0.0}
    total = sum(p["count"] for p in trend)
    peak = max(trend, key=lambda p: p["count"])

    yearly: dict[int, int] = {}
    for p in trend:
        yearly[p["year"]] = yearly.get(p["year"], 0) + p["count"]
    years = sorted(yearly)
    latest = years[-1]
    change = None
    if len(years) > 1 and yearly[years[-2]]:
        change = round((yearly[latest] - yearly[years[-2]]) / yearly[years[-2]] * 100, 1)
    return {
        "total_incidents": total,
        "months_covered": len(trend),
        "average_per_month": round(total / len(trend), 1),
        "peak_month": {"period": peak["period"], "count": peak["count"]},
        "latest_year": latest,
        "latest_year_total": yearly[latest],
        "year_over_year_change_pct": change,
    }


def get_state_totals(db: Session, start_year=None, end_year=None, limit: int = 15) -> list[dict]:
    q = (
        select(M.state, func.sum(M.count).label("total"))
        .where(*_filters(None, start_year, end_year))
        .group_by(M.state)
        .order_by(func.sum(M.count).desc())
        .limit(limit)
    )
    return [{"state": s, "total": int(t)} for s, t in db.execute(q).all()]
