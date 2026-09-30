from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parents[3] / "model" / "random_forest_risk_model.joblib"

CATEGORICAL_COLUMNS = [
    "merchant_id",
    "payment_status",
    "payment_method",
    "device_type",
    "location",
    "dispute_type",
]
NUMERIC_COLUMNS = [
    "amount",
    "failed_attempts",
    "transaction_frequency",
    "customer_age_days",
    "previous_chargebacks",
]
FEATURE_COLUMNS = CATEGORICAL_COLUMNS + NUMERIC_COLUMNS

RISK_CATEGORY_MAP = {
    "low": "LOW_RISK",
    "medium": "MEDIUM_RISK",
    "high": "HIGH_RISK",
}


def load_model() -> Any:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Saved model not found at: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


def _normalize_field_value(column: str, value: Any) -> Any:
    if value is None or value == "":
        if column in NUMERIC_COLUMNS:
            return float("nan")
        return "unknown"

    if column in NUMERIC_COLUMNS:
        try:
            return float(value)
        except (TypeError, ValueError):
            return float("nan")

    text = str(value).strip()
    if column in {"payment_status", "payment_method", "device_type", "dispute_type"}:
        return text.lower()
    return text


def prepare_prediction_dataframe(transaction: dict[str, Any]) -> pd.DataFrame:
    normalized: dict[str, Any] = {}
    for column in FEATURE_COLUMNS:
        normalized[column] = _normalize_field_value(column, transaction.get(column))

    for column in [
        "merchant_id",
        "payment_status",
        "payment_method",
        "device_type",
        "location",
        "dispute_type",
    ]:
        if normalized.get(column) in (None, ""):
            normalized[column] = "unknown"

    dataframe = pd.DataFrame([normalized], columns=FEATURE_COLUMNS)
    return dataframe


def predict_risk(transaction: dict[str, Any], model: Any | None = None) -> dict[str, Any]:
    pipeline = model if model is not None else load_model()
    input_df = prepare_prediction_dataframe(transaction)
    probabilities = pipeline.predict_proba(input_df)[0]
    predicted_index = int(probabilities.argmax())
    predicted_label = str(pipeline.named_steps["model"].classes_[predicted_index]).lower()
    risk_score = float(probabilities[predicted_index])
    risk_category = RISK_CATEGORY_MAP.get(predicted_label, predicted_label.upper() + "_RISK")

    message = "Transaction appears low risk." if predicted_label == "low" else "Transaction requires review."
    if predicted_label == "medium":
        message = "Transaction should be monitored closely."

    return {
        "risk_score": round(risk_score, 4),
        "risk_category": risk_category,
        "message": message,
    }
