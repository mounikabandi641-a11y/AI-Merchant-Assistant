package com.aiassistant.merchant.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record AssistantChatRequest(@NotBlank @Size(max = 1000) String message, String transactionId) {}
