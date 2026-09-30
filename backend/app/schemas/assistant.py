from pydantic import BaseModel, Field


class AssistantChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    transaction_id: str | None = Field(default=None, min_length=1, max_length=100)


class AssistantChatResponse(BaseModel):
    answer: str
    related_transaction_id: str | None = None
    sources: list[str] = Field(default_factory=list)
