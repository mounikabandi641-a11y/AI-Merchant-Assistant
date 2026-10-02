FROM maven:3.9.9-eclipse-temurin-17 AS build

WORKDIR /workspace
COPY java-backend/pom.xml java-backend/pom.xml
COPY java-backend/src java-backend/src
COPY data/transactions.csv data/transactions.csv

WORKDIR /workspace/java-backend
RUN mvn clean package

FROM eclipse-temurin:17-jre

WORKDIR /app/java-backend
COPY --from=build /workspace/java-backend/target/merchant-assistant-backend-0.1.0.jar target/merchant-assistant-backend-0.1.0.jar
COPY --from=build /workspace/data/transactions.csv /app/data/transactions.csv

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "target/merchant-assistant-backend-0.1.0.jar"]