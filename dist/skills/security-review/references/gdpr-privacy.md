# GDPR og personvern

## Håndtering av persondata

Kartlegg hvilke datafelter som faktisk er nødvendige. Del gjerne data i tre nivåer:

- **Direkte identifikatorer**: fødselsnummer, navn, e-post, telefonnummer
- **Sensitive eller særskilte kategorier**: helseopplysninger, fagforeningsmedlemskap, biometriske data
- **Støtte- og driftsdata**: saks-ID, korrelasjons-ID, tekniske statusfelter

Be om dokumentasjon på behandlingsgrunnlag per formål. Vanlige grunnlag er lovpålagt behandling, avtale eller samtykke. Ikke bruk samtykke som standard hvis løsningen egentlig bygger på lov eller avtale.

```kotlin
// ✅ Good - collect only what the feature needs
data class UserProfileMinimal(
    val id: String,
    val email: String,
    val displayName: String,
)

// ❌ Bad - collects more personal data than the feature needs
data class UserProfileVerbose(
    val id: String,
    val email: String,
    val displayName: String,
    val phoneNumber: String,
    val address: String,
    val dateOfBirth: LocalDate,
)
```

Sjekk at hvert felt er nødvendig, at formålet er forklart, og at sensitive felter ikke lekker i logger, events eller feilmeldinger.

## Lagringstid

Lagringstid skal være definert, begrunnet og implementert.

```kotlin
@Configuration
@EnableScheduling
class SchedulingConfiguration

@Component
class RetentionJob(
    private val repository: UserDataRepository,
    private val logger: Logger,
) {
    @Scheduled(cron = "0 0 2 * * *")
    fun deleteExpiredData() {
        val retentionDays = 365
        val cutoffDate = LocalDate.now().minusDays(retentionDays.toLong())

        repository.deleteOlderThan(cutoffDate)
        logger.info("Deleted expired user data", kv("cutoff_date", cutoffDate))
    }
}
```

Se etter automatisk sletting eller arkivering, retention-perioder som kan spores til regelverk eller policy, og at også testdata, eksportfiler, backup og analytics-datasett er vurdert. Hvis data må beholdes for statistikk eller revisjon, vurder anonymisering i stedet for full identitet.

## Anonymisering av data

Anonymisering betyr at personen ikke lenger kan identifiseres. Pseudonymisering reduserer risiko, men er fortsatt personopplysninger under GDPR. Vanlige teknikker er å fjerne direkte identifikatorer, bruke irreversible eller nøytrale erstatninger, aggregere data eller splitte identitet og domenedata med streng tilgangskontroll.

```kotlin
fun anonymizeUser(userId: String) {
    repository.update(userId) {
        it.copy(
            name = "Anonymized User",
            email = "anonymized@deleted.local",
            phoneNumber = null,
            deletedAt = LocalDateTime.now(),
        )
    }

    logger.info("User anonymized", kv("user_id", userId))
}
```

Sjekk når anonymisering brukes, hvem som kan trigge den, og hvordan downstream-systemer håndterer anonymiserte data.

## Audit Logging med CEF-format

Nav bruker **ArcSight CEF (Common Event Format)** for audit logging ved tilgang til personopplysninger. Logg når persondata faktisk vises til en Nav-ansatt, ikke bare når et tilgangssjekk-kall skjer.

```kotlin
class AuditLogger(
    private val application: String,
) {
    private val auditLog = LoggerFactory.getLogger("auditLogger")

    fun logRead(
        fnr: String,
        employeeEmail: String,
        requestPath: String,
        permit: Boolean,
    ) {
        val now = Instant.now().toEpochMilli()
        val decision = if (permit) "Permit" else "Deny"

        auditLog.info(
            "CEF:0|$application|auditLog|1.0|audit:read|Sporingslogg|INFO|" +
                "end=$now duid=$fnr suid=$employeeEmail request=$requestPath " +
                "flexString1Label=Decision flexString1=$decision",
        )
    }
}
```

Tommelfingerregler: én brukerhandling per logglinje, ikke logg mer enn nødvendig i CEF-extension-feltene, bruk normalt `INFO`, og koordiner med audit logging-krav ved sentral rapportering.

## Samtykke-håndtering

Når samtykke er behandlingsgrunnlaget, må det være frivillig, spesifikt og like lett å trekke tilbake som å gi. Gjennomgangen bør avdekke om løsningen lagrer samtykkehistorikk og stopper videre behandling etter tilbaketrekking.

```kotlin
data class ConsentRecord(
    val userId: String,
    val purpose: String,
    val granted: Boolean,
    val grantedAt: Instant?,
    val withdrawnAt: Instant?,
)

fun withdrawConsent(userId: String, purpose: String) {
    consentRepository.markWithdrawn(
        userId = userId,
        purpose = purpose,
        withdrawnAt = Instant.now(),
    )
}
```

Sjekk at samtykke er separert per formål, at UI og API støtter tilbaketrekking uten manuell saksbehandling, at downstream-jobber og cache respekterer tilbaketrekking, og at behandlingsgrunnlag er dokumentert også når samtykke ikke brukes.
