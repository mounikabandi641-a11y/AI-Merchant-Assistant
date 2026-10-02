package com.aiassistant.merchant.repository;

import com.aiassistant.merchant.model.Dispute;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface DisputeRepository extends JpaRepository<Dispute, Long> {
    Optional<Dispute> findByDisputeId(String disputeId);
    boolean existsByDisputeId(String disputeId);
}
