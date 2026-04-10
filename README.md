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
      collections: "frontend"              # eller "backend", "backend,frontend"
      github_project: "navikt/157"         # valgfritt: bytt til ditt teams GitHub Project, eller fjern linjen
```

Kjør workflowen manuelt første gang via `Actions` → `Sync hovmester` → `Run workflow`. Den oppretter en PR med alle filer klare i `.github/`. Merge → du er i gang.

Dette er nok hvis du vil ha sync-PRer og merge manuelt. Hvis du vil auto-merg'e dem, se [Auto-merge](#auto-merge-valgfritt) lenger ned.

Hvis repoet ditt har required CI-checks på PRer, anbefaler vi også App-oppsettet under. Da opprettes sync-PRer som vanlige PRer og trigger CI normalt.

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
- `"backend"` — backend-repo
- `"frontend"` — frontend-repo
- `"backend,frontend"` — fullstack-repo
- `"hovmester"` — bare orkestratoren og generiske ting (ingen rammeverk-spesifikke skills)

## Konfigurasjon

| Input | Beskrivelse | Påkrevd |
|---|---|---|
| `collections` | Kommaseparert liste over collections. Gyldige valg er `hovmester`, `backend`, `frontend`. `hovmester` er alltid inkludert, så du skriver vanligvis `"backend"`, `"frontend"` eller `"backend,frontend"`. | Ja |
| `exclude` | Kommaseparert liste over konkrete ting som skal utelates fra de valgte collectionene, f.eks. `"kafka-topic,epic"` eller `"task,story"`. | Nei |
| `github_project` | Valgfritt GitHub Project i format `owner/number`, f.eks. `"navikt/123"`. Fjern linjen hvis teamet ikke bruker GitHub Projects. | Nei |
| `pr_app_id` | GitHub App ID for PR-opprettelse. Anbefalt når du bruker auto-merge eller har required CI-checks. | Nei |

| Secret | Beskrivelse |
|---|---|
| `APP_PRIVATE_KEY` | GitHub App private key for PR-opprettelse. Brukes sammen med `pr_app_id`. |

Vanlige valg:

- Backend-repo: `collections: "backend"`
- Frontend-repo: `collections: "frontend"`
- Fullstack-repo: `collections: "backend,frontend"`
- Bare hovmester-oppsettet: `collections: "hovmester"`
- Ingen GitHub Projects: fjern `github_project` helt

### Issue templates

Default-settet er `bug`, `feature`, `story`, `task` og `epic` (pluss `config`). Hvis du vil utelate noen, bruk `exclude: "epic,task"`.

Hvis `github_project` er satt, auto-linkes nye issues til det prosjektet. Hvis ikke, opprettes de uten prosjekttilknytning.

### Auto-merge (valgfritt)

Auto-merge er valgfritt. Hvis du bare vil ha sync-PRer og merge manuelt, kan du stoppe etter **Kom i gang**.

Hvis du vil auto-merg'e sync-PRene, trenger du tre ting:

1. En GitHub App som oppretter PRen
2. En verify-workflow i consumer-repoet
3. Branch protection som krever verify-jobben

| Ønske | Det du trenger |
|---|---|
| Manuell merge | Kun `hovmester-sync.yml` |
| Manuell merge + vanlig CI på sync-PRer | `hovmester-sync.yml` + GitHub App |
| Auto-merge | `hovmester-sync.yml` + GitHub App + `hovmester-verify.yml` |

**Steg 1 — Opprett GitHub App**

Opprett en [GitHub App](https://docs.github.com/en/apps/creating-github-apps) og installer den i consumer-repoet.

Appen trenger:

- **Contents: Read & write**
- **Pull requests: Read & write**

Lagre deretter:

- App ID som repository variable: `HOVMESTER_APP_ID`
- Appens bot-login som repository variable: `HOVMESTER_APP_BOT_LOGIN` (for eksempel `my-sync-app[bot]`)
- Private key som secret: `HOVMESTER_APP_PRIVATE_KEY`

Repoet må også ha dette slått på:

- **Allow auto-merge**
- **Allow squash merging**
- **Settings → Actions → General → Workflow permissions → Allow GitHub Actions to create and approve pull requests**

> **Bot-approval:** Hvis dere bruker branch protection eller CODEOWNERS, må oppsettet tillate at sync-PRer kan godkjennes av `github-actions[bot]`. Sørg også for at `.github/`-stier ikke krever manuell CODEOWNERS-review.

**Steg 2 — Send App-credentials inn i sync-workflowen**

Oppdater sync-workflowen fra **Kom i gang** med disse to linjene:

```yaml
jobs:
  sync:
    uses: navikt/hovmester/.github/workflows/hovmester-sync.yml@main
    with:
      collections: "frontend"
      github_project: "navikt/157"         # valgfritt
      pr_app_id: ${{ vars.HOVMESTER_APP_ID }}
    secrets:
      APP_PRIVATE_KEY: ${{ secrets.HOVMESTER_APP_PRIVATE_KEY }}
```

Da opprettes sync-PRen av Appen i stedet for `github-actions[bot]`. Det gjør to ting:

- vanlige `pull_request`-checks og CI trigges som normalt
- verify-workflowen kan godkjenne PRen med `GITHUB_TOKEN` uten self-approval-konflikt

Hvis du bare trenger at CI skal trigges på sync-PRer, kan du stoppe her og merge manuelt.

**Steg 3 — Legg til verify-workflow**

Legg til `.github/workflows/hovmester-verify.yml` i consumer-repoet:

<details>
<summary>Vis workflow</summary>

```yaml
# Managed by team — do not sync from hovmester.
name: Verify and merge hovmester sync

