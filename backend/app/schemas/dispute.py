from datetime import datetime

from pydantic import BaseModel, Field


class DisputeBase(BaseModel):
    dispute_id: str = Field(..., min_length=1)
    transaction_id: str = Field(..., min_length=1)
    dispute_type: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    status: str = "open"
    recommended_action: str = "manual_review"
    created_at: datetime | None = None


class DisputeCreate(DisputeBase):
    pass


class DisputeRead(DisputeBase):
    id: int


class DisputeResolutionRequest(BaseModel):
    transaction_id: str = Field(..., min_length=1)
    dispute_type: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)


class DisputeResolutionResponse(BaseModel):
    dispute_id: str
    dispute_category: str
    transaction_details: dict | None = None
    explanation: str
    recommended_action: str
    status: str
