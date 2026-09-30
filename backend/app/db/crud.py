from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dispute import Dispute
from app.models.transaction import Transaction


def _validate_required_fields(data: dict[str, Any], required_fields: list[str]) -> None:
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")


def create_transaction(db: Session, transaction_data: dict[str, Any]) -> Transaction:
    _validate_required_fields(
        transaction_data,
        [
            "transaction_id",
            "merchant_id",
            "amount",
            "payment_status",
            "payment_method",
            "device_type",
            "location",
            "fraud_risk_label",
        ],
    )

    existing = db.scalar(
        select(Transaction).where(Transaction.transaction_id == transaction_data["transaction_id"])
    )
    if existing:
        raise ValueError(f"Transaction with transaction_id '{transaction_data['transaction_id']}' already exists.")

    transaction = Transaction(**transaction_data)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def get_all_transactions(db: Session, skip: int = 0, limit: int = 100) -> list[Transaction]:
    return db.scalars(select(Transaction).offset(skip).limit(limit)).all()


def get_transaction_by_transaction_id(db: Session, transaction_id: str) -> Transaction | None:
    if not transaction_id:
        raise ValueError("transaction_id is required.")
    return db.scalar(select(Transaction).where(Transaction.transaction_id == transaction_id))


def create_dispute(db: Session, dispute_data: dict[str, Any]) -> Dispute:
    _validate_required_fields(
        dispute_data,
        ["dispute_id", "transaction_id", "dispute_type", "description"],
    )

    existing = db.scalar(select(Dispute).where(Dispute.dispute_id == dispute_data["dispute_id"]))
    if existing:
        raise ValueError(f"Dispute with dispute_id '{dispute_data['dispute_id']}' already exists.")

    dispute = Dispute(**dispute_data)
    db.add(dispute)
    db.commit()
    db.refresh(dispute)
    return dispute


def get_all_disputes(db: Session, skip: int = 0, limit: int = 100) -> list[Dispute]:
    return db.scalars(select(Dispute).offset(skip).limit(limit)).all()


def get_dispute_by_dispute_id(db: Session, dispute_id: str) -> Dispute | None:
    if not dispute_id:
        raise ValueError("dispute_id is required.")
    return db.scalar(select(Dispute).where(Dispute.dispute_id == dispute_id))


def update_dispute_status(
    db: Session,
    dispute_id: str,
    status: str,
    recommended_action: str | None = None,
) -> Dispute:
    if not dispute_id:
        raise ValueError("dispute_id is required.")
    if not status:
        raise ValueError("status is required.")

    dispute = get_dispute_by_dispute_id(db, dispute_id)
    if dispute is None:
        raise ValueError(f"Dispute with dispute_id '{dispute_id}' was not found.")

    dispute.status = status
    if recommended_action is not None:
        dispute.recommended_action = recommended_action

    db.commit()
    db.refresh(dispute)
    return dispute
