package com.aiassistant.merchant.controller;

import com.aiassistant.merchant.dto.*;
import com.aiassistant.merchant.model.Dispute;
import com.aiassistant.merchant.model.Transaction;
import com.aiassistant.merchant.repository.DisputeRepository;
import com.aiassistant.merchant.repository.TransactionRepository;
import com.aiassistant.merchant.service.AssistantService;
import com.aiassistant.merchant.service.DisputeService;
import com.aiassistant.merchant.service.RiskService;
import jakarta.validation.Valid;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
public class ApiController {
    private final TransactionRepository transactions; private final DisputeRepository disputes; private final RiskService risk; private final DisputeService disputeService; private final AssistantService assistant;
    public ApiController(TransactionRepository transactions, DisputeRepository disputes, RiskService risk, DisputeService disputeService, AssistantService assistant) { this.transactions = transactions; this.disputes = disputes; this.risk = risk; this.disputeService = disputeService; this.assistant = assistant; }

    @GetMapping("/health") public Map<String, String> health() { return Map.of("status", "ok"); }

    @GetMapping({"/transactions", "/transactions/"}) public List<Transaction> listTransactions(@RequestParam(defaultValue = "0") int skip, @RequestParam(defaultValue = "100") int limit) { return transactions.findAll().stream().skip(Math.max(0, skip)).limit(Math.max(0, limit)).toList(); }
    @GetMapping("/transactions/{transactionId}") public ResponseEntity<?> getTransaction(@PathVariable String transactionId) { return transactions.findByTransactionId(transactionId).<ResponseEntity<?>>map(ResponseEntity::ok).orElseGet(() -> ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("detail", "Transaction with transaction_id '" + transactionId + "' not found."))); }
    @PostMapping("/transactions") public ResponseEntity<?> createTransaction(@Valid @RequestBody TransactionRequest request) { if (transactions.existsByTransactionId(request.transactionId())) return ResponseEntity.badRequest().body(Map.of("detail", "Transaction with transaction_id '" + request.transactionId() + "' already exists.")); Transaction t = new Transaction(); t.transactionId = request.transactionId(); t.merchantId = request.merchantId(); t.amount = request.amount(); t.transactionTime = request.transactionTime() == null ? LocalDateTime.now() : request.transactionTime(); t.paymentStatus = request.paymentStatus(); t.paymentMethod = request.paymentMethod(); t.deviceType = request.deviceType(); t.location = request.location(); t.failedAttempts = request.failedAttempts(); t.transactionFrequency = request.transactionFrequency(); t.customerAgeDays = request.customerAgeDays(); t.previousChargebacks = request.previousChargebacks(); t.disputeType = request.disputeType(); t.fraudRiskLabel = request.fraudRiskLabel(); return ResponseEntity.status(HttpStatus.CREATED).body(transactions.save(t)); }

    @PostMapping("/api/fraud/predict") public FraudPredictionResponse predict(@RequestBody FraudPredictionRequest request) { return risk.predict(request); }

    @GetMapping({"/disputes", "/api/disputes"}) public List<Dispute> listDisputes(@RequestParam(defaultValue = "0") int skip, @RequestParam(defaultValue = "100") int limit) { return disputes.findAll().stream().skip(Math.max(0, skip)).limit(Math.max(0, limit)).toList(); }
    @GetMapping({"/disputes/{disputeId}", "/api/disputes/{disputeId}"}) public ResponseEntity<?> getDispute(@PathVariable String disputeId) { return disputes.findByDisputeId(disputeId).<ResponseEntity<?>>map(ResponseEntity::ok).orElseGet(() -> ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("detail", "Dispute with dispute_id '" + disputeId + "' not found."))); }
    @PostMapping("/api/disputes/resolve") public DisputeResolutionResponse resolve(@Valid @RequestBody DisputeResolutionRequest request) { return disputeService.resolve(request); }
    @PatchMapping("/disputes/{disputeId}") public ResponseEntity<?> updateDispute(@PathVariable String disputeId, @RequestParam String status, @RequestParam(required = false) String recommendedAction) { var result = disputes.findByDisputeId(disputeId); if (result.isEmpty()) return ResponseEntity.badRequest().body(Map.of("detail", "Dispute with dispute_id '" + disputeId + "' was not found.")); Dispute d = result.get(); d.status = status; if (recommendedAction != null) d.recommendedAction = recommendedAction; return ResponseEntity.ok(disputes.save(d)); }

    @PostMapping("/api/assistant/chat") public AssistantChatResponse chat(@Valid @RequestBody AssistantChatRequest request) { return assistant.answer(request.message(), request.transactionId()); }
}
