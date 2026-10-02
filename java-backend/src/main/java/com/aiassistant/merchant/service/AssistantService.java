package com.aiassistant.merchant.service;

import com.aiassistant.merchant.dto.AssistantChatResponse;
import com.aiassistant.merchant.dto.FraudPredictionRequest;
import com.aiassistant.merchant.model.Dispute;
import com.aiassistant.merchant.model.Transaction;
import com.aiassistant.merchant.repository.DisputeRepository;
import com.aiassistant.merchant.repository.TransactionRepository;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.springframework.stereotype.Service;

@Service
public class AssistantService {
    public static final String FALLBACK = "I don't have enough information in the application to answer that.";
    private static final Pattern TRANSACTION_ID = Pattern.compile("\\b(?:transaction|txn)(?:\\s+(?:id|number))?\\s*(?:is|=|:|#)?\\s*([A-Za-z][A-Za-z0-9_-]*\\d[A-Za-z0-9_-]*)\\b|\\b(TX\\d+|txn_\\d+)\\b", Pattern.CASE_INSENSITIVE);
    private final TransactionRepository transactions; private final DisputeRepository disputes; private final RiskService risk; private final DisputeService disputeService;
    public AssistantService(TransactionRepository transactions, DisputeRepository disputes, RiskService risk, DisputeService disputeService) { this.transactions = transactions; this.disputes = disputes; this.risk = risk; this.disputeService = disputeService; }

    public AssistantChatResponse answer(String message, String contextId) {
        String text = message.trim(); String id = contextId;
        Matcher matcher = TRANSACTION_ID.matcher(text);
        boolean hasExplicitTransactionId = matcher.find();
        if (hasExplicitTransactionId) id = matcher.group(1) != null ? matcher.group(1) : matcher.group(2);
        if (id != null && !id.isBlank() && (hasExplicitTransactionId || isRisk(text) || isContextQuestion(text))) {
            Transaction t = transactions.findByTransactionId(id).orElse(null); if (t == null) return new AssistantChatResponse(FALLBACK, null, List.of());
            if (isRisk(text)) { var prediction = risk.predict(new FraudPredictionRequest(t.amount, t.paymentMethod, t.deviceType, t.failedAttempts, t.transactionFrequency, t.customerAgeDays, t.previousChargebacks, t.merchantId, t.paymentStatus, t.location, t.disputeType));
                return new AssistantChatResponse("The current model prediction is " + prediction.riskCategory() + ": " + prediction.message() + " The stored record shows payment status " + t.paymentStatus + ", " + t.failedAttempts + " failed attempts, transaction frequency " + t.transactionFrequency + ", and " + t.previousChargebacks + " previous chargebacks. These are available review indicators; verify the transaction records before deciding what to do.", t.transactionId, List.of("transaction data", "risk analysis")); }
            return new AssistantChatResponse(details(t), t.transactionId, List.of("transaction data"));
        }
        String lower = text.toLowerCase();
        if (lower.contains("before resolving") || lower.contains("before resolve") || (lower.contains("before") && lower.contains("dispute"))) return new AssistantChatResponse("Before resolving a dispute, verify the transaction reference and original payment status, check processor, settlement, and reconciliation records, review the applicable dispute category and merchant policy, and document the evidence. A merchant must make the final decision; this assistant does not approve disputes or initiate refunds.", null, List.of("dispute categories", "recommended actions"));
        if (lower.contains("dispute type") || lower.contains("dispute categor")) {
            String availableTypes = disputeService.categories().stream().sorted().map(type -> type.replace('_', ' ')).reduce((first, next) -> first + ", " + next).orElse("");
            return new AssistantChatResponse("The application supports these dispute types: " + availableTypes + ".", null, List.of("dispute categories"));
        }
        String category = category(lower); if (category != null) { String storedAction = disputes.findAll().stream().filter(d -> disputeService.normalize(d.disputeType).equals(category) && d.recommendedAction != null).reduce((a,b) -> b).map(d -> d.recommendedAction).orElse(null); String action = storedAction != null ? storedAction : disputeService.recommendedAction(category, id); String answer = "For " + category.replace('_', ' ').toLowerCase() + ": " + action + " Merchant review is required; this is guidance, not a final decision."; return new AssistantChatResponse(answer, null, List.of("dispute categories", storedAction == null ? "recommended actions" : "stored recommended actions")); }
        return new AssistantChatResponse(FALLBACK, null, List.of());
    }
    private boolean isRisk(String text) { String s = text.toLowerCase(); return s.contains("risk") || s.contains("risky") || s.contains("fraud") || s.contains("indicator"); }
    private boolean isContextQuestion(String text) { String s = text.toLowerCase(); return s.contains("transaction") || s.contains("details") || s.contains("amount") || s.contains("payment status") || s.contains("device") || s.contains("location"); }
    private String details(Transaction t) { return String.format("Transaction %s: amount %.2f; status %s; payment method %s; device %s; location %s; failed attempts %d; transaction frequency %d; previous chargebacks %d; recorded risk label %s.", t.transactionId, t.amount, t.paymentStatus, t.paymentMethod, t.deviceType, t.location, t.failedAttempts, t.transactionFrequency, t.previousChargebacks, t.fraudRiskLabel); }
    private String category(String s) { if (s.contains("duplicat") || s.contains("double charge")) return "DUPLICATE_TRANSACTION"; if (s.contains("refund")) return "REFUND_ISSUE"; if (s.contains("not received") || s.contains("missing payment")) return "PAYMENT_NOT_RECEIVED"; if (s.contains("unknown transaction") || s.contains("unrecognized transaction")) return "UNKNOWN_TRANSACTION"; if (s.contains("payment failed") || s.contains("failed but debit") || s.contains("failed and debit")) return "PAYMENT_FAILED_DEBITED"; return null; }
}
