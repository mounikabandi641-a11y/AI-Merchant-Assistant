# Java Spring Boot Backend

This is the application backend. It uses Spring Boot 3.3.5, Java 17, Maven, Spring Web, Spring Data JPA/Hibernate, and SQLite.

## Risk scoring

`RiskService` provides deterministic risk estimates from the transaction attributes available to the application. Its score is a review signal, not a fraud verdict.

## Run

```powershell
cd java-backend
mvn spring-boot:run
```

The server listens on `http://localhost:8080`. For local web development, run Vite separately; its proxy forwards relative API requests to Java. For production, the Java app serves the React build from the same origin. The Java API exposes `/health`, `/transactions`, `/transactions/{transaction_id}`, `/api/fraud/predict`, `/api/disputes/resolve`, `/api/disputes`, `/api/disputes/{dispute_id}`, and `/api/assistant/chat`.

## Deploy on Render

Render does not provide a native JVM runtime, so create a Docker Web Service from the existing repository with:

- Runtime: Docker
- Root Directory: leave blank (repository root)
- Dockerfile Path: `java-backend/Dockerfile`
- Docker Context: `.` (repository root)

The Dockerfile builds React using `npm ci` and `npm run build`, copies `frontend/dist` into the Spring Boot static resources, then runs `mvn clean package` from `java-backend`. The container start command is `java -jar target/merchant-assistant-backend-0.1.0.jar`. Both image stages use Java 17. Render supplies `PORT`; Spring Boot binds to it and defaults to `8080` locally.

Configure these environment variables:

- `SQLITE_DATABASE_FILE`: `/var/data/merchant_assistant.db` when using a persistent disk.

Attach a Render persistent disk mounted at `/var/data` for SQLite data to survive restarts and deploys. Persistent disks require a paid Render service. Without one, SQLite is on ephemeral storage and transaction/dispute changes can be lost when the instance is replaced. The Docker image includes the unchanged `data/transactions.csv` at `/app/data/transactions.csv`; when the database is empty, startup imports all 1,200 rows.

The UI and API share the Render service origin; no frontend API URL environment variable or CORS configuration is required for the combined deployment. The Vite proxy remains configured for local development.
