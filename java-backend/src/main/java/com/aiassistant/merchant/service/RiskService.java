package com.aiassistant.merchant.service;

import com.aiassistant.merchant.dto.FraudPredictionRequest;
import com.aiassistant.merchant.dto.FraudPredictionResponse;
import org.springframework.stereotype.Service;

@Service
public class RiskService {
    public FraudPredictionResponse predict(FraudPredictionRequest input) {
        double amount = value(input.amount(), 0);
        double failed = value(input.failedAttempts(), 0);
        double frequency = value(input.transactionFrequency(), 1);
        double chargebacks = value(input.previousChargebacks(), 0);
        double score = Math.min(0.99, 0.05 + Math.min(amount / 2000.0, 0.35)
            + Math.min(failed * 0.08, 0.24) + Math.min(frequency / 100.0, 0.15)
            + Math.min(chargebacks * 0.12, 0.24));
        if ("flagged".equalsIgnoreCase(input.paymentStatus())) score = Math.min(0.99, score + 0.2);
        String category;
        String message;
        if (score < 0.33) { category = "LOW_RISK"; message = "Transaction appears low risk."; }
        else if (score < 0.66) { category = "MEDIUM_RISK"; message = "Transaction should be monitored closely."; }
        else { category = "HIGH_RISK"; message = "Transaction requires review."; }
        return new FraudPredictionResponse(round(score), category, message);
    }

    private double value(Number value, double fallback) { return value == null ? fallback : value.doubleValue(); }
    private double round(double value) { return Math.round(value * 10000.0) / 10000.0; }
}
