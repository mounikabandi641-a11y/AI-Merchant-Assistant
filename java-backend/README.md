# Java Spring Boot Backend

This backend runs alongside the existing Python/FastAPI service. It uses Spring Boot 3.3.5, Java 17, Maven, Spring Web, Spring Data JPA/Hibernate, and SQLite.

## ML compatibility note

The existing `model/random_forest_risk_model.joblib` is a Python scikit-learn Pipeline. Java cannot execute that artifact directly without a Python runtime or a model conversion step. This project therefore uses the explicitly named deterministic `RiskService` compatibility scorer so the API is available without silently claiming Random Forest parity. The original Python Random Forest remains untouched and remains the reference implementation. A future ONNX conversion can replace this service after validating prediction parity.

## Run

```powershell
cd java-backend
mvn spring-boot:run
```

The server listens on `http://localhost:8080`. The React development server can call it using the existing relative URLs by running Vite with a proxy, or the frontend can be served from the same origin after its production build. The Java API exposes the existing `/health`, `/transactions`, `/api/fraud/predict`, `/api/disputes`, and `/api/assistant/chat` routes.
