FROM eclipse-temurin:21-jre

ARG SYNTHEA_VERSION=v4.0.0
ADD --chmod=644 https://github.com/synthetichealth/synthea/releases/download/${SYNTHEA_VERSION}/synthea-with-dependencies.jar /opt/synthea.jar

WORKDIR /data
ENTRYPOINT ["java", "-jar", "/opt/synthea.jar"]
