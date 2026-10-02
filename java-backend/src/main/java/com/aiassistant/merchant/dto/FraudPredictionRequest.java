package com.aiassistant.merchant.dto;

public record FraudPredictionRequest(
    Double amount, String paymentMethod, String deviceType, Integer failedAttempts,
    Integer transactionFrequency, Integer customerAgeDays, Integer previousChargebacks,
    String merchantId, String paymentStatus, String location, String disputeType
) {}
