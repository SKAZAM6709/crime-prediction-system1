from typing import Optional

from pydantic import BaseModel


class DataRange(BaseModel):
    min_year: int
    max_year: int
    states: list[str]


class TrendPoint(BaseModel):
    period: str  # "YYYY-MM"
    year: int
    month: int
    count: int


class StateTotal(BaseModel):
    state: str
    total: int


class PeakMonth(BaseModel):
    period: str
    count: int


class Summary(BaseModel):
    total_incidents: int
    months_covered: int
    average_per_month: float
    peak_month: Optional[PeakMonth] = None
    latest_year: Optional[int] = None
    latest_year_total: Optional[int] = None
    year_over_year_change_pct: Optional[float] = None
