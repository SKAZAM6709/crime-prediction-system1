from fastapi import APIRouter

from app.config import MODEL_FILE

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {"status": "ok", "model_ready": MODEL_FILE.exists()}
