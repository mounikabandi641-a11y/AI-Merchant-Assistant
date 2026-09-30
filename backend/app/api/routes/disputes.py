from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.crud import create_dispute, get_all_disputes, get_dispute_by_dispute_id, update_dispute_status
from app.db.database import get_db
from app.schemas.dispute import (
    DisputeCreate,
    DisputeRead,
    DisputeResolutionRequest,
    DisputeResolutionResponse,
)
from app.services.dispute_service import resolve_dispute

router = APIRouter(prefix="/disputes", tags=["disputes"])
api_router = APIRouter(prefix="/api/disputes", tags=["disputes"])


@router.post("/", response_model=DisputeRead, status_code=status.HTTP_201_CREATED)
def create_new_dispute(
    dispute: DisputeCreate,
    db: Session = Depends(get_db),
) -> DisputeRead:
    try:
        db_dispute = create_dispute(db, dispute.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return db_dispute


@router.get("/", response_model=list[DisputeRead])
def list_disputes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[DisputeRead]:
    return get_all_disputes(db, skip=skip, limit=limit)


@router.get("/{dispute_id}", response_model=DisputeRead)
def get_dispute(
    dispute_id: str,
    db: Session = Depends(get_db),
) -> DisputeRead:
    dispute = get_dispute_by_dispute_id(db, dispute_id)
    if dispute is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispute with dispute_id '{dispute_id}' not found.",
        )
    return dispute


@router.patch("/{dispute_id}", response_model=DisputeRead)
def update_dispute(
    dispute_id: str,
    status: str,
    recommended_action: str | None = None,
    db: Session = Depends(get_db),
) -> DisputeRead:
    try:
        updated_dispute = update_dispute_status(db, dispute_id, status, recommended_action)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return updated_dispute


@api_router.get("", response_model=list[DisputeRead])
def list_api_disputes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[DisputeRead]:
    return get_all_disputes(db, skip=skip, limit=limit)


@api_router.get("/{dispute_id}", response_model=DisputeRead)
def get_api_dispute(
    dispute_id: str,
    db: Session = Depends(get_db),
) -> DisputeRead:
    dispute = get_dispute_by_dispute_id(db, dispute_id)
    if dispute is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispute with dispute_id '{dispute_id}' not found.",
        )
    return dispute


@api_router.post("/resolve", response_model=DisputeResolutionResponse, status_code=status.HTTP_200_OK)
def resolve_dispute_route(
    request: DisputeResolutionRequest,
    db: Session = Depends(get_db),
) -> DisputeResolutionResponse:
    try:
        result = resolve_dispute(db, request.transaction_id, request.dispute_type, request.description)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return DisputeResolutionResponse(**result)
