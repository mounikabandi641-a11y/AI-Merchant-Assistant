from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.assistant import AssistantChatRequest, AssistantChatResponse
from app.services.assistant_service import answer_question

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


@router.post("/chat", response_model=AssistantChatResponse)
def assistant_chat(
    payload: AssistantChatRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> AssistantChatResponse:
    model = getattr(request.app.state, "risk_model", None)
    result = answer_question(
        db,
        payload.message,
        model=model,
        context_transaction_id=payload.transaction_id,
    )
    return AssistantChatResponse(**result)
