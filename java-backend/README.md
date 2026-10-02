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

## Deploy on Render

Render does not provide a native JVM runtime, so create a Docker Web Service from the existing repository with:

- Runtime: Docker
- Root Directory: leave blank (repository root)
- Dockerfile Path: `java-backend/Dockerfile`
- Docker Context: `.` (repository root)

The Dockerfile build stage runs the requested build command `mvn clean package` from `java-backend`. Its container start command is `java -jar target/merchant-assistant-backend-0.1.0.jar`. Both image stages use Java 17. Render supplies `PORT`; Spring Boot binds to it and defaults to `8080` locally.

Configure these environment variables:

- `FRONTEND_ORIGIN`: the production frontend origin, for example `https://your-app.vercel.app` (origin only, no path).
- `SQLITE_DATABASE_FILE`: `/var/data/merchant_assistant.db` when using a persistent disk.

Attach a Render persistent disk mounted at `/var/data` for SQLite data to survive restarts and deploys. Persistent disks require a paid Render service. Without one, SQLite is on ephemeral storage and transaction/dispute changes can be lost when the instance is replaced. The Docker image includes the unchanged `data/transactions.csv` at `/app/data/transactions.csv`; when the database is empty, startup imports all 1,200 rows.

Set `VITE_API_BASE_URL` in the frontend's Vercel project settings to the deployed Render service URL. This value is baked into the Vite production build; the local Vite proxy remains active for development.
