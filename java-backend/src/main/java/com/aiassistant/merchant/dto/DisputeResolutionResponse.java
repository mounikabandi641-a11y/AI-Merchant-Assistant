package com.aiassistant.merchant.dto;

import java.util.Map;

public record DisputeResolutionResponse(
    String disputeId, String disputeCategory, Map<String, Object> transactionDetails,
    String explanation, String recommendedAction, String status
) {}
