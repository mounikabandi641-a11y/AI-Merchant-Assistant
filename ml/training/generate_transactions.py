from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "transactions.csv"


def generate_synthetic_transactions(n_rows: int = 1200) -> pd.DataFrame:
    """Create a fictional transaction dataset for ML training."""
    random.seed(42)

    merchants = [f"M{idx:04d}" for idx in range(1, 51)]
    payment_methods = ["card", "wallet", "bank_transfer", "cash"]
    device_types = ["desktop", "mobile", "tablet"]
    locations = [
        "New York",
        "Chicago",
        "Los Angeles",
        "Dallas",
        "Miami",
        "Seattle",
        "London",
        "Berlin",
        "Toronto",
        "Sydney",
    ]
    payment_statuses = ["completed", "pending", "failed", "refunded"]
    dispute_types = ["chargeback", "refund", "duplicate", "authorization", "billing", "none"]
    risk_levels = ["low", "medium", "high"]

    records: list[dict[str, object]] = []

    for index in range(1, n_rows + 1):
        risk_label = random.choices(risk_levels, weights=[0.65, 0.25, 0.10], k=1)[0]

        if risk_label == "low":
            amount = round(random.uniform(8.0, 500.0), 2)
            failed_attempts = random.randint(0, 2)
            transaction_frequency = random.randint(1, 18)
            customer_age_days = random.randint(30, 2500)
            previous_chargebacks = random.randint(0, 1)
            dispute_type = random.choices(dispute_types, weights=[0.05, 0.08, 0.05, 0.04, 0.03, 0.75], k=1)[0]
        elif risk_label == "medium":
            amount = round(random.uniform(120.0, 1800.0), 2)
            failed_attempts = random.randint(1, 4)
            transaction_frequency = random.randint(4, 30)
            customer_age_days = random.randint(60, 1800)
            previous_chargebacks = random.randint(0, 3)
            dispute_type = random.choices(dispute_types, weights=[0.18, 0.15, 0.12, 0.1, 0.08, 0.37], k=1)[0]
        else:
            amount = round(random.uniform(300.0, 6000.0), 2)
            failed_attempts = random.randint(2, 9)
            transaction_frequency = random.randint(5, 40)
            customer_age_days = random.randint(10, 2200)
            previous_chargebacks = random.randint(1, 6)
            dispute_type = random.choices(dispute_types, weights=[0.35, 0.15, 0.15, 0.2, 0.1, 0.05], k=1)[0]

        transaction_time = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 700), hours=random.randint(0, 23))
        payment_status = random.choices(
            payment_statuses,
            weights=[0.72, 0.12, 0.1, 0.06],
            k=1,
        )[0]

        record = {
            "transaction_id": f"txn_{index:06d}",
            "merchant_id": random.choice(merchants),
            "amount": amount,
            "transaction_time": transaction_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "payment_status": payment_status,
            "payment_method": random.choice(payment_methods),
            "device_type": random.choice(device_types),
            "location": random.choice(locations),
            "failed_attempts": failed_attempts,
            "transaction_frequency": transaction_frequency,
            "customer_age_days": customer_age_days,
            "previous_chargebacks": previous_chargebacks,
            "dispute_type": dispute_type,
            "fraud_risk_label": risk_label,
        }
        records.append(record)

    df = pd.DataFrame(records)
    return df


def ensure_transactions_dataset() -> Path:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_PATH.exists():
        df = generate_synthetic_transactions()
        df.to_csv(DATA_PATH, index=False)
        print(f"Created synthetic dataset at: {DATA_PATH}")
    else:
        print(f"Dataset already exists at: {DATA_PATH}")
    return DATA_PATH


if __name__ == "__main__":
    ensure_transactions_dataset()
