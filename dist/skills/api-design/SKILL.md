---
name: api-design
description: REST API-design for Ktor — URL-konvensjoner, StatusPages-basert feilhåndtering, paginering og input-validering
---
# API Design — REST
Standarder for REST API-design i Nav-applikasjoner bygget med Ktor.
## URL-konvensjoner
```
GET    /api/v1/vedtak              → List vedtak
GET    /api/v1/vedtak/{id}         → Hent enkelt vedtak
POST   /api/v1/vedtak              → Opprett vedtak
PUT    /api/v1/vedtak/{id}         → Oppdater vedtak (full)
PATCH  /api/v1/vedtak/{id}         → Oppdater vedtak (delvis)
DELETE /api/v1/vedtak/{id}         → Slett vedtak
```

### Regler
- Bruk **flertall** for ressursnavn: `/vedtak`, `/saker`, `/brukere`
- Bruk **kebab-case** for sammensatte navn: `/sykmeldinger`, `/oppfolgingsplaner`
- Bruk **path params** for identifikatorer: `/vedtak/{id}`
- Bruk **query params** for filtrering: `/vedtak?status=AKTIV&side=2`
- Maks **3 nivåer** nesting: `/saker/{id}/vedtak` (ikke dypere)

## HTTP-statuskoder
| Kode | Bruksområde |
|------|-------------|
| 200 | Vellykket henting/oppdatering |
| 201 | Ressurs opprettet (med `Location`-header) |
| 204 | Vellykket sletting (ingen body) |
| 400 | Ugyldig request (validering) |
| 401 | Ikke autentisert |
| 403 | Ikke autorisert (mangler tilgang) |
| 404 | Ressurs ikke funnet |
| 409 | Konflikt (duplikat, utdatert versjon) |
| 422 | Ugyldig input som er syntaktisk korrekt |
| 500 | Intern feil |

## Feilhåndtering — Ktor StatusPages

Bruk `StatusPages`-pluginen med en `sealed class ApiErrorException`-hierarki for strukturert feilhåndtering.
Alle exceptions kastet i routes fanges automatisk og mappes til en `ApiError`-respons med riktig HTTP-statuskode.

Nøkkelkomponenter:
- `ApiError` — Strukturert feilrespons med `status`, `type`, `message`, `path` og `timestamp`
- `ErrorType` enum — Kategoriserer feil (`NOT_FOUND`, `BAD_REQUEST`, `CONFLICT`, osv.)
- `ApiErrorException` sealed class — Subklasser for `ForbiddenException`, `BadRequestException`, `NotFoundException`, osv.
- `installStatusPages()` — Logger og responderer med riktig `ApiError`
- `determineApiError()` — Mapper Ktor-exceptions og egne exceptions til `ApiError`

Se [references/error-handling.md](references/error-handling.md) for komplett implementasjon.

## Paginering

Bruk `PaginatedResponse<T>` med `innhold`, `side`, `antallPerSide`, `totaltAntall` og `totaltAntallSider`.
Maks 100 elementer per side. Default er 20.

Se [references/code-examples.md](references/code-examples.md) for implementasjon og responseksempel.

## Input-validering

Valider all input tidlig i route-handleren. Kast `ApiErrorException.BadRequestException` ved ugyldig input.
Bruk `@Serializable` data classes for request-bodies med eksplisitte valideringsregler.

Se [references/code-examples.md](references/code-examples.md) for eksempel med `CreateVedtakRequest`.

## Versjonering

- Bruk URL-versjonering: `/api/v1/...`
- Bump versjon kun ved breaking changes
- Støtt gammel versjon i overgangsperiode
- Dokumenter endringer i changelog

## Grenser

### ✅ Alltid
- Flertall for ressursnavn
- Strukturert ApiError via StatusPages
- Valider all input
- Location-header ved 201

### ⚠️ Spør først
- Nye API-versjoner (breaking changes)
- Endring av eksisterende kontrakt
- Asynkrone operasjoner (202 Accepted)

### 🚫 Aldri
- Verb i URL-er (`/getVedtak`, `/createSak`)
- PII i URL-er eller query params (FNR, navn)
- 200 med feilmelding i body
- Ukonsistent navngiving mellom endepunkter
- Kaste exceptions som ikke fanges av StatusPages uten bevisst valg

## Referansefiler

- [references/error-handling.md](references/error-handling.md) — Komplett Ktor StatusPages-implementasjon (ApiError, ApiErrorException, installStatusPages, determineApiError)
- [references/code-examples.md](references/code-examples.md) — Pagineringsrespons og input-valideringseksempler
