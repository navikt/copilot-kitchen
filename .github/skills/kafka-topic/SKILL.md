---
name: kafka-topic
description: Sett opp Kafka-topic, consumer og producer — mønstre, idempotens, feilhåndtering, NAIS-konfig og testing
---

# Kafka — Topic, Consumer og Producer

Nav-team bruker typisk **plain Apache Kafka clients** på NAIS Kafka — ikke Rapids & Rivers.

## Fremgangsmåte

1. Les NAIS-manifest for Kafka pool-konfigurasjon
2. Søk i kodebasen etter eksisterende consumere/producere og følg samme mønstre
3. Sjekk `build.gradle.kts` for Kafka-avhengigheter

## NAIS Kafka-konfigurasjon

```yaml
# nais.yaml
spec:
  kafka:
    pool: nav-dev  # eller nav-prod
```

### SSL (NAIS-injiserte env vars)
NAIS injiserer automatisk SSL-konfigurasjon:
- `KAFKA_BROKERS` — bootstrap servers
- `KAFKA_TRUSTSTORE_PATH` — truststore-fil
- `KAFKA_KEYSTORE_PATH` — keystore-fil
- `KAFKA_CREDSTORE_PASSWORD` — passord for begge

## Consumer-mønster (Kotlin)

```kotlin
while (running) {
    val records = consumer.poll(Duration.ofMillis(1000))
    records.forEach { record ->
        try {
            processRecord(record)
        } catch (e: Exception) {
            logger.error("Feil ved prosessering av melding", kv("topic", record.topic()), kv("partition", record.partition()), kv("offset", record.offset()), e)
            // håndter feil — ikke svelg stille
        }
    }
    consumer.commitSync()
}
```

## Producer-mønster (Kotlin)

```kotlin
producer.send(ProducerRecord(topic, key, value)) { metadata, exception ->
    if (exception != null) {
        logger.error("Feil ved sending til Kafka", kv("topic", topic), exception)
    }
}
```

## Spring Kafka

### Consumer med @KafkaListener
```kotlin
@KafkaListener(topics = ["\${kafka.topic.name}"], groupId = "\${kafka.consumer.group-id}")
fun consume(record: ConsumerRecord<String, String>) {
    processRecord(record)
}
```

### Producer med KafkaTemplate
```kotlin
kafkaTemplate.send(topic, key, value)
```

### Spring Kafka SSL-konfig (application.yml)
```yaml
spring:
  kafka:
    bootstrap-servers: ${KAFKA_BROKERS}
    properties:
      security.protocol: SSL
      ssl.truststore.location: ${KAFKA_TRUSTSTORE_PATH}
      ssl.truststore.password: ${KAFKA_CREDSTORE_PASSWORD}
      ssl.keystore.location: ${KAFKA_KEYSTORE_PATH}
      ssl.keystore.password: ${KAFKA_CREDSTORE_PASSWORD}
```

## Idempotens

Implementer dedup med event-ID der det er nødvendig:

```kotlin
fun processRecord(record: ConsumerRecord<String, String>) {
    val eventId = extractEventId(record)
    if (alreadyProcessed(eventId)) return
    // prosesser...
    markProcessed(eventId)
}
```

## Event-konvensjoner

- Navngi events i **fortid** og **snake_case**: `vedtak_fattet`, `soknad_sendt`
- Key: bruker-ID eller entitet-ID
- Value: JSON med event-data

## Sjekkliste

- [ ] Kafka pool i NAIS-manifest
- [ ] Consumer/producer følger eksisterende mønstre i repoet
- [ ] Idempotent behandling der nødvendig
- [ ] Feilhåndtering og strukturert logging (aldri PII)
- [ ] Metrikker for prosesserte events
- [ ] Tester etter eksisterende Kafka-testmønstre
