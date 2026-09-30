class FraudDetectionService:
    """Placeholder service for fraud classification logic."""

    def score_transaction(self, transaction_data: dict) -> dict:
        amount = float(transaction_data.get("amount", 0))
        risk_score = 0.0

        if amount > 2000:
            risk_score += 0.4

        if transaction_data.get("status") == "flagged":
            risk_score += 0.5

        status = "high_risk" if risk_score >= 0.7 else "low_risk"
        return {"risk_score": round(risk_score, 2), "status": status}
