---
name: tech-stack
description: Team eSyfos teknologivalg, bibliotekpreferanser og plattform. Brukes ved nye apper, omskrivinger, arkitekturvalg eller når du trenger oversikt over teamets teknologivalg.
---

# Tech Stack — Team eSyfo

## Plattform

- **NAIS** (Kubernetes) — [doc.nais.io](https://doc.nais.io)
- **Aksel** designsystem — [aksel.nav.no](https://aksel.nav.no)
- **Sikkerhet** — [sikkerhet.nav.no](https://sikkerhet.nav.no)
- **Observability**: Prometheus + Grafana Loki + Tempo/OpenTelemetry

## Auth-mekanismer

Sjekk NAIS-manifest (`nais.yaml`) for hvilke som brukes i det aktuelle repoet.

| Mekanisme | Bruk |
|---|---|
| Azure AD | Interne brukere og service-to-service |
| TokenX | OBO-flyt mellom interne tjenester |
| ID-porten | Innbyggere |
| Maskinporten | Eksterne organisasjoner |

- **Kotlin**: Texas sidecar (`localhost:3000`) — se `auth-overview`-skillen
- **TypeScript**: `@navikt/oasis` — se `auth-overview`-skillen

## Backend (Kotlin)

| Valg | Preferanse |
|---|---|
| **Språk** | Kotlin (ikke Java) |
| **Build** | Gradle med Kotlin DSL og Version Catalog |
| **Framework** | Ktor (standard) eller Spring Boot (noen eldre repoer) |
| **DB-tilgang** | Exposed (foretrukket for nye prosjekter). Kotliquery i noen eksisterende repoer. |
| **DI** | Koin (Ktor-repos), Spring DI (Spring-repos) |
| **Kafka** | Plain Apache Kafka clients — **ikke** Rapids & Rivers |
| **Migreringer** | Flyway |
| **Testing** | Kotest DescribeSpec + MockK + Testcontainers |
| **Auth-testing** | MockOAuth2Server |
| **Logging** | SLF4J med KotlinLogging, strukturert med kv()-felter der mønsteret finnes |
| **Metrikker** | Micrometer / Prometheus |

## Frontend (TypeScript)

| Valg | Preferanse |
|---|---|
| **Språk** | TypeScript (strict) |
| **UI-lib** | Aksel (`@navikt/ds-react`, `@navikt/ds-tokens`, `@navikt/aksel-icons`) |
| **Spacing** | Aksel tokens (`space-4`, `space-8`, etc.) — aldri Tailwind padding/margin |
| **Testing** | Vitest + Testing Library |
| **Auth** | `@navikt/oasis` |
| **Tall-formatering** | Norsk locale (mellomrom som tusenskilletegn) |

## Konvensjoner

- Engelsk kode, norsk brukerrettet tekst (klarspråk)
- Semantiske commits (`feat:`, `fix:`, `refactor:`, etc.)
- NAIS-manifest i repo-root eller `.nais/`-mappe
- Skills finnes for domenespesifikk veiledning — bruk dem
