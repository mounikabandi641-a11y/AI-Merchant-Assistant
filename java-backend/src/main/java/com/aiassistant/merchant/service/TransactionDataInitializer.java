package com.aiassistant.merchant.service;

import com.aiassistant.merchant.model.Transaction;
import com.aiassistant.merchant.repository.TransactionRepository;
import java.io.BufferedReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

@Component
public class TransactionDataInitializer implements ApplicationRunner {
    private static final Logger logger = LoggerFactory.getLogger(TransactionDataInitializer.class);
    private static final String DATASET_PATH = "data/transactions.csv";
    private final TransactionRepository transactions;

    public TransactionDataInitializer(TransactionRepository transactions) {
        this.transactions = transactions;
    }

    @Override
    public void run(ApplicationArguments args) {
        if (transactions.count() > 0) return;

        Path dataset = findDataset();
        if (dataset == null) {
            logger.warn("No transactions loaded: {} was not found in this project or its parent directories.", DATASET_PATH);
            return;
        }

        try (BufferedReader reader = Files.newBufferedReader(dataset)) {
            List<String> headers = parseCsvRow(reader.readLine());
            Map<String, Integer> columns = new HashMap<>();
            for (int index = 0; index < headers.size(); index++) columns.put(headers.get(index), index);

            List<Transaction> rows = new ArrayList<>();
            String line;
            while ((line = reader.readLine()) != null) {
                List<String> values = parseCsvRow(line);
                Transaction transaction = new Transaction();
                transaction.transactionId = value(values, columns, "transaction_id");
                transaction.merchantId = value(values, columns, "merchant_id");
                transaction.amount = Double.parseDouble(value(values, columns, "amount"));
                transaction.transactionTime = LocalDateTime.parse(value(values, columns, "transaction_time"));
                transaction.paymentStatus = value(values, columns, "payment_status");
                transaction.paymentMethod = value(values, columns, "payment_method");
                transaction.deviceType = value(values, columns, "device_type");
                transaction.location = value(values, columns, "location");
                transaction.failedAttempts = Integer.parseInt(value(values, columns, "failed_attempts"));
                transaction.transactionFrequency = Integer.parseInt(value(values, columns, "transaction_frequency"));
                transaction.customerAgeDays = Integer.parseInt(value(values, columns, "customer_age_days"));
                transaction.previousChargebacks = Integer.parseInt(value(values, columns, "previous_chargebacks"));
                transaction.disputeType = value(values, columns, "dispute_type");
                transaction.fraudRiskLabel = value(values, columns, "fraud_risk_label");
                rows.add(transaction);
            }
            transactions.saveAll(rows);
            logger.info("Imported {} transactions from {}.", rows.size(), dataset);
        } catch (IOException | RuntimeException exception) {
            throw new IllegalStateException("Could not import synthetic transactions from " + dataset, exception);
        }
    }

    private Path findDataset() {
        Path directory = Path.of("").toAbsolutePath();
        while (directory != null) {
            Path candidate = directory.resolve(DATASET_PATH);
            if (Files.isRegularFile(candidate)) return candidate;
            directory = directory.getParent();
        }
        return null;
    }

    private String value(List<String> values, Map<String, Integer> columns, String name) {
        Integer index = columns.get(name);
        if (index == null || index >= values.size()) throw new IllegalArgumentException("Missing CSV column: " + name);
        return values.get(index);
    }

    private List<String> parseCsvRow(String line) {
        if (line == null) throw new IllegalArgumentException("CSV file is empty.");
        List<String> fields = new ArrayList<>();
        StringBuilder field = new StringBuilder();
        boolean quoted = false;
        for (int index = 0; index < line.length(); index++) {
            char current = line.charAt(index);
            if (current == '"') {
                if (quoted && index + 1 < line.length() && line.charAt(index + 1) == '"') {
                    field.append('"');
                    index++;
                } else {
                    quoted = !quoted;
                }
            } else if (current == ',' && !quoted) {
                fields.add(field.toString());
                field.setLength(0);
            } else {
                field.append(current);
            }
        }
        if (quoted) throw new IllegalArgumentException("Unclosed quoted CSV field.");
        fields.add(field.toString());
        return fields;
    }
}