from __future__ import annotations

from pydantic import BaseModel, Field


class FraudPredictionRequest(BaseModel):
    amount: float | None = Field(default=None, description="Transaction amount in base currency")
    payment_method: str | None = Field(default=None, description="Payment method, such as card or UPI")
    device_type: str | None = Field(default=None, description="Device type, such as mobile or desktop")
    failed_attempts: int | None = Field(default=None, description="Number of failed payment attempts")
    transaction_frequency: int | None = Field(default=None, description="Recent transaction frequency")
    customer_age_days: int | None = Field(default=None, description="Customer age in days")
    previous_chargebacks: int | None = Field(default=None, description="Historical chargebacks on the customer")
    merchant_id: str | None = Field(default=None, description="Merchant identifier")
    payment_status: str | None = Field(default=None, description="Payment status")
    location: str | None = Field(default=None, description="Location of the transaction")
    dispute_type: str | None = Field(default=None, description="Known dispute type, if any")


class FraudPredictionResponse(BaseModel):
    risk_score: float
    risk_category: str
    message: str
