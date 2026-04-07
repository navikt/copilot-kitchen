---
name: kotlin-ktor
description: Ktor Nav-spesifikt — NAVident JWT-claim, Koin DI, CallLogging MDC
---

# Ktor — Nav-spesifikt

## Autentisering

```kotlin
authenticate("azureAd") {
    get("/api/protected") {
        val principal = call.principal<JWTPrincipal>()
        val navIdent = principal?.getClaim("NAVident", String::class)
    }
}
```

## Avhengighetsinjeksjon

Koin er standard DI-rammeverk for Ktor-repoer i teamet (hvis `io.insert-koin` finnes i avhengighetene).

## Logging

```kotlin
install(CallLogging) {
    mdc("x_request_id") { call.request.header("X-Request-Id") ?: UUID.randomUUID().toString() }
}
```
