from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.crud import create_transaction, get_all_transactions, get_transaction_by_transaction_id
from app.db.database import get_db
from app.schemas.transaction import TransactionCreate, TransactionRead

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_new_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
) -> TransactionRead:
    try:
        db_transaction = create_transaction(db, transaction.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return db_transaction


@router.get("/", response_model=list[TransactionRead])
def list_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[TransactionRead]:
    return get_all_transactions(db, skip=skip, limit=limit)


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
) -> TransactionRead:
    transaction = get_transaction_by_transaction_id(db, transaction_id)
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with transaction_id '{transaction_id}' not found.",
        )
    return transaction