on:
  pull_request_target:
    types: [opened, synchronize, reopened]

permissions:
  contents: write
  pull-requests: write

jobs:
  verify-and-merge:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - name: Verify file scope
        env:
          GH_TOKEN: ${{ github.token }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
          HEAD_REF: ${{ github.head_ref }}
          HEAD_REPO: ${{ github.event.pull_request.head.repo.full_name }}
          PR_AUTHOR: ${{ github.event.pull_request.user.login }}
          EXPECTED_PR_AUTHOR: ${{ vars.HOVMESTER_APP_BOT_LOGIN }}
          REPO: ${{ github.repository }}
        run: |
          set -euo pipefail

          if [[ "$HEAD_REF" != "hovmester-sync" ]] || [[ "$HEAD_REPO" != "$REPO" ]]; then
            echo "Not a hovmester sync PR — skipping"
            exit 0
          fi

          if [[ -z "$EXPECTED_PR_AUTHOR" ]]; then
            echo "::error::HOVMESTER_APP_BOT_LOGIN must be set"
            exit 1
          fi

          if [[ "$PR_AUTHOR" != "$EXPECTED_PR_AUTHOR" ]]; then
            echo "::error::Unexpected PR author: $PR_AUTHOR"
            echo "Expected PR author: $EXPECTED_PR_AUTHOR"
            exit 1
          fi

          FILES=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}/files" \
            --paginate --jq '.[] | .filename, (.previous_filename // empty)')

          if [ -z "$FILES" ]; then
            echo "::warning::No files found — skipping (possible API issue)"
            exit 1
          fi

          echo "Changed files:"
          echo "$FILES"

          while IFS= read -r file; do
            [[ -z "$file" ]] && continue
            case "$file" in
              .github/agents/*|\
              .github/instructions/*|\
              .github/skills/*|\
              .github/ISSUE_TEMPLATE/*|\
              .github/PULL_REQUEST_TEMPLATE.md|\
              .github/.hovmester-manifest.json|\
              .github/.copilot-kitchen-manifest.json)
                ;;
              *)
                echo "::error::File outside sync scope: $file"
                echo "Only hovmester-managed paths are allowed in sync PRs"
                exit 1
                ;;
            esac
          done <<< "$FILES"

          echo "✅ All files within hovmester sync scope"

      - name: Approve and enable auto-merge
        if: github.head_ref == 'hovmester-sync' && github.event.pull_request.head.repo.full_name == github.repository && github.event.pull_request.user.login == vars.HOVMESTER_APP_BOT_LOGIN
        env:
          GH_TOKEN: ${{ github.token }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
        run: |
          gh pr review "$PR_NUMBER" --approve --body "Auto-approved: file scope verified ✅"
          gh pr merge "$PR_NUMBER" --auto --squash
```

</details>

> `pull_request_target` er trygt her fordi workflowen aldri sjekker ut PR-branchen. Den leser bare filstier via GitHub API og bruker repoets egne workflow-fil fra default branch.

**Steg 4 — Sett branch protection**

Sett `verify-and-merge` som required status check på default branch. Hvis dere krever approvals for å merge, må bot-approval telle for disse PRene.

Første gang: merge `hovmester-verify.yml` til default branch før du aktiverer branch protection, ellers får du en chicken-and-egg-situasjon.

Det er hele oppsettet. Når hovmester lager en sync-PR:

1. PRen opprettes av GitHub Appen
2. Verify-workflowen sjekker at kun hovmester-eide stier er endret
3. `github-actions[bot]` godkjenner PRen
4. GitHub auto-merger når required checks er grønne

**Sikkerhetsmodell**

- Sync-scriptet forvalter bare hovmesters managed paths under `.github/`
- `.github/workflows/` er alltid ekskludert fra sync
- Verify-workflowen eies av consumer-repoet og kan ikke synkes over
- Verify-jobben er den uavhengige gaten som stopper auto-merge hvis PRen inneholder andre filstier enn det hovmester skal eie
- Når du bruker auto-merge, sendes App-credentials inn i reusable workflowen for å opprette PRen som App. Det er et bevisst kompromiss for enklere consumer-oppsett

## Slik fungerer det

Workflowen kjøres på cron (eller manuell trigger), sammenligner ditt repos `.github/`-katalog med den valgte collectionen i hovmester, og oppretter en PR hvis noe har endret seg. Hvis `pr_app_id` + `APP_PRIVATE_KEY` er satt, opprettes PRen av GitHub Appen; ellers brukes `GITHUB_TOKEN`. Manifest-fila `.github/.hovmester-manifest.json` sporer hvilke filer som er "eid" av hovmester så stale filer fjernes automatisk.

Workflowen endrer aldri filer utenfor `.github/`, og `.github/workflows/` er alltid ekskludert — workflows eier du selv.

Synkede filer forvaltes av hovmester — ikke rediger dem manuelt. Lag egne filer for repo-spesifikke tilpasninger.

## Bidra

Se `.github/copilot-instructions.md` for arkitektur, filstruktur, og retningslinjer for å legge til nye agenter, instructions og skills.
