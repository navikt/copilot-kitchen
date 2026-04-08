---
name: kotlin-spring
description: Spring Boot Nav-spesifikt — @ProtectedWithClaims, NAIS-miljøvariabler, testing med Testcontainers og MockOAuth2Server
---

# Spring Boot — Nav-spesifikt

## Autentisering

```kotlin
@ProtectedWithClaims(issuer = "azuread", claimMap = ["NAVident=*"])
```
Krever `token-validation-spring`-avhengigheten.

## NAIS-miljøvariabler for database

```yaml
spring:
  datasource:
    url: jdbc:postgresql://${DB_HOST}:${DB_PORT}/${DB_DATABASE}
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
```

## Testing

- `@SpringBootTest` + Testcontainers for integrasjonstester
- `@MockkBean` (krever `com.ninja-squad:springmockk`)
- MockOAuth2Server for autentiseringstester
