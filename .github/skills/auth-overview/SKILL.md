---
name: auth-overview
description: Sett opp autentisering i en Nav-applikasjon — Azure AD, TokenX, ID-porten, Maskinporten, Texas sidecar (Kotlin) og Oasis (TypeScript)
---

# Autentiseringsoversikt — Nav

Oversikt over autentiseringsmekanismer i Nav. Bruk denne som referanse ved oppsett av autentisering i nye eller eksisterende tjenester.

## Autentiseringstyper

### 1. Azure AD / Entra ID (interne Nav-brukere)
```yaml
azure:
  application:
    enabled: true
    tenant: nav.no
```
Env vars: `AZURE_APP_CLIENT_ID`, `AZURE_APP_CLIENT_SECRET`, `AZURE_APP_WELL_KNOWN_URL`, `AZURE_OPENID_CONFIG_JWKS_URI`

### 2. TokenX (service-to-service, on-behalf-of)
```yaml
tokenx:
  enabled: true
accessPolicy:
  inbound:
    rules:
      - application: calling-service
        namespace: team-calling
```
Env vars: `TOKEN_X_WELL_KNOWN_URL`, `TOKEN_X_CLIENT_ID`, `TOKEN_X_PRIVATE_JWK`

### 3. ID-porten (innbyggere)
```yaml
idporten:
  enabled: true
  sidecar:
    enabled: true
    level: Level4
```

### 4. Maskinporten (eksterne organisasjoner)
```yaml
maskinporten:
  enabled: true
  scopes:
    consumes:
      - name: "nav:example/scope"
```

### 5. Systembruker via Maskinporten (Altinn 3)

Systembruker er en mekanisme i Altinn 3 der eksterne virksomheter oppretter en systembruker som gir tilgang til Nav-tjenester via Maskinporten. Se [Altinn 3 systembruker-dokumentasjon](https://docs.altinn.studio/authentication/what-do-you-get/systemuser/).

## Kotlin — Texas sidecar

Texas er en HTTP-sidecar som kjører på `localhost:3000` i NAIS-podden. Den håndterer tokenoperasjoner uten at applikasjonen trenger OAuth-biblioteker.

### Token (M2M)
```
POST http://localhost:3000/api/v1/token
Content-Type: application/json

{ "identity_provider": "azuread", "target": "api://cluster.namespace.app/.default" }
```

### Token Exchange (OBO)
```
POST http://localhost:3000/api/v1/token/exchange
Content-Type: application/json

{ "identity_provider": "tokenx", "target": "cluster:namespace:app", "user_token": "<brukerens token>" }
```

**Audience-format**:
- Azure AD: `api://cluster.namespace.app/.default`
- TokenX: `cluster:namespace:app`

### Introspect (validering)
```
POST http://localhost:3000/api/v1/introspect
Content-Type: application/json

{ "token": "<token som skal valideres>" }
```

**Caching**: Texas cacher tokens automatisk med 60 sekunders preemptiv refresh. Ikke implementer egen caching.

### Spring Boot-auth-dekorator
```kotlin
@ProtectedWithClaims(issuer = "azuread", claimMap = ["NAVident=*"])
```
Krever `token-validation-spring`-biblioteket.

### NAV-spesifikke JWT-claims
- `NAVident` — ansattens identifikator
- `oid` — objekt-ID i Azure AD

## TypeScript — Oasis

`@navikt/oasis` er Nav-biblioteket for token-validering og -utveksling i TypeScript.

### Validering
```typescript
import { validateToken, validateAzureToken, validateIdportenToken, validateTokenxToken } from "@navikt/oasis"

const result = await validateAzureToken(token)
if (result.ok) { /* gyldig */ }
```

### Token Exchange (OBO)
```typescript
import { requestOboToken } from "@navikt/oasis"

const obo = await requestOboToken(userToken, "cluster:namespace:app")
if (obo.ok) { /* bruk obo.token */ }
```

### M2M
```typescript
import { requestAzureClientCredentialsToken } from "@navikt/oasis"

const m2m = await requestAzureClientCredentialsToken("api://cluster.namespace.app/.default")
```

### Brukerinfo
```typescript
import { parseAzureUserToken, parseIdportenToken } from "@navikt/oasis"

const { NAVident, name, oid } = parseAzureUserToken(token)
const { pid } = parseIdportenToken(token) // pid = fødselsnummer
```

**Caching**: Oasis har innebygd SIEVE-cache med Prometheus-metrikker. Ikke implementer egen caching.

## Tilnærming

1. Les NAIS-manifestet for å identifisere hvilke autentiseringsmekanismer som er konfigurert
2. Søk i kodebasen etter eksisterende autentiseringsoppsett og følg samme mønster
3. Bruk Texas (Kotlin) eller Oasis (TypeScript) — ikke implementer OAuth-flyter manuelt

Komplett dokumentasjon om autentisering: https://doc.nais.io/auth/

## Boundaries

### ✅ Alltid
- Valider JWT-utsteder, audience, utløpstid og signatur
- Bruk kun HTTPS for tokenoverføring
- Definer eksplisitt `accessPolicy` i NAIS-manifestet
- Bruk miljøvariabler fra NAIS (aldri hardkod)

### 🚫 Aldri
- Hardkod klienthemmeligheter eller tokens
- Logg aldri hele JWT-er (eller deler som inneholder PII)
- Hopp aldri over tokenvalidering
- Ikke lagre tokens i localStorage
- Ikke lag egen token-caching (Texas/Oasis håndterer dette)
