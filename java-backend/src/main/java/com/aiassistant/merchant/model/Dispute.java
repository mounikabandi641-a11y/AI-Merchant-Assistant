package com.aiassistant.merchant.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "disputes", indexes = {@Index(name = "idx_dispute_id", columnList = "disputeId", unique = true)})
public class Dispute {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Long id;
    @Column(nullable = false, unique = true) public String disputeId;
    @Column(nullable = false) public String transactionId;
    @Column(nullable = false) public String disputeType;
    @Column(nullable = false, columnDefinition = "TEXT") public String description;
    @Column(nullable = false) public String status;
    @Column(nullable = false, columnDefinition = "TEXT") public String recommendedAction;
    @Column(nullable = false) public LocalDateTime createdAt;
}
