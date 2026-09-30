from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.db.database import Base


class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(Integer, primary_key=True, index=True)
    dispute_id = Column(String, unique=True, index=True, nullable=False)
    transaction_id = Column(String, index=True, nullable=False)
    dispute_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="open")
    recommended_action = Column(String, nullable=False, default="manual_review")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
