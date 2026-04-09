---
name: nais-manifest
description: Generer og vedlikehold NAIS-manifest — spec, database, Kafka, auth, accessPolicy, ressurser
---

# NAIS-manifest

Bruk denne skillen når du skal lage eller oppdatere et komplett NAIS-manifest.

## Fremgangsmåte

1. **Les eksisterende NAIS-manifester** i `.nais/` eller `nais/` for å forstå hvordan applikasjonen er satt opp i dag. Bruk eksisterende `namespace` og `labels.team` — ikke anta verdier.
2. Avklar om applikasjonen er backend (Kotlin) eller frontend (Node.js), siden port, health paths og observability-oppsett kan variere.
3. Kartlegg hvilke ressurser applikasjonen trenger, for eksempel database, Kafka, auth, ingress og scaling.
4. Gjenbruk eksisterende stier for health, readiness og metrics fra nåværende manifester.
5. Bruk miljøspesifikke manifester (`app-dev.yaml`, `app-prod.yaml`) når repoet allerede følger det mønsteret.

## Manifest-mal

Generer manifestet med denne strukturen:

```yaml
apiVersion: nais.io/v1alpha1
kind: Application
metadata:
  name: {app-name}
  namespace: {team-namespace}  # Read from existing manifest
  labels:
    team: {team-namespace}
spec:
  image: {{ image }}
  port: 8080  # Check existing manifests — varies per repo (for example 3000 for frontend)

  # Paths vary per repo — check existing manifests for actual values
  prometheus:
    enabled: true
    path: /metrics  # or /internal/prometheus
  liveness:
    path: /isalive  # or /internal/health/livenessState
    initialDelay: 5
  readiness:
    path: /isready  # or /internal/health/readinessState
    initialDelay: 5

  resources:
    requests:
      cpu: 50m
      memory: 256Mi
    limits:
      memory: 512Mi
```

**Viktig**: Sjekk alltid eksisterende NAIS-manifester for korrekt `port`, `prometheus.path`, `liveness.path` og `readiness.path`. Disse varierer mellom repoer.

## PostgreSQL Database

Legg til PostgreSQL når applikasjonen trenger database:

```yaml
gcp:
  sqlInstances:
    - type: POSTGRES_17  # Check repo's existing manifests for actual version
      databases:
        - name: myapp-db
          envVarPrefix: DB
```

Dette gir typisk følgende miljøvariabler: `DB_HOST`, `DB_PORT`, `DB_DATABASE`, `DB_USERNAME`, `DB_PASSWORD`.

## Kafka

Legg til Kafka når applikasjonen produserer eller konsumerer meldinger:

```yaml
kafka:
  pool: nav-dev  # or nav-prod
```

## Azure AD

Bruk Azure AD når applikasjonen trenger autentisering eller validering av tokens fra Azure AD:

```yaml
azure:
  application:
    enabled: true
    tenant: nav.no
```

## TokenX (on-behalf-of)

Bruk TokenX når applikasjonen skal gjøre kall på vegne av en innlogget bruker.

```yaml
tokenx:
  enabled: true
```

For ren maskin-til-maskin-kommunikasjon, bruk Maskinporten. Systembrukere er legacy — bruk Maskinporten/OAuth for nye M2M-integrasjoner.

## accessPolicy

Definer eksplisitt nettverkstilgang for alle tjenester:

```yaml
accessPolicy:
  inbound:
    rules:
      - application: calling-app
        namespace: calling-namespace
  outbound:
    rules:
      - application: downstream-app
        namespace: downstream-namespace
```

## Ingress

Legg til `ingresses` ved behov, og gjenbruk etablerte URL-mønstre i repoet:

```yaml
ingresses:
  - https://<app>.intern.dev.nav.no   # Interne apper (ansattflater)
  - https://<app>.ekstern.dev.nav.no  # Eksterne apper (brukerflater)
```

## Scaling

Bruk eksisterende mønstre for `replicas`, og vær forsiktig med endringer i produksjon:

```yaml
replicas:
  min: 2
  max: 4
  cpuThresholdPercentage: 80
```

## Auto-Instrumentation (Observability)

Aktiver NAIS auto-instrumentation når applikasjonen skal eksponere tracing og standard observability-signaler:

```yaml
spec:
  observability:
    autoInstrumentation:
      enabled: true
      runtime: java  # or nodejs, python
```

## Boundaries

### ✅ Always
- Include liveness, readiness, and metrics endpoints
- Set memory limits
- Define explicit `accessPolicy`
- Use environment-specific manifests (`app-dev.yaml`, `app-prod.yaml`)

### ⚠️ Ask First
- Changing production resource limits or replicas
- Adding new GCP resources (cost implications)
- Modifying network policies
- Changing CPU limits (can cause throttling — follow existing manifests)

### 🚫 Never
- Store secrets in Git
- Deploy without CI/CD pipeline
- Skip health endpoints
