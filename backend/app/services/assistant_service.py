from __future__ import annotations

import re
from typing import Any

from sqlalchemy.orm import Session

from app.db.crud import get_all_disputes, get_transaction_by_transaction_id
from app.services.dispute_service import VALID_DISPUTE_CATEGORIES, normalize_dispute_type
from app.services.ml_service import predict_risk

INSUFFICIENT_INFORMATION = "I don't have enough information in the application to answer that."

DISPUTE_GUIDANCE = {
    "PAYMENT_FAILED_DEBITED": (
        "A failed status in the application does not confirm whether a debit settled. "
        "Compare processor and settlement logs with the transaction record, then follow the approved manual support workflow."
    ),
    "DUPLICATE_TRANSACTION": (
        "Compare the transaction records and payment gateway logs, then verify the customer's report. "
        "Any refund or reversal decision must follow merchant review and the approved workflow."
    ),
    "PAYMENT_NOT_RECEIVED": (
        "Check processor status, transfer confirmation, and merchant reconciliation records, then verify the transaction reference."
    ),
    "REFUND_ISSUE": (
        "Review the original transaction history and refund policy, then route the case through the manual approval workflow."
    ),
    "UNKNOWN_TRANSACTION": (
        "Request the transaction reference and verify it against the merchant or processor records before taking further action."
    ),
    "OTHER": (
        "Review the case details with merchant support and follow the approved dispute workflow before any final action."
    ),
}

TRANSACTION_ID_PATTERN = re.compile(
    r"\b(?:transaction|txn)(?:\s+(?:id|number))?\s*(?:is|=|:|#)?\s*"
    r"(?P<context_id>[A-Za-z][A-Za-z0-9_-]*\d[A-Za-z0-9_-]*)\b"
    r"|\b(?P<bare_id>TX\d+|txn_\d+)\b",
    re.IGNORECASE,
)


def _find_transaction_id(message: str, context_transaction_id: str | None) -> str | None:
    if context_transaction_id and context_transaction_id.strip():
        return context_transaction_id.strip()
    match = TRANSACTION_ID_PATTERN.search(message)
    return (match.group("context_id") or match.group("bare_id")) if match else None


def _is_risk_question(message: str) -> bool:
    text = message.lower()
    return any(term in text for term in ("risk", "risky", "fraud", "indicator", "indicators"))


def _is_contextual_transaction_question(message: str) -> bool:
    text = message.lower()
    if any(term in text for term in ("dispute", "duplicat", "refund", "payment failed", "debited", "not received")):
        return False
    if _is_risk_question(text):
        return True
    return any(
        term in text
        for term in (
            "transaction",
            "details",
            "amount",
            "payment status",
            "payment method",
            "device",
            "location",
            "failed attempts",
            "frequency",
            "chargebacks",
        )
    )


def _transaction_payload(transaction: Any) -> dict[str, Any]:
    return {
        "amount": transaction.amount,
        "payment_method": transaction.payment_method,
        "device_type": transaction.device_type,
        "failed_attempts": transaction.failed_attempts,
        "transaction_frequency": transaction.transaction_frequency,
        "customer_age_days": transaction.customer_age_days,
        "previous_chargebacks": transaction.previous_chargebacks,
        "merchant_id": transaction.merchant_id,
        "payment_status": transaction.payment_status,
        "location": transaction.location,
        "dispute_type": transaction.dispute_type,
    }


def _transaction_details(transaction: Any) -> str:
    return (
        f"Transaction {transaction.transaction_id}: amount {transaction.amount:.2f}; "
        f"status {transaction.payment_status}; payment method {transaction.payment_method}; "
        f"device {transaction.device_type}; location {transaction.location}; "
        f"failed attempts {transaction.failed_attempts}; transaction frequency "
        f"{transaction.transaction_frequency}; previous chargebacks {transaction.previous_chargebacks}; "
        f"recorded risk label {transaction.fraud_risk_label}."
    )


