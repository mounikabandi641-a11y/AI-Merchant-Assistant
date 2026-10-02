# Java Spring Boot Backend

This is the application backend. It uses Spring Boot 3.3.5, Java 17, Maven, Spring Web, Spring Data JPA/Hibernate, and SQLite.

## Risk scoring

`RiskService` provides deterministic risk estimates from the transaction attributes available to the application. Its score is a review signal, not a fraud verdict.

## Run

```powershell
cd java-backend
mvn spring-boot:run
```

The server listens on `http://localhost:8080`. The React development server can call it using the existing relative URLs by running Vite with a proxy, or the frontend can be served from the same origin after its production build. The Java API exposes the existing `/health`, `/transactions`, `/api/fraud/predict`, `/api/disputes`, and `/api/assistant/chat` routes.
