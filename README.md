# hovmester 🍽️

Multi-agent Copilot-orkestrering for Nav-team. Én workflow-innlegging gir repoet ditt en orkestrator (hovmester), en planlegger (souschef), spesialister (kokk/konditor) og kryssmodell-reviewere (inspektører) — pluss Nav-brede instruksjoner, skills og issue-/PR-templates.

## Kom i gang

Legg til denne workflowen i repoet ditt som `.github/workflows/hovmester-sync.yml`:

```yaml
name: Sync hovmester
on:
  schedule:
    - cron: '0 5 * * *'
  workflow_dispatch:

permissions:
  contents: write
  pull-requests: write

jobs:
  sync:
    uses: navikt/hovmester/.github/workflows/hovmester-sync.yml@main
    with:
      collections: "hovmester,frontend"    # eller "hovmester,backend", "hovmester,backend,frontend"
      github_project: "navikt/157"         # bytt til ditt teams prosjekt-URL
      automerge_app_id: "2906300"          # bytt til din GitHub App ID (valgfritt — se Auto-merge)
    secrets:
      APP_PRIVATE_KEY: ${{ secrets.AUTOMERGE_APP_PRIVATE_KEY }}  # valgfritt — se Auto-merge
```

Kjør workflowen manuelt første gang via `Actions` → `Sync hovmester` → `Run workflow`. Den oppretter en PR med alle filer klare i `.github/`. Merge → du er i gang.

## Hva du får

Bruk **@hovmester** som inngang til alt — den koordinerer planlegging, implementasjon og kodegjennomgang automatisk.

```
                        ┌─────────────┐
                        │  Hovmester  │ Orkestrator (Opus)
                        │     🍽️      │ Tar imot bestillingen
                        └──────┬──────┘
                               │
                    ┌──────────┼──────────┐
                    ▼                     ▼
             ┌────────────┐        ┌────────────┐
             │  Souschef  │        │ Brainstorm  │
             │     📋     │        │     💡      │
             │ Planlegger │        │ Utforsker   │
             │   (Opus)   │        │   (skill)   │
             └─────┬──────┘        └─────────────┘
                   │
          ┌────────┴────────┐
          ▼                 ▼
   ┌────────────┐    ┌────────────┐
   │    Kokk    │    │  Konditor  │
   │    👨‍🍳     │    │     🎂     │
   │  Backend   │    │  Frontend  │
   │   (GPT)    │    │   (Opus)   │
   └─────┬──────┘    └──────┬─────┘
         │                  │
         └────────┬─────────┘
                  ▼
   ┌──────────────────────────┐
   │  Kryssmodell-inspeksjon  │
   │         🔍 🔍            │
   │ Claude inspects GPT work │
   │ GPT inspects Opus work   │
   └──────────┬───────────────┘
              ▼
       ┌────────────┐
       │  Hovmester  │
       │ konsoliderer│
       │ 😊 😐 😞   │
       └────────────┘
```

| Agent | Rolle | Modell |
|-------|-------|--------|
| **@hovmester** 🍽️ | Orkestrator — tar imot bestillingen, delegerer, konsoliderer inspeksjon | Opus |
| **@kokk** 👨‍🍳 | Backend — API, tjenester, database, Kafka, infrastruktur | GPT |
| **@konditor** 🎂 | Frontend — UI, Aksel, tilgjengelighet, state | Opus |
| *@souschef* 📋 | *(internt)* Planlegger — lager implementasjonsplaner | Opus |
| *@inspektør-claude* 🔬 | *(internt)* Kryssmodell-reviewer for GPT-arbeid | Opus |
| *@inspektør-gpt* 🔬 | *(internt)* Kryssmodell-reviewer for Opus-arbeid | GPT |

> Oppgaver delegeres som vertikale funksjonssnitt — én agent eier hele funksjonen. Kryssmodell-review fanger blindsoner: Opus gjennomgår GPT-kode, GPT gjennomgår Opus-kode.

## Collections

