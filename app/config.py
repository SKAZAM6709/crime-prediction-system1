"""Central configuration. Values can be overridden with environment variables or backend/.env."""
import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent

load_dotenv(BACKEND_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BACKEND_DIR / 'crime.db'}")
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()]

RAW_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
ARTIFACT_DIR = BACKEND_DIR / "ml" / "artifacts"

RAW_FILE = RAW_DIR / "US_Crime_DataSet.csv"
INCIDENTS_FILE = PROCESSED_DIR / "incidents_clean.csv"
MONTHLY_FILE = PROCESSED_DIR / "state_monthly_counts.csv"
MODEL_FILE = ARTIFACT_DIR / "model.joblib"
META_FILE = ARTIFACT_DIR / "meta.json"
