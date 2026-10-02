package com.aiassistant.merchant.dto;

import jakarta.validation.constraints.*;
import java.time.LocalDateTime;

public record TransactionRequest(
    @NotBlank String transactionId,
    @NotBlank String merchantId,
    @Positive double amount,
    LocalDateTime transactionTime,
    @NotBlank String paymentStatus,
    @NotBlank String paymentMethod,
    @NotBlank String deviceType,
    @NotBlank String location,
    @PositiveOrZero int failedAttempts,
    @Min(1) int transactionFrequency,
    @PositiveOrZero int customerAgeDays,
    @PositiveOrZero int previousChargebacks,
    String disputeType,
    @NotBlank String fraudRiskLabel
) {}
