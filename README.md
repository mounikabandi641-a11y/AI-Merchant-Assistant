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

## Build

```powershell
cd frontend
npm run build

cd ..\java-backend
mvn package
```
