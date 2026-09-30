from datetime import datetime

from pydantic import BaseModel, Field


class TransactionBase(BaseModel):
    transaction_id: str = Field(..., min_length=1)
    merchant_id: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    transaction_time: datetime
    payment_status: str = Field(..., min_length=1)
    payment_method: str = Field(..., min_length=1)
    device_type: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    failed_attempts: int = Field(..., ge=0)
    transaction_frequency: int = Field(..., ge=1)
    customer_age_days: int = Field(..., ge=0)
    previous_chargebacks: int = Field(..., ge=0)
    dispute_type: str | None = None
    fraud_risk_label: str = Field(..., min_length=1)


class TransactionCreate(TransactionBase):
    pass


class TransactionRead(TransactionBase):
    id: int
