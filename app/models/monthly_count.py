from sqlalchemy import Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MonthlyCount(Base):
    __tablename__ = "monthly_counts"
    __table_args__ = (Index("ix_state_period", "state", "year", "month"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    state: Mapped[str] = mapped_column(String(64), index=True)
    year: Mapped[int] = mapped_column(Integer, index=True)
    month: Mapped[int] = mapped_column(Integer)
    count: Mapped[int] = mapped_column(Integer)