def _risk_explanation(transaction: Any, model: Any) -> str:
    prediction = predict_risk(_transaction_payload(transaction), model=model)
    indicators = (
        f"The stored record shows payment status {transaction.payment_status}, "
        f"{transaction.failed_attempts} failed attempts, transaction frequency "
        f"{transaction.transaction_frequency}, and {transaction.previous_chargebacks} previous chargebacks."
    )
    return (
        f"The current model prediction is {prediction['risk_category']}: {prediction['message']} "
        f"{indicators} These are available review indicators, but the prediction API does not explain "
        "how much each field contributed. A risk result is not proof of fraud; verify the transaction records before deciding what to do."
    )


def _dispute_category(message: str) -> str | None:
    text = message.lower()
    if "duplicat" in text or "double charge" in text or "charged twice" in text:
        return "DUPLICATE_TRANSACTION"
    if "refund" in text:
        return "REFUND_ISSUE"
    if "not received" in text or "missing payment" in text:
        return "PAYMENT_NOT_RECEIVED"
    if "unknown transaction" in text or "unrecognized transaction" in text:
        return "UNKNOWN_TRANSACTION"
    if "payment failed" in text or "failed but debit" in text or "failed and debit" in text:
        return "PAYMENT_FAILED_DEBITED"
    return None


def _stored_recommended_action(db: Session, category: str) -> str | None:
    disputes = get_all_disputes(db, skip=0, limit=500)
    for dispute in reversed(disputes):
        if normalize_dispute_type(dispute.dispute_type) == category and dispute.recommended_action:
            return dispute.recommended_action
    return None


def answer_question(
    db: Session,
    message: str,
    model: Any = None,
    context_transaction_id: str | None = None,
) -> dict[str, Any]:
    text = message.strip()
    transaction_id = _find_transaction_id(text, None)
    if transaction_id is None and context_transaction_id and _is_contextual_transaction_question(text):
        transaction_id = context_transaction_id.strip()

    if transaction_id:
        transaction = get_transaction_by_transaction_id(db, transaction_id)
        if transaction is None:
            return {
                "answer": INSUFFICIENT_INFORMATION,
                "related_transaction_id": None,
                "sources": [],
            }
        if _is_risk_question(text):
            if model is None:
                return {
                    "answer": INSUFFICIENT_INFORMATION,
                    "related_transaction_id": None,
                    "sources": [],
                }
            try:
                answer = _risk_explanation(transaction, model)
            except Exception:
                return {
                    "answer": INSUFFICIENT_INFORMATION,
                    "related_transaction_id": None,
                    "sources": [],
                }
            return {
                "answer": answer,
                "related_transaction_id": transaction.transaction_id,
                "sources": ["transaction data", "risk analysis"],
            }
        return {
            "answer": _transaction_details(transaction),
            "related_transaction_id": transaction.transaction_id,
            "sources": ["transaction data"],
        }

    lower_message = text.lower()
    if "before resolving" in lower_message or "before resolve" in lower_message or (
        "before" in lower_message and "dispute" in lower_message
    ):
        return {
            "answer": (
                "Before resolving a dispute, verify the transaction reference and original payment status, "
                "check processor, settlement, and reconciliation records, review the applicable dispute category "
                "and merchant policy, and document the evidence. A merchant must make the final decision; "
                "this assistant does not approve disputes or initiate refunds."
            ),
            "related_transaction_id": None,
            "sources": ["dispute categories", "recommended actions"],
        }

    category = _dispute_category(text)
    if category in VALID_DISPUTE_CATEGORIES:
        action = _stored_recommended_action(db, category)
        if action:
            explanation = DISPUTE_GUIDANCE[category]
            if category == "PAYMENT_FAILED_DEBITED":
                answer = f"{explanation} Recommended next step: {action} Merchant review is required; this is guidance, not a final decision."
            else:
                answer = f"For {category.replace('_', ' ').lower()}: {action} Merchant review is required; this is guidance, not a final decision."
            sources = ["dispute categories", "recommended actions"]
        else:
            answer = f"For {category.replace('_', ' ').lower()}: {DISPUTE_GUIDANCE[category]} Merchant review is required; this is guidance, not a final decision."
            sources = ["dispute categories", "dispute guidance"]
        return {"answer": answer, "related_transaction_id": None, "sources": sources}

    return {
        "answer": INSUFFICIENT_INFORMATION,
        "related_transaction_id": None,
        "sources": [],
    }
