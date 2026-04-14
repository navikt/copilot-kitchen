# hovmester

Distribusjonsrepo for GitHub Copilot-tilpasninger (agenter, instructions, skills) til Nav-teamenes repositories via GitHub Actions.

## Arkitektur

### Pull-basert sync
Consumer-repos kaller en reusable workflow (`hovmester-sync.yml`) som shallow-kloner dette repoet, kjører `scripts/sync.py`, og oppretter PR med endringer. Konfigurasjon via workflow-inputs (`collections`, `exclude`, `github_project`) og valgfri App-auth for PR-opprettelse (`pr_app_id` + `APP_PRIVATE_KEY`). Auto-merge er consumer-eid via en egen verify-workflow.

### Filstruktur

```
dist/                  (alt som synkes til consumer-repos)
  agents/              → .github/agents/
  instructions/        → .github/instructions/
  skills/              → .github/skills/
  issue-templates/     → .github/ISSUE_TEMPLATE/
.github/               (dette repoets egen Copilot-konfig, synkes IKKE)
  copilot-instructions.md
  skills/              (repo-lokale skills)
scripts/               (sync-verktøy, synkes ikke)
```

### Collections
`collections.yml` grupperer filer i navngitte samlinger (`hovmester`, `backend`, `frontend`). `hovmester` inkluderes alltid implisitt og bundler agenter, Nav-brede instruksjoner, generiske skills og standard issue templates. Consumer-repos velger samlinger og kan ekskludere enkeltfiler med `exclude`-input.

## Instruction vs Skill — når bruke hva

### Instructions (`instructions/*.instructions.md`)
Persistent bakgrunnskontekst som auto-lastes basert på `applyTo`-glob. Bruk for:
- Regler som **alltid** skal gjelde for en filtype (sikkerhet, kodestandarder, konvensjoner)
- Eksempel: `docker.instructions.md` med `applyTo: "**/Dockerfile*"` — Dockerfile-regler gjelder automatisk

```yaml
---
description: "Kort beskrivelse"
applyTo: "mønster"
---
```

### Skills (`skills/<navn>/SKILL.md`)
On-demand kunnskapsmoduler som lastes eksplisitt av bruker eller agent. Bruk for:
- Oppgave-spesifikk veiledning (generering, review, oppsett)
- Detaljerte workflows med steg-for-steg
- Innhold som kun er relevant i spesifikke situasjoner
- Kan ha `references/`-undermappe med støttefiler

```yaml
---
name: skill-navn
description: "Kort beskrivelse — brukes til agent-discovery"
---
```

### Progressive disclosure
Instructions kan referere til skills for dypere veiledning. Eksempel: `kotlin.instructions.md` dekker generelle Kotlin-regler og peker til `kotlin-spring` og `kotlin-ktor`-skills for framework-spesifikke mønstre.

### Prompts — deprecated
`.github/prompts/*.prompt.md` er erstattet av skills. Ikke distribuer prompts.

## Lean-filter for skill- og instruction-innhold

Alt distribuert innhold skal bestå lean-filteret:

1. **Kan modellen (Claude/GPT) dette fra før?** Eksempler som droppes: Playwright-API, OpenAPI-syntaks, WCAG-basics, Kotlin/Spring/Ktor-syntaks, React, SQL-indeksering, OAuth2/JWT-mekanikk, testpyramide-terminologi.
2. **Lærer det å jobbe i Nav, eller styrker det agenten på annen måte?** Eksempler som beholdes: Nais, Wonderwall, accessPolicy, TokenX, Rapids & Rivers, Aksel, HikariCP-i-containere, Nav-team-koordinering.

Drop hvis ja på 1 og nei på 2. Hold teknologiagnostisk der mulig.

## Betingede råd (respekter eksisterende stack)

Skills skal gi betingede råd basert på hva repoet faktisk bruker, ikke anta at Nav-mønstre er universelle. Eksempel: `kafka-topic` skal detektere om repoet bruker Rapids & Rivers eller plain Kafka, og følge eksisterende stil. Ikke foreslå migrasjon mellom stiler som del av uavhengige oppgaver. LLM kan lese `build.gradle.kts` / `pom.xml` / konfig-filer; skrivereglen er at skills ber den gjøre det.

## Konvensjoner

### Navngivning i collections.yml
Bruk kortnavn uten filendelse: `hovmester` (ikke `hovmester.agent.md`), `security` (ikke `security.instructions.md`), `brainstorm` (ikke `brainstorm/SKILL.md`).

### Innholdsstruktur
- Kodeeksempler over prosa — vis ✅ riktig og ❌ feil
- Grenser-seksjon med tre nivåer: Alltid / Spør først / Aldri
- Referanser til offisielle Nav-ressurser (sikkerhet.nav.no, aksel.nav.no)
- Norsk innhold i instruksjoner/skills (teamets arbeidsspråk)

### Manifest og cleanup
Sync-scriptet skriver `.hovmester-manifest.json` i target-repo for å spore synkede filer. Stale filer fjernes automatisk. Consumer-repoer skal ikke redigere synkede filer. Repoer som tidligere brukte `.copilot-kitchen-manifest.json` migreres automatisk til det nye navnet ved første sync.

## Kommandoer

```bash
# Kjør tester
cd scripts && python3 -m pytest test_sync.py -v

# Test sync lokalt (dry-run mot et repo)
python3 scripts/sync.py --source . --target /path/to/repo --output /tmp/result.json

# Med collections
python3 scripts/sync.py --source . --target /path/to/repo --output /tmp/result.json --collections "hovmester,backend"
```

## Upstream-referanse

Hovmester vedlikeholdes Nav-bredt, men sjekker jevnlig `navikt/copilot` for nye mønstre, instruksjoner og skills som er verdt å adoptere. Se `.github/skills/copilot-upstream-sync/SKILL.md` for strukturert gjennomgang (ligger i `.github/skills/`, ikke `dist/skills/`, så den synkes ikke til consumer-repos).
