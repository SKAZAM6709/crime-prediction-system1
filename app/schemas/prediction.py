from typing import Optional

from pydantic import BaseModel


class ForecastPoint(BaseModel):
    period: str
    predicted: float
    lower: float
    upper: float


class HistoryPoint(BaseModel):
    period: str
    count: int


class ForecastResponse(BaseModel):
    state: str
    horizon: int
    history: list[HistoryPoint]
    forecast: list[ForecastPoint]


class ModelInfo(BaseModel):
    model_name: str
    trained_at: Optional[str] = None
    last_observed_period: Optional[str] = None
    test_months: Optional[int] = None
    metrics: dict
    baselines: dict
    features: list[str]
