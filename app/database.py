"""SQLite database setup. The monthly counts table is seeded from the processed CSV on startup."""
import pandas as pd
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import DATABASE_URL, MONTHLY_FILE

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(force_reload: bool = False) -> int:
    """Create tables and load state_monthly_counts.csv. Returns number of rows in the table."""
    from app.models.monthly_count import MonthlyCount

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        existing = db.scalar(select(func.count()).select_from(MonthlyCount)) or 0
        if existing and not force_reload:
            return existing
        if not MONTHLY_FILE.exists():
            return existing  # nothing to load yet; run `python -m ml.prepare_data`
        if existing:
            db.query(MonthlyCount).delete()
        df = pd.read_csv(MONTHLY_FILE)
        rows = df[["state", "year", "month", "count"]].to_dict(orient="records")
        db.bulk_insert_mappings(MonthlyCount, rows)
        db.commit()
        return len(rows)
