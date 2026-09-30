from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.db.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True, nullable=False)
    merchant_id = Column(String, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    payment_status = Column(String, nullable=False, default="pending")
    payment_method = Column(String, nullable=False, default="card")
    device_type = Column(String, nullable=False, default="desktop")
    location = Column(String, nullable=False, default="unknown")
    failed_attempts = Column(Integer, nullable=False, default=0)
    transaction_frequency = Column(Integer, nullable=False, default=1)
    customer_age_days = Column(Integer, nullable=False, default=0)
    previous_chargebacks = Column(Integer, nullable=False, default=0)
    dispute_type = Column(String, nullable=True)
    fraud_risk_label = Column(String, nullable=False, default="low")