| Collection | Innhold |
|---|---|
| `hovmester` (alltid inkludert) | 6 agenter, 3 Nav-brede instructions, 10 generiske skills, issue templates, PR-mal |
| `backend` | Kotlin instruction + 7 backend-skills (Ktor, Spring, Flyway, Kafka, Postgres, API-design, auth) |
| `frontend` | Frontend og accessibility instructions + 3 frontend-skills (Aksel, auth, Lumi) |

**Eksempler:**
- `"hovmester,backend"` — backend-repo
- `"hovmester,frontend"` — frontend-repo
- `"hovmester,backend,frontend"` — fullstack-repo
- `"hovmester"` — bare orkestratoren og generiske ting (ingen rammeverk-spesifikke skills)

## Konfigurasjon

| Input | Beskrivelse | Påkrevd |
|---|---|---|
| `collections` | Kommaseparerte collections (f.eks. `"hovmester,backend"`) | Ja |
| `exclude` | Kommaseparert liste over items som skal utelates (f.eks. `"kafka-topic,epic"`) | Nei |
| `github_project` | GitHub-prosjekt for auto-linking av nye issues (f.eks. `"navikt/123"`). Hvis tom, fjernes `projects`-feltet fra issue-templatene. | Nei |
| `automerge_app_id` | GitHub App ID for auto-merge. Må være satt sammen med `APP_PRIVATE_KEY` secret. | Nei |

| Secret | Beskrivelse |
|---|---|
| `APP_PRIVATE_KEY` | Privatnøkkel for GitHub App som gir auto-merge. |

### Issue templates

Default-settet er `bug`, `feature`, `story`, `task` og `epic` (pluss `config`). Hvis du vil utelate noen, bruk `exclude: "epic,task"`.

Hvis `github_project` er satt, auto-linkes nye issues til det prosjektet. Hvis ikke, opprettes de uten prosjekttilknytning.

### Auto-merge

Auto-merge krever to ting:
1. En GitHub App installert på repoet ditt (med `contents: write` og `pull-requests: write`)
2. Både `automerge_app_id`-input OG `APP_PRIVATE_KEY`-secret

Uten begge deler opprettes PRen som vanlig og må merges manuelt.

## Eksempler

### Backend-repo med auto-merge

```yaml
jobs:
  sync:
    uses: navikt/hovmester/.github/workflows/hovmester-sync.yml@main
    with:
      collections: "hovmester,backend"
      github_project: "navikt/157"         # bytt til ditt teams prosjekt-URL
      automerge_app_id: "2906300"          # bytt til din GitHub App ID
    secrets:
      APP_PRIVATE_KEY: ${{ secrets.AUTOMERGE_APP_PRIVATE_KEY }}
```

### Fullstack uten auto-merge, utelater Kafka

```yaml
jobs:
  sync:
    uses: navikt/hovmester/.github/workflows/hovmester-sync.yml@main
    with:
      collections: "hovmester,backend,frontend"
      exclude: "kafka-topic"
      github_project: "navikt/157"         # bytt til ditt teams prosjekt-URL
```

### Minimal — bare hovmester, ingen templates, manuell merge

```yaml
jobs:
  sync:
    uses: navikt/hovmester/.github/workflows/hovmester-sync.yml@main
    with:
      collections: "hovmester"
      exclude: "bug,feature,story,task,epic"
```

## Slik fungerer det

Workflowen kjøres på cron (eller manuell trigger), sammenligner ditt repos `.github/`-katalog med den valgte collectionen i hovmester, og oppretter en PR hvis noe har endret seg. Manifest-fila `.github/.hovmester-manifest.json` sporer hvilke filer som er "eid" av hovmester så stale filer fjernes automatisk.

Workflowen endrer aldri filer utenfor `.github/`, og `.github/workflows/` er alltid ekskludert — workflows eier du selv.

Synkede filer forvaltes av hovmester — ikke rediger dem manuelt. Lag egne filer for repo-spesifikke tilpasninger.

## Bidra

Se `.github/copilot-instructions.md` for arkitektur, filstruktur, og retningslinjer for å legge til nye agenter, instructions og skills.
