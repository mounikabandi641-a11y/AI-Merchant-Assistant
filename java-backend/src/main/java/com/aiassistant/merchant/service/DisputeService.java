package com.aiassistant.merchant.service;

import com.aiassistant.merchant.dto.DisputeResolutionRequest;
import com.aiassistant.merchant.dto.DisputeResolutionResponse;
import com.aiassistant.merchant.model.Dispute;
import com.aiassistant.merchant.model.Transaction;
import com.aiassistant.merchant.repository.DisputeRepository;
import com.aiassistant.merchant.repository.TransactionRepository;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;

@Service
public class DisputeService {
    public static final String FALLBACK_ACTION = "Review the case manually with the merchant support team and follow the approved dispute workflow before any irreversible action.";
    private static final Set<String> CATEGORIES = Set.of("PAYMENT_FAILED_DEBITED", "DUPLICATE_TRANSACTION", "PAYMENT_NOT_RECEIVED", "REFUND_ISSUE", "UNKNOWN_TRANSACTION", "OTHER");
    private final DisputeRepository disputes;
    private final TransactionRepository transactions;

    public DisputeService(DisputeRepository disputes, TransactionRepository transactions) { this.disputes = disputes; this.transactions = transactions; }

    public String normalize(String value) {
        if (value == null) return "OTHER";
        String normalized = value.trim().toUpperCase().replace('-', '_').replace(' ', '_');
        if (CATEGORIES.contains(normalized)) return normalized;
        return switch (normalized) {
            case "PAYMENT_FAILED", "FAILED_DEBITED", "FAILED_PAYMENT" -> "PAYMENT_FAILED_DEBITED";
            case "DUPLICATE", "DOUBLE_CHARGE" -> "DUPLICATE_TRANSACTION";
            case "NOT_RECEIVED", "MISSING_PAYMENT" -> "PAYMENT_NOT_RECEIVED";
            case "REFUND", "CHARGEBACK" -> "REFUND_ISSUE";
            case "UNKNOWN" -> "UNKNOWN_TRANSACTION";
            default -> "OTHER";
        };
    }

    public Set<String> categories() {
        return CATEGORIES;
    }

    public String recommendedAction(String disputeType, String transactionId) {
        Transaction transaction = transactionId == null ? null : transactions.findByTransactionId(transactionId).orElse(null);
        return action(normalize(disputeType), transaction);
    }

    public DisputeResolutionResponse resolve(DisputeResolutionRequest request) {
        String category = normalize(request.disputeType());
        Transaction transaction = transactions.findByTransactionId(request.transactionId()).orElse(null);
        String action = action(category, transaction);
        String id = "DISP-" + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss")) + "-" + request.transactionId();
        Dispute dispute = new Dispute(); dispute.disputeId = id; dispute.transactionId = request.transactionId(); dispute.disputeType = category;
        dispute.description = request.description(); dispute.status = "OPEN"; dispute.recommendedAction = action; dispute.createdAt = LocalDateTime.now(); disputes.save(dispute);
        return new DisputeResolutionResponse(id, category, summary(transaction), explanation(category, transaction, request.description()), action, "OPEN");
    }

    private Map<String, Object> summary(Transaction t) {
        if (t == null) return null;
        Map<String, Object> result = new LinkedHashMap<>(); result.put("transaction_id", t.transactionId); result.put("merchant_id", t.merchantId); result.put("amount", t.amount);
        result.put("payment_status", t.paymentStatus); result.put("payment_method", t.paymentMethod); result.put("device_type", t.deviceType); result.put("location", t.location);
        result.put("failed_attempts", t.failedAttempts); result.put("transaction_frequency", t.transactionFrequency); result.put("customer_age_days", t.customerAgeDays); result.put("previous_chargebacks", t.previousChargebacks); result.put("fraud_risk_label", t.fraudRiskLabel); return result;
    }
    private String explanation(String category, Transaction t, String description) {
        if (t == null) return "No matching transaction record was found in the application for this dispute reference. The case needs merchant verification before any support action is taken.";
        String status = t.paymentStatus.toLowerCase();
        return switch (category) {
            case "PAYMENT_FAILED_DEBITED" -> "The customer reports a debit even though the payment status is " + status + ". This should be reviewed against settlement and processing logs before any refund decision.";
            case "DUPLICATE_TRANSACTION" -> "The dispute indicates a possible duplicate payment or repeated charge. Current transaction details show " + t.failedAttempts + " failed attempts and " + t.previousChargebacks + " prior chargeback references for review.";
            case "PAYMENT_NOT_RECEIVED" -> "The customer indicates the payment was not received or not confirmed. The current transaction status is " + status + ", which requires merchant verification.";
            case "REFUND_ISSUE" -> "This dispute references a refund problem. Review the original payment status and prior settlement history before approving or denying any refund workflow.";
            case "UNKNOWN_TRANSACTION" -> "The dispute cannot be mapped to a clearly identifiable transaction within the application. Merchant review is required before any final action.";
            default -> "The dispute description is '" + description.trim() + "'. The case does not clearly match a standard category and should be reviewed manually.";
        };
    }
    private String action(String category, Transaction t) {
        if (t == null) return "Verify the transaction reference, payment logs, and merchant account details before any refund or support action.";
        return switch (category) {
            case "PAYMENT_FAILED_DEBITED" -> "Verify the final settlement status and confirm whether the debit was a successful authorization or a failed payment, then follow the approved support/refund workflow.";
            case "DUPLICATE_TRANSACTION" -> "Review duplicate transaction records, payment gateway logs, and customer confirmation before any refund or reversal decision.";
            case "PAYMENT_NOT_RECEIVED" -> "Check the payment processor, bank transfer status, and merchant reconciliation records before taking further action.";
            case "REFUND_ISSUE" -> "Confirm the original transaction history and refund policy, then route the case to the manual support workflow for approval.";
            case "UNKNOWN_TRANSACTION" -> "Request more payment details from the customer, then verify the transaction reference against merchant or processor records.";
            default -> FALLBACK_ACTION;
        };
    }
}
