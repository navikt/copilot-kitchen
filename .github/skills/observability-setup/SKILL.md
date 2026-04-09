---
name: observability-setup
description: Observability for Nav-apper — metrikker, logging, tracing, alerts, Micrometer, PromQL/LogQL og Faro for backend/frontend
---

# Sett opp observability

Bruk denne skillen når du skal etablere eller forbedre observability i en Nav-applikasjon. Hold hovedreglene korte. Bruk `references/` for detaljer.

## Kort intro

- **Metrikker** forteller *hva* som skjer
- **Logger** forklarer *hvorfor* det skjedde
- **Traces** viser *hvor* i flyten det skjedde
- Verifiser alltid eksisterende oppsett i repoet før du legger til nye målepunkter, labels eller varsler

## Arbeidsflyt

1. Les NAIS-manifest, `application*.yaml`, `build.gradle.kts` eller `package.json` for eksisterende observability-oppsett.
2. Finn etablerte mønstre for Micrometer, `prom-client`, strukturert logging, health-endepunkter og tracing.
3. Verifiser hvilke endepunkter som faktisk brukes (`/isalive`, `/isready`, `/metrics`, `/internal/*`, `/actuator/*`).
4. Start med standardmålinger og utvid med domenemetrikker som gir operativ verdi.
5. Legg til dashboards og varsler når metrikkene og label-settet er stabile.

## Navngivning for metrikker og labels

### Metrikker
- Bruk `snake_case`
- Bruk enhetssuffiks når det er relevant: `_seconds`, `_bytes`, `_milliseconds`
- Countere skal ha suffikset `_total`
- Bruk navn som beskriver domenet
- Unngå `camelCase`, forkortelser uten mening og miljøspesifikke navn

### Labels
- Hold labels lave i kardinalitet og stabile over tid
- Gode labels: `method`, `route`, `status`, `event_type`, `result`, `consumer_group`
- Dårlige labels: `user_id`, `email`, `fnr`, `trace_id`, `transaction_id`, rå URL-er med dynamiske segmenter
- Foretrekk normaliserte verdier som `/api/oppgaver/:id`
- Hver unik label-kombinasjon gir en ny tidsserie: legg bare til labels som brukes i dashboards, varsler eller feilsøking

## Backend (Kotlin/Spring)

- Aktiver Prometheus/Micrometer og behold eksisterende registry-oppsett hvis det finnes
- Sørg for health- og metrics-endepunkter som stemmer med NAIS-manifestet
- Bruk `Counter`, `Timer`, `Gauge` og `DistributionSummary` bevisst
- Mål viktige domenehendelser, køstørrelser, feilrater og behandlingstid
- Aktiver OpenTelemetry auto-instrumentation i NAIS før du legger til manuelle spans

Se `references/micrometer.md` for Kotlin/Spring-eksempler, health-oppsett og domenemetrikker.

## Frontend (Next.js)

- Bruk Faro når appen trenger frontend-feil, brukerhendelser eller innsikt i web-vitals
- Skill mellom tekniske hendelser og reelle domenehendelser
- Send aldri persondata, tokens eller andre hemmeligheter til frontend-observability
- Samordne event-navn og felter med backend der korrelasjon er viktig

Se `references/alerting.md` for Faro-oppsett og varslingsmønstre.

## Logging og tracing

- Logg strukturert JSON til stdout/stderr
- Følg eksisterende mønstre med MDC, `kv()` eller tilsvarende strukturerte argumenter
- Inkluder `trace_id` og relevant kontekst når loggingoppsettet støtter det
- Ikke bruk logger som erstatning for metrikker; metrikker skal svare på frekvens, volum og varighet
- Bruk tracing for request-kjeder, Kafka-flyt og kall mot databaser eller eksterne tjenester

Se `references/promql-logql.md` for PromQL-, LogQL- og dashboard-eksempler.

## Varsling

- Varsle på brukeropplevde symptomer først: feilrate, latency, utilgjengelighet og restarts
- Bruk runbook-lenker og tydelige annotasjoner
- Hold terskler forsiktige til du kjenner trafikkmønstrene
- Skill mellom `warning`, `critical` og informative varsler

Se `references/alerting.md` for Prometheus-regler, Slack-integrasjon og vanlige varslingsmønstre.

## Sjekkliste

- [ ] Health-, readiness- og metrics-endepunkter stemmer med NAIS-manifestet
- [ ] Auto-instrumentation er vurdert eller aktivert for riktig runtime
- [ ] Strukturert logging er på plass med korrelasjonsfelt der det er relevant
- [ ] Viktige domenemetrikker er definert med stabile navn og labels
- [ ] Dashboards dekker trafikkvolum, feilrate, latency og sentrale domeneindikatorer
- [ ] Varsler finnes for høy feilrate, høy latency, pod restarts og kritiske avhengigheter
- [ ] Logger, traces og labels på metrikker inneholder ikke sensitive data

## Boundaries

### ✅ Alltid
- Bruk `snake_case` og enhetssuffiks for metrikker
- Bruk lave og begrensede label-verdier
- Følg eksisterende logging- og metrikkmønstre i repoet
- Verifiser health paths, scrape paths og tracing-oppsett mot faktisk konfigurasjon

### ⚠️ Spør først
- Nye labels som kan øke kardinalitet vesentlig
- Endring av produksjonsterskler for varsler
- Nye dashboards, mapper eller varslingskanaler som påvirker teamets arbeidsflyt

### 🚫 Aldri
- Logg eller eksponer PII, tokens, passord eller andre hemmeligheter
- Bruk `camelCase` i metric-navn
- Bruk labels med høy kardinalitet eller ubegrensede verdier
- Legg til observability-kode som ikke kan forklares operativt eller brukes i praksis
