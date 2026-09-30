from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.db.crud import create_dispute, get_transaction_by_transaction_id

VALID_DISPUTE_CATEGORIES = {
    "PAYMENT_FAILED_DEBITED",
    "DUPLICATE_TRANSACTION",
    "PAYMENT_NOT_RECEIVED",
    "REFUND_ISSUE",
    "UNKNOWN_TRANSACTION",
    "OTHER",
}


def normalize_dispute_type(dispute_type: str | None) -> str:
    if dispute_type is None:
        return "OTHER"

    normalized = dispute_type.strip().upper().replace("-", "_").replace(" ", "_")
    if normalized in VALID_DISPUTE_CATEGORIES:
        return normalized

    aliases = {
        "PAYMENT_FAILED": "PAYMENT_FAILED_DEBITED",
        "FAILED_DEBITED": "PAYMENT_FAILED_DEBITED",
        "FAILED_PAYMENT": "PAYMENT_FAILED_DEBITED",
        "DUPLICATE": "DUPLICATE_TRANSACTION",
        "DOUBLE_CHARGE": "DUPLICATE_TRANSACTION",
        "NOT_RECEIVED": "PAYMENT_NOT_RECEIVED",
        "MISSING_PAYMENT": "PAYMENT_NOT_RECEIVED",
        "REFUND": "REFUND_ISSUE",
        "CHARGEBACK": "REFUND_ISSUE",
        "UNKNOWN": "UNKNOWN_TRANSACTION",
    }
    return aliases.get(normalized, "OTHER")


def _transaction_summary(transaction: Any) -> dict[str, Any] | None:
    if transaction is None:
        return None

    return {
        "transaction_id": transaction.transaction_id,
        "merchant_id": transaction.merchant_id,
        "amount": transaction.amount,
        "payment_status": transaction.payment_status,
        "payment_method": transaction.payment_method,
        "device_type": transaction.device_type,
        "location": transaction.location,
        "failed_attempts": transaction.failed_attempts,
        "transaction_frequency": transaction.transaction_frequency,
        "customer_age_days": transaction.customer_age_days,
        "previous_chargebacks": transaction.previous_chargebacks,
        "fraud_risk_label": transaction.fraud_risk_label,
    }


def _build_explanation(category: str, transaction: Any, description: str) -> str:
    text = (description or "Customer reported a payment issue.").strip()
    if transaction is None:
        return (
            "No matching transaction record was found in the application for this dispute reference. "
            "The case needs merchant verification before any support action is taken."
        )

    payment_status = str(transaction.payment_status).lower()
    if category == "PAYMENT_FAILED_DEBITED":
        return (
            "The customer reports a debit even though the payment status is "
            f"{payment_status}. This should be reviewed against settlement and processing logs before any refund decision."
        )
    if category == "DUPLICATE_TRANSACTION":
        return (
            "The dispute indicates a possible duplicate payment or repeated charge. "
            f"Current transaction details show {transaction.failed_attempts} failed attempts and "
            f"{transaction.previous_chargebacks} prior chargeback references for review."
        )
    if category == "PAYMENT_NOT_RECEIVED":
        return (
            "The customer indicates the payment was not received or not confirmed. "
            f"The current transaction status is {payment_status}, which requires merchant verification."
        )
    if category == "REFUND_ISSUE":
        return (
            "This dispute references a refund problem. Review the original payment status and prior settlement history "
            "before approving or denying any refund workflow."
        )
    if category == "UNKNOWN_TRANSACTION":
        return (
            "The dispute cannot be mapped to a clearly identifiable transaction within the application. "
            "Merchant review is required before any final action."
        )
    return (
        f"The dispute description is '{text}'. The case does not clearly match a standard category and should be reviewed manually."
    )


def _build_recommended_action(category: str, transaction: Any) -> str:
    if transaction is None:
        return "Verify the transaction reference, payment logs, and merchant account details before any refund or support action."

    if category == "PAYMENT_FAILED_DEBITED":
        return "Verify the final settlement status and confirm whether the debit was a successful authorization or a failed payment, then follow the approved support/refund workflow."
    if category == "DUPLICATE_TRANSACTION":
        return "Review duplicate transaction records, payment gateway logs, and customer confirmation before any refund or reversal decision."
    if category == "PAYMENT_NOT_RECEIVED":
        return "Check the payment processor, bank transfer status, and merchant reconciliation records before taking further action."
    if category == "REFUND_ISSUE":
        return "Confirm the original transaction history and refund policy, then route the case to the manual support workflow for approval." 
    if category == "UNKNOWN_TRANSACTION":
        return "Request more payment details from the customer, then verify the transaction reference against merchant or processor records."
    return "Review the case manually with the merchant support team and follow the approved dispute workflow before any irreversible action."


def resolve_dispute(db: Session, transaction_id: str, dispute_type: str, description: str) -> dict[str, Any]:
    category = normalize_dispute_type(dispute_type)
    transaction = get_transaction_by_transaction_id(db, transaction_id)
    transaction_summary = _transaction_summary(transaction)
    explanation = _build_explanation(category, transaction, description)
    recommended_action = _build_recommended_action(category, transaction)
    status = "OPEN"

    dispute_id = f"DISP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{transaction_id or 'UNKNOWN'}"
    create_dispute(
        db,
        {
            "dispute_id": dispute_id,
            "transaction_id": transaction_id,
            "dispute_type": category,
            "description": description or "No description provided.",
            "status": status,
            "recommended_action": recommended_action,
            "created_at": datetime.utcnow(),
        },
    )

    return {
        "dispute_id": dispute_id,
        "dispute_category": category,
        "transaction_details": transaction_summary,
        "explanation": explanation,
        "recommended_action": recommended_action,
        "status": status,
    }
