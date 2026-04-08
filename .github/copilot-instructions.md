# copilot-kitchen

Distribusjonsrepo for GitHub Copilot-tilpasninger (agenter, instructions, skills) til Team eSyfos repositories via GitHub Actions.

## Arkitektur

### Pull-basert sync
Consumer-repos kaller en reusable workflow (`copilot-sync.yml`) som shallow-kloner dette repoet, kjører `scripts/sync.py`, og oppretter PR med endringer. Konfigurasjon via workflow-inputs (`collections`, `exclude`).

### Filstruktur

```
agents/           → .github/agents/        (alltid-tilgjengelige agentprofiler)
instructions/     → .github/instructions/  (auto-loaded basert på applyTo-mønster)
skills/           → .github/skills/        (on-demand, eksplisitt invokert)
issue-templates/  → .github/ISSUE_TEMPLATE/
scripts/          (sync-logikk, ikke distribuert)
```

### Collections
`collections.yml` grupperer filer i navngitte samlinger (`common`, `backend`, `frontend`). `common` inkluderes alltid implisitt. Consumer-repos velger samlinger og kan ekskludere enkeltfiler.

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

## Konvensjoner

### Navngivning i collections.yml
Bruk kortnavn uten filendelse: `hovmester` (ikke `hovmester.agent.md`), `security` (ikke `security.instructions.md`), `brainstorm` (ikke `brainstorm/SKILL.md`).

### Innholdsstruktur
- Kodeeksempler over prosa — vis ✅ riktig og ❌ feil
- Grenser-seksjon med tre nivåer: Alltid / Spør først / Aldri
- Referanser til offisielle Nav-ressurser (sikkerhet.nav.no, aksel.nav.no)
- Norsk innhold i instruksjoner/skills (teamets arbeidsspråk)

### Manifest og cleanup
Sync-scriptet skriver `.copilot-kitchen-manifest.json` i target-repo for å spore synkede filer. Stale filer fjernes automatisk. Consumer-repoer skal ikke redigere synkede filer — lag egne filer uten managed header.

## Kommandoer

```bash
# Kjør tester
cd scripts && python3 -m pytest test_sync.py -v

# Test sync lokalt (dry-run mot et repo)
python3 scripts/sync.py --source . --target /path/to/repo --output /tmp/result.json

# Med collections
python3 scripts/sync.py --source . --target /path/to/repo --output /tmp/result.json --collections "common,backend"
```

## Upstream-referanse

Team eSyfo vedlikeholder copilot-kitchen uavhengig, men sjekker jevnlig `navikt/copilot` for nye mønstre, instruksjoner og skills som er verdt å adoptere. Se `internal/copilot-upstream-sync/SKILL.md` for strukturert gjennomgang (denne filen synkes ikke til consumer-repos).
