---
name: security-review
description: Sikkerhetsgjennomgang før commit/push/PR — OWASP Top 10, Dependabot, Trivy, hemmeligheter, inputvalidering og referanser for GDPR/API-sikkerhet
---
# Sikkerhetsgjennomgang

Sikkerhetssjekk før commit, push og PR for Nav-applikasjoner. Dekker hemmeligheter, sårbarhetsskanning, OWASP Top 10, GDPR/personvern og API-sikkerhet. Hold hovedreglene korte; bruk `references/` for detaljer.

## Automatiserte skanninger

Kjør disse i terminalen:

```bash
# Skann repoet for kjente sårbarheter og hemmeligheter
trivy repo .

# Skann Docker image for HIGH/CRITICAL CVE-er
trivy image <image-name> --severity HIGH,CRITICAL

# Skann GitHub Actions workflows for usikre mønstre
zizmor .github/workflows/

# Raskt søk etter hemmeligheter i git-historikken
git log -p --all -S 'password' -- '*.kt' '*.ts' | head -100
git log -p --all -S 'secret' -- '*.kt' '*.ts' | head -100
```

## Parameteriserte SQL-spørringer

```kotlin
// ✅ Parameterisert spørring
fun findBruker(fnr: String): Bruker? =
    jdbcTemplate.queryForObject(
        "SELECT * FROM bruker WHERE fnr = ?",
        brukerRowMapper,
        fnr
    )

// ❌ SQL injection
fun findBrukerUnsafe(fnr: String): Bruker? =
    jdbcTemplate.queryForObject(
        "SELECT * FROM bruker WHERE fnr = '$fnr'",
        brukerRowMapper
    )
```

## Ingen PII i logger

```kotlin
// ✅ Logg korrelasjons-ID, ikke PII
log.info("Behandler sak for bruker", kv("sakId", sak.id), kv("tema", sak.tema))

// ❌ Aldri logg FNR, navn eller annen PII
log.info("Behandler sak for bruker ${bruker.fnr}")
```

## Hemmeligheter fra miljøvariabler

```kotlin
// ✅ Les fra miljø (Nais injiserer via Secret)
val dbPassword = System.getenv("DB_PASSWORD")
    ?: throw IllegalStateException("DB_PASSWORD mangler")

// ❌ Hardkodet hemmelighet
val dbPassword = "supersecret123"
```

## Nettverkspolicy (Nais)

```yaml
spec:
  accessPolicy:
    inbound:
      rules:
        - application: frontend-app
    outbound:
      rules:
        - application: pdl-api
          namespace: pdl
          cluster: prod-gcp
      external:
        - host: api.external-service.no
```

## OWASP Top 10

### A01: Broken Access Control

```kotlin
// ✅ Sjekk at bruker har tilgang til ressursen
@GetMapping("/api/vedtak/{id}")
fun getVedtak(@PathVariable id: UUID): ResponseEntity<VedtakDTO> {
    val bruker = hentInnloggetBruker()
    val vedtak = vedtakService.findById(id)
    if (vedtak.brukerId != bruker.id) {
        return ResponseEntity.status(HttpStatus.FORBIDDEN).build()
    }
    return ResponseEntity.ok(vedtak.toDTO())
}

// ❌ Ingen tilgangskontroll (IDOR)
@GetMapping("/api/vedtak/{id}")
fun getVedtak(@PathVariable id: UUID) = vedtakService.findById(id)
```

### A03: Injection

```kotlin
// ✅ Parameterisert spørring
jdbcTemplate.query("SELECT * FROM bruker WHERE fnr = ?", mapper, fnr)

// ❌ String-sammenslåing
jdbcTemplate.query("SELECT * FROM bruker WHERE fnr = '$fnr'", mapper)
```

### A05: Security Misconfiguration

```kotlin
// ✅ CORS kun for kjente domener
@Bean
fun corsFilter() = CorsFilter(CorsConfiguration().apply {
    allowedOrigins = listOf("https://my-app.intern.nav.no")
    allowedMethods = listOf("GET", "POST")
})

// ❌ Åpen CORS
allowedOrigins = listOf("*")
```

### A07: Cross-Site Scripting (XSS)

