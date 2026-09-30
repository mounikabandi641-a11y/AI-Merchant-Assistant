from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from generate_transactions import ensure_transactions_dataset

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "transactions.csv"
MODEL_DIR = ROOT / "model"
MODEL_FILE = MODEL_DIR / "random_forest_risk_model.joblib"

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
TARGET_COLUMN = "fraud_risk_label"


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    clean_df = df.copy()

    for column in NUMERIC_COLUMNS:
        if column in clean_df.columns:
            clean_df[column] = pd.to_numeric(clean_df[column], errors="coerce")
            clean_df[column] = clean_df[column].fillna(clean_df[column].median())

    for column in CATEGORICAL_COLUMNS:
        if column in clean_df.columns:
            clean_df[column] = clean_df[column].fillna("unknown")

    return clean_df


def build_model_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_COLUMNS,
            ),
            (
                "numeric",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                ]),
                NUMERIC_COLUMNS,
            ),
        ]
    )

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )


def train_and_evaluate_model() -> dict[str, object]:
    ensure_transactions_dataset()
    df = pd.read_csv(DATA_FILE)
    df = handle_missing_values(df)

    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Missing target column: {TARGET_COLUMN}")

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    pipeline = build_model_pipeline()
    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions, average="weighted", zero_division=0)
    recall = recall_score(y_test, predictions, average="weighted", zero_division=0)
    f1 = f1_score(y_test, predictions, average="weighted", zero_division=0)
    cm = confusion_matrix(y_test, predictions, labels=pipeline.named_steps["model"].classes_)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_FILE)

    report = {
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1_score": round(float(f1), 4),
        "confusion_matrix": cm.tolist(),
        "model_path": str(MODEL_FILE),
        "class_labels": list(pipeline.named_steps["model"].classes_),
    }

    print(json.dumps(report, indent=2))
    return report


def predict_risk(transaction: dict[str, object]) -> dict[str, float | str]:
    if not MODEL_FILE.exists():
        raise FileNotFoundError(f"Model not found at {MODEL_FILE}. Train the model first.")

    pipeline = joblib.load(MODEL_FILE)
    input_row: dict[str, object] = {}

    for column in FEATURE_COLUMNS:
        raw_value = transaction.get(column)
        if raw_value is None:
            if column in NUMERIC_COLUMNS:
                input_row[column] = 0
            else:
                input_row[column] = "unknown"
        else:
            input_row[column] = raw_value

    df = pd.DataFrame([input_row])
    probabilities = pipeline.predict_proba(df)[0]
    predicted_index = int(probabilities.argmax())
    risk_indicator = pipeline.named_steps["model"].classes_[predicted_index]
    risk_score = float(probabilities[predicted_index])

    return {
        "risk_indicator": str(risk_indicator),
        "risk_score": round(risk_score, 4),
        "risk_category": str(risk_indicator),
    }


if __name__ == "__main__":
    train_and_evaluate_model()
