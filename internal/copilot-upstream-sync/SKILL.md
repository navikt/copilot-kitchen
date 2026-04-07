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
| Er det relevant for Team eSyfos stack? | Gå videre | Hopp over |
| Er det generelt nok for alle team-repos? | Legg i `common` | Legg i `backend`/`frontend` |
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

copilot-kitchen er tilpasset Team eSyfo og har:
- Team-spesifikke gjenbrukbare workflows (teamesyfo-github-actions-workflows)
- Multi-agent orkestreringsmønster (hovmester → kokk/konditor → inspektører)
- Collections-basert distribusjon (navikt/copilot har flatere struktur)
- Pull-basert sync via GitHub Actions (navikt/copilot bruker lignende mønster)

navikt/copilot har bredere dekning med:
- Flere agenter (auth, research, forfatter, code-review)
- Dypere observability- og sikkerhetsveiledning
- MCP-integrasjon og registrering
- Web-portal for oppdagelse (min-copilot.ansatt.nav.no)
