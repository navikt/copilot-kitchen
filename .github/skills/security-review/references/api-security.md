# API-sikkerhet

## API-sikkerhetsmønstre

Sensitive eller offentlig tilgjengelige API-er bør ha både rate limiting og grenser for request-størrelse.

```kotlin
@Component
class ApiAbuseProtectionFilter(
    private val rateLimiterService: RateLimiterService,
) : OncePerRequestFilter() {
    override fun doFilterInternal(
        request: HttpServletRequest,
        response: HttpServletResponse,
        filterChain: FilterChain,
    ) {
        val clientKey = request.getHeader("Nav-Consumer-Id") ?: request.remoteAddr
        if (!rateLimiterService.allow(clientKey)) {
            response.sendError(HttpStatus.TOO_MANY_REQUESTS.value(), "Rate limit exceeded")
            return
        }

        val contentLength = request.contentLengthLong
        val maxBytes = 1024 * 1024L

        if (contentLength > maxBytes && contentLength != -1L) {
            response.sendError(HttpStatus.PAYLOAD_TOO_LARGE.value(), "Payload too large")
            return
        }

        filterChain.doFilter(request, response)
    }
}
```

Vurder egne grenser for sensitive endepunkter som innlogging, søk og eksport, samt inputvalidering før tunge database- eller filoperasjoner.

## CORS-konfigurasjon

CORS skal være eksplisitt. Tillat bare kjente origins, metoder og headere. `*` sammen med credentials er et rødt flagg.

```kotlin
@Bean
fun corsConfigurationSource(): UrlBasedCorsConfigurationSource {
    val configuration = CorsConfiguration()
    configuration.allowedOrigins = listOf(
        "https://www.nav.no",
        "https://app.intern.nav.no",
    )
    configuration.allowedMethods = listOf("GET", "POST", "PUT", "DELETE")
    configuration.allowedHeaders = listOf("Authorization", "Content-Type", "Nav-Call-Id")
    configuration.allowCredentials = true
    configuration.maxAge = 3600

    val source = UrlBasedCorsConfigurationSource()
    source.registerCorsConfiguration("/**", configuration)
    return source
}
```

Se etter at dev-domener er avgrenset til ikke-produksjonsmiljø, og at preflight-svar ikke åpner mer enn nødvendig.

## Sikkerhetsheadere

Sikkerhetsheadere bør være eksplisitt vurdert på webflater og administrative API-er.

```kotlin
@Bean
fun securityFilterChain(http: HttpSecurity): SecurityFilterChain {
    http {
        headers {
            contentSecurityPolicy {
                policyDirectives = "default-src 'self'; frame-ancestors 'none'; object-src 'none'"
            }
            referrerPolicy {
                policy = ReferrerPolicy.SAME_ORIGIN
            }
            permissionPolicy {
                policy = "geolocation=(), microphone=(), camera=()"
            }
            addHeaderWriter(StaticHeadersWriter("X-Content-Type-Options", "nosniff"))
            addHeaderWriter(StaticHeadersWriter("X-Frame-Options", "DENY"))
        }
    }
    return http.build()
}
```

Minstekrav i gjennomgangen er `Content-Security-Policy`, `X-Frame-Options`, `Strict-Transport-Security` for rene HTTPS-flater, `Referrer-Policy` og `X-Content-Type-Options`.

## Sikker håndtering av sesjoner og cookies

Hvis løsningen bruker sesjoner eller cookies, må de være sikre som standard. `csrf { disable() }` er bare riktig for rene stateless API-er som autentiserer med Bearer tokens og ikke bruker cookies eller server-side sesjoner.

```kotlin
@Bean
fun apiSecurity(http: HttpSecurity): SecurityFilterChain {
    // ✅ Stateless API med Bearer token — ingen cookies/sesjoner
    http {
        sessionManagement {
            sessionCreationPolicy(SessionCreationPolicy.STATELESS)
        }
        csrf {
            disable()  // Trygt i denne konfigen: ingen cookie-basert auth, kun Bearer token
        }
        // ...
    }
    return http.build()
}
```

⚠️ Browser-klient med cookies? Da MÅ CSRF-beskyttelse være PÅ.

Sjekk at session fixation-beskyttelse er aktiv hvis sesjoner brukes, at cookies settes med `Secure`, `HttpOnly` og riktig `SameSite`, at CSRF er vurdert eksplisitt for browser-baserte klienter, og at tokens og sessions ikke blandes uten tydelig begrunnelse.

Eksempel på sikker cookie-header:

```http
Set-Cookie: JSESSIONID=randomid; Secure; HttpOnly; SameSite=Lax
```

## Sporbarhet med Call ID

`Nav-Call-Id` gjør det mulig å følge et kall gjennom flere tjenester.

```kotlin
@Component
class CallIdFilter : OncePerRequestFilter() {
    override fun doFilterInternal(
        request: HttpServletRequest,
        response: HttpServletResponse,
        filterChain: FilterChain,
    ) {
        val callId = request.getHeader("Nav-Call-Id") ?: UUID.randomUUID().toString()
        MDC.put("call_id", callId)
        request.setAttribute("callId", callId)
        response.setHeader("Nav-Call-Id", callId)

        try {
            filterChain.doFilter(request, response)
        } finally {
            MDC.remove("call_id")
        }
    }
}
```

Send samme header videre til downstream-kall, og logg den strukturert i stedet for å logge persondata.

## STRIDE threat modeling

Bruk STRIDE som en kort sjekkliste før nye endepunkter eller integrasjoner:

| Trussel | Typisk spørsmål | Vanlige tiltak |
|---|---|---|
| Spoofing | Kan noen utgi seg for å være bruker eller tjeneste? | Sterk autentisering, tokenvalidering |
| Tampering | Kan input eller meldinger manipuleres? | Validering, integritetssjekk, signering |
| Repudiation | Kan handlinger benektes i ettertid? | Audit logging, `Nav-Call-Id`, sporbarhet |
| Information Disclosure | Kan data lekke via svar, logger eller feil? | Tilgangskontroll, masking, kryptering |
| Denial of Service | Kan API-et overbelastes? | Rate limiting, grenser for request-størrelse, ressursgrenser |
| Elevation of Privilege | Kan noen få mer tilgang enn de skal? | RBAC, least privilege, eksplisitte policy-sjekker |

## Hendelseshåndtering

Når gjennomgangen avdekker en mulig sikkerhetshendelse, følg denne rekkefølgen:

1. **Detect**: bekreft signalet med logger, alarmer og reproduksjon
2. **Contain**: begrens skade med sperring av konto, nøkkelrotasjon eller midlertidig blokkering
3. **Investigate**: gå gjennom audit-logger, `Nav-Call-Id` og scope for eksponering
4. **Remediate**: rett koden, patch avhengigheter og stram inn konfigurasjon
5. **Document**: skriv hendelsesnotat og oppdater runbook eller sjekkliste

Ved tvil: eskaler tidlig heller enn sent.