```tsx
// ✅ React escaper automatisk
<BodyShort>{bruker.navn}</BodyShort>

// ❌ Raw HTML injection
<div dangerouslySetInnerHTML={{ __html: userInput }} />
```

## GDPR og personvern

- Følg dataminimering, formålsbinding og innebygd personvern.
- Dokumenter behandlingsgrunnlag før innsamling eller visning av personopplysninger.
- Planlegg sletting, anonymisering og audit-logging sammen med funksjonaliteten.
- Samtykke skal være eksplisitt og lett å trekke tilbake når det er behandlingsgrunnlaget.

Se `references/gdpr-privacy.md` for detaljer om PII-kategorisering, retention, anonymisering, CEF-auditlogging og samtykkehåndtering.

## API-sikkerhet

- Begrens eksponering med rate limiting, grenser for request-størrelse og eksplisitt CORS.
- Bruk sikre headers, sikre cookies/sesjoner og `Nav-Call-Id`.
- Vurder STRIDE før nye endepunkter, spesielt for sensitive operasjoner og integrasjoner.
- Ha en enkel plan for hendelseshåndtering ved funn i gjennomgang eller drift.

Se `references/api-security.md` for Kotlin/Spring-eksempler og mer detaljerte mønstre.

## Filopplasting

```kotlin
// ✅ Valider filtype, størrelse og magic bytes
fun validateUpload(file: MultipartFile) {
    require(file.size <= 10 * 1024 * 1024) { "Fil for stor (maks 10 MB)" }
    require(file.contentType in ALLOWED_TYPES) { "Ugyldig filtype" }
    val bytes = file.bytes.take(8).toByteArray()
    require(verifyMagicBytes(bytes, file.contentType!!)) { "Filinnhold matcher ikke type" }
}
```

## Avhengigheter

```bash
# Kotlin
./gradlew dependencyUpdates
./gradlew dependencyCheckAnalyze

# Node/TypeScript
npm audit
npm audit fix
```

## Sjekkliste

- [ ] SQL-spørringer er parameteriserte
- [ ] Ingen PII i logger (FNR, navn, adresse)
- [ ] Hemmeligheter kun fra miljøvariabler
- [ ] Nais accessPolicy er eksplisitt (ingen åpen inbound)
- [ ] CORS begrenset til kjente domener
- [ ] Rate limiting vurdert for sensitive eller publikt eksponerte endepunkter
- [ ] Grenser for request-størrelse og payload-validering er på plass der store kall kan misbrukes
- [ ] Sikkerhetsheadere er satt for web/API-flater
- [ ] Sesjoner/cookies er `Secure`, `HttpOnly` og har riktig `SameSite`
- [ ] `Nav-Call-Id` brukes for korrelasjon mellom tjenester
- [ ] Input validert og sanitert
- [ ] Tilgangskontroll sjekker eierskap (ikke bare autentisering)
- [ ] Filopplasting validerer type, størrelse og innhold
- [ ] Behandlingsgrunnlag for persondata er dokumentert
- [ ] Retention, sletting eller anonymisering er definert for lagret persondata
- [ ] Samtykke lagres og kan trekkes tilbake når samtykke er behandlingsgrunnlaget
- [ ] Audit logging er vurdert for visning av personopplysninger
- [ ] Avhengigheter oppdatert og sårbarhetsskannet
- [ ] `trivy repo .` uten HIGH/CRITICAL funn
- [ ] `zizmor` godkjent for alle GitHub Actions workflows
- [ ] Det finnes ingen committede hemmeligheter i Git-historikken

## Referanser

| Ressurs | Bruksområde |
|---------|-------------|
| [sikkerhet.nav.no](https://sikkerhet.nav.no) | Navs Golden Path for sikkerhet |
| auth-overview skill | JWT-validering, TokenX, ID-porten, Maskinporten |
| `references/gdpr-privacy.md` | GDPR, personvern, retention, anonymisering og CEF-auditlogging |
| `references/api-security.md` | API-sikkerhet, headere, CORS, cookies, STRIDE og hendelseshåndtering |

For GDPR-detaljer, se `references/gdpr-privacy.md`. For API-sikkerhet, se `references/api-security.md`.
