package com.aiassistant.merchant.dto;

import jakarta.validation.constraints.NotBlank;

public record DisputeResolutionRequest(
    @NotBlank String transactionId,
    @NotBlank String disputeType,
    @NotBlank String description
) {}
