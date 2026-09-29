from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.analytics import DataRange, StateTotal, Summary, TrendPoint
from app.services import analytics_service as svc

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/range", response_model=DataRange)
def data_range(db: Session = Depends(get_db)):
    return svc.get_range(db)


@router.get("/summary", response_model=Summary)
def summary(
    state: Optional[str] = None,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    db: Session = Depends(get_db),
):
    return svc.get_summary(db, state, start_year, end_year)


@router.get("/trend", response_model=list[TrendPoint])
def trend(
    state: Optional[str] = None,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    db: Session = Depends(get_db),
):
    return svc.get_trend(db, state, start_year, end_year)


@router.get("/by-state", response_model=list[StateTotal])
def by_state(
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    limit: int = Query(15, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return svc.get_state_totals(db, start_year, end_year, limit)
