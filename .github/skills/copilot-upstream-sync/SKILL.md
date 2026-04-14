---
name: copilot-upstream-sync
description: Sjekk navikt/copilot for nye mønstre, instructions og skills som er verdt å adoptere i copilot-kitchen
---

# Upstream-sync fra navikt/copilot

Strukturert gjennomgang av `navikt/copilot`-repoet for å finne oppdateringer verdt å ta inn i copilot-kitchen.

## Fremgangsmåte

### 1. Hent og sammenlign

Klon eller oppdater `navikt/copilot` og sammenlign med copilot-kitchen:

```bash
# Sammenlign instruksjoner
diff <(ls navikt-copilot/.github/instructions/) <(ls copilot-kitchen/instructions/)

# Sammenlign skills
diff <(ls navikt-copilot/.github/skills/) <(ls copilot-kitchen/skills/)

# Sammenlign agenter
diff <(ls navikt-copilot/.github/agents/) <(ls copilot-kitchen/agents/)
```

### 2. Vurder nye filer

For hvert nytt element i navikt/copilot, vurder:

| Spørsmål | Ja → | Nei → |
|----------|------|-------|
| Er det relevant for Nav-team generelt? | Gå videre | Hopp over |
| Er det generelt nok for alle team-repos? | Legg i `hovmester` | Legg i `backend`/`frontend` |
| Bør det alltid gjelde for en filtype? | Lag instruction med `applyTo` | Lag skill |
| Har det referansefiler? | Skill med `references/` | Instruction (inline eksempler) |

### 3. Sjekk eksisterende overlapp

For filer som finnes i begge repos, sammenlign dybde:
- Har navikt/copilot bedre kodeeksempler? → Oppdater vår versjon
- Har de nye seksjoner vi mangler? → Vurder om det er relevant
- Har de endret format eller struktur? → Vurder om vi bør følge

### 4. Adopsjonsregler

- **Instruction vs skill**: Se `.github/copilot-instructions.md` for retningslinjer
- **Prompts**: Ignorer — deprecated, erstattet av skills
- **Metadata.json**: Ignorer — kun relevant for navikt/copilots web-portal
- **Agenter**: Vurder om vi trenger agenten, eller om en instruction/skill dekker behovet
- **Progressive disclosure**: Instructions bør referere til skills for dypere veiledning

### 4b. Lean-filter

Før adopsjon: still begge spørsmål (se `copilot-instructions.md` → Lean-filter). Konkret, dropp:

- **LLM vet dette fra før**: Playwright-API-snutter, OpenAPI 3 YAML-syntaks, WCAG 2.x-basics, Kotlin/Spring Boot/Ktor-idiomer, React hooks-grunnkurs, SQL-indeksteori, OAuth2/JWT-flyt-beskrivelser, testpyramide-pedagogikk.
- **Generiske tekno-prompts** uten Nav-vinkel.
- **Strukturelle valg fra uvaliderte systemer**: Ikke kopier arkitektur fra upstream-skill kun fordi strukturen er ny.

Behold innhold som binder LLM til Nav-spesifikke gotchas (Nais, Wonderwall, accessPolicy, TokenX, Rapids & Rivers, Aksel, HikariCP-i-containere, team-koordineringspraksis).

### 4c. Betingede råd-regelen

Alle nye skills må formuleres slik at de leser repoets faktiske stack før de gir råd — ikke anta Nav-default som universelt. Eksempel: en `kafka-topic`-skill ber LLM sjekke `build.gradle.kts` for Rapids & Rivers vs plain Kafka og følge eksisterende stil. Migrasjoner mellom stiler skal aldri sneakes inn som del av uavhengige oppgaver.

### 4d. Soft cap 200 linjer for nye SKILL.md

Hold SKILL.md under ~200 linjer. Større innhold → split til `references/`-filer (f.eks. `references/lean-filter.md`, `references/regression-checks.md`) og pek til dem fra SKILL.md. Eat-your-own-dog-food: denne skillen er selv splittet når den passerer taket.

### 4e. Placeholder-regel for sensitive referansefiler

Ingen ekte personopplysninger eller interne detaljer i `references/`:
- Fødselsnummer: bruk `00000000000` (11 nuller).
- Interne kontakter: ingen navn, bruk roller (f.eks. "NAIS-plattformteamet").
- Case-beskrivelser: syntetiske eksempler, ingen reelle saksdetaljer.

### 4f. Regresjonssjekker for upstream-sync

Før PR merges, verifiser at adopterte filer ikke reintroduserer droppede mønstre:

- Ingen `@nais-agent` / `@auth-agent` / `@kafka-agent` / `@nav-pilot`-agent-referanser i adopterte skills (spesialistagentene er avviklet til fordel for skills).
- Ingen nye `actions/*@v<N>`, `@main`, `@master`-eksempler i CI/CD-snutter — SHA-pinning kreves (`actions/checkout@<40-char-sha> # v4.2.2`).
- Ingen ekte fnr, team-medlemsnavn eller case-beskrivelser (se placeholder-regel).

### 4g. Rolle-spill-testing mot begge modeller

Før merge: kjør en realistisk prompt mot både Claude (Opus) og GPT (den consumer-team faktisk bruker i Copilot) for den adopterte skillen. Verifiser at begge:
1. Laster skillen ved forventet trigger.
2. Gir betingede råd (ikke Nav-default antatt).
3. Respekterer lean-filteret (ikke repeterer LLM-kunnskap).

### 4h. Droppeliste (ikke adopter)

- **Spesialistagenter som dupliserer skill-innhold** (f.eks. `@nais-agent` når `nais-deploy`-skillen dekker samme).
- **CI/CD-snutter med usikre pinninger** (`@v4`, `@main`, `@master`).
- **Generiske tekno-prompts** (React-hooks-forklaring, SQL-optimalisering-guide) uten Nav-vinkel.
- **Strukturelle valg fra uvaliderte systemer** — vent til mønsteret er bevist i produksjon et sted.

### 5. Prioriteringsliste

Fokuser på disse kategoriene i denne rekkefølgen:

1. **Sikkerhet** — nye trusselmodeller, oppdaterte mønstre
2. **Plattform** — NAIS-endringer, nye Chainguard images
3. **Observability** — nye metrikkmønstre, logging-standarder
4. **Testing** — nye testrammeverk, oppdaterte mønstre
5. **Framework** — nye Spring Boot/Ktor/Next.js-versjoner og mønstre

### 6. Etter adopsjon

- Oppdater `collections.yml` med nye filer i riktig collection
- Kjør tester: `cd scripts && python3 -m pytest test_sync.py -v`
- Verifiser at sync fungerer: `python3 scripts/sync.py --source . --target /tmp/test-repo --output /tmp/result.json`

## Kjente forskjeller

hovmester er Nav-bredt, men kan avvike fra upstream ved bevisste valg:
- Multi-agent orkestrering med Nav-spesifikke agenter (ikke i navikt/copilot)
- Multi-agent orkestreringsmønster (hovmester → kokk/konditor → inspektører)
- Collections-basert distribusjon (navikt/copilot har flatere struktur)
- Pull-basert sync via GitHub Actions (navikt/copilot bruker lignende mønster)

navikt/copilot har bredere dekning med:
- Flere agenter (auth, research, forfatter, code-review)
- Dypere observability- og sikkerhetsveiledning
- MCP-integrasjon og registrering
- Web-portal for oppdagelse (min-copilot.ansatt.nav.no)
