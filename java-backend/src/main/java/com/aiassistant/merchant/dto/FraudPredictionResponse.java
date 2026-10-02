package com.aiassistant.merchant.dto;

public record FraudPredictionResponse(double riskScore, String riskCategory, String message) {}
