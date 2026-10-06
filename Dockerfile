FROM node:20-alpine AS frontend-build

WORKDIR /workspace/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM maven:3.9.9-eclipse-temurin-17 AS java-build

WORKDIR /workspace
COPY java-backend/pom.xml java-backend/pom.xml
COPY java-backend/src java-backend/src
COPY data/transactions.csv data/transactions.csv
COPY --from=frontend-build /workspace/frontend/dist/ java-backend/src/main/resources/static/

WORKDIR /workspace/java-backend
RUN mvn clean package

FROM eclipse-temurin:17-jre

WORKDIR /app/java-backend
COPY --from=java-build /workspace/java-backend/target/merchant-assistant-backend-0.1.0.jar target/merchant-assistant-backend-0.1.0.jar
COPY --from=java-build /workspace/data/transactions.csv /app/data/transactions.csv

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "target/merchant-assistant-backend-0.1.0.jar"]