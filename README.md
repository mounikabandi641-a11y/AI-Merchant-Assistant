# AI Merchant Assistant

A merchant operations application for transaction review, risk analysis, dispute resolution, and application-grounded assistant guidance.

## Current application

- `java-backend/`: Java 17, Spring Boot 3.3.5 REST API with Spring Data JPA, Hibernate, and SQLite.
- `frontend/`: React and Vite web application with dashboard, transaction ledger/details, risk analysis, dispute resolver, and AI Assistant.
- `data/transactions.csv`: the project's 1,200 synthetic transaction records. On a fresh Java database, the backend imports these records at startup only when the transactions table is empty.

The Java backend creates its SQLite database in `java-backend/merchant_assistant.db`. Database files and build outputs are local runtime artifacts and are not committed.

## Run the application

Start the Java backend from the repository root:

```powershell
cd java-backend
mvn spring-boot:run
```

Start the React frontend in another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies API requests to the Java backend at `http://localhost:8080`.

The local demo sign-in accepts any non-empty username and password. Transaction details can be opened from the ledger; **Ask Assistant** carries the selected transaction into assistant context.

## Single-URL deployment

The Render Docker service builds the React frontend, packages `frontend/dist` into the Spring Boot jar, and serves the UI and API from one origin. Configure the Render Web Service with the repository root as its Docker context and `java-backend/Dockerfile` as its Dockerfile. Do not set a subdirectory root; the build needs the root `data/transactions.csv` file.

The container binds to Render's `PORT` environment variable (local default `8080`). For durable SQLite data, mount a Render persistent disk at `/var/data` and set `SQLITE_DATABASE_FILE=/var/data/merchant_assistant.db`. The frontend uses relative API URLs in production.

## Build locally

```powershell
cd frontend
npm run build

cd ..\java-backend
mvn clean package
```

The Docker build runs both frontend and backend build steps and is the production packaging path.
