from fastapi import APIRouter, HTTPException

from app.services.prediction_service import (
    available_states,
    forecast_next_month,
)


router = APIRouter(prefix="/api", tags=["Predictions"])


@router.get("/states")
def get_states():
    try:
        return {"states": available_states()}
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@router.get("/forecast/{state}")
def get_forecast(state: str):
    try:
        return forecast_next_month(state)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error