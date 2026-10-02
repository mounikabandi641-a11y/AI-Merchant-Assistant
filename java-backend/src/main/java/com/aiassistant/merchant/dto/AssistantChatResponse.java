package com.aiassistant.merchant.dto;

import java.util.List;

public record AssistantChatResponse(String answer, String relatedTransactionId, List<String> sources) {}
