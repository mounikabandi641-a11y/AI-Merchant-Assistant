from train_model import predict_risk

sample_transaction = {
    "merchant_id": "M0001",
    "amount": 250.5,
    "payment_status": "completed",
    "payment_method": "card",
    "device_type": "mobile",
    "location": "New York",
    "failed_attempts": 1,
    "transaction_frequency": 10,
    "customer_age_days": 365,
    "previous_chargebacks": 0,
    "dispute_type": "none",
}

print(predict_risk(sample_transaction))
