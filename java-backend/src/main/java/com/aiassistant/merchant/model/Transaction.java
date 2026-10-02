package com.aiassistant.merchant.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "transactions", indexes = {@Index(name = "idx_transaction_id", columnList = "transactionId", unique = true)})
public class Transaction {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Long id;
    @Column(nullable = false, unique = true) public String transactionId;
    @Column(nullable = false) public String merchantId;
    @Column(nullable = false) public double amount;
    @Column(nullable = false) public LocalDateTime transactionTime;
    @Column(nullable = false) public String paymentStatus;
    @Column(nullable = false) public String paymentMethod;
    @Column(nullable = false) public String deviceType;
    @Column(nullable = false) public String location;
    @Column(nullable = false) public int failedAttempts;
    @Column(nullable = false) public int transactionFrequency;
    @Column(nullable = false) public int customerAgeDays;
    @Column(nullable = false) public int previousChargebacks;
    public String disputeType;
    @Column(nullable = false) public String fraudRiskLabel;
}
