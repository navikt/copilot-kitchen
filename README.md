# copilot-kitchen

Distribuerer Copilot-tilpasninger (agenter, skills, instructions) til teamets repoer via GitHub Actions.

## Kom i gang

Legg til workflowen i repoet ditt:

```yaml
# .github/workflows/copilot-sync.yml
name: Copilot Config Sync
on:
  schedule:
    - cron: '0 5 * * *'
  workflow_dispatch:
jobs:
  sync:
    uses: navikt/copilot-kitchen/.github/workflows/copilot-sync.yml@main
    with:
      collections: "common,backend"   # Eller "common,frontend", eller utelat for alt
      # exclude: "tech-stack"         # Valgfritt — hopp over enkeltfiler
    secrets:
      APP_PRIVATE_KEY: ${{ secrets.AUTOMERGE_APP_PRIVATE_KEY }}  # Valgfritt — gir auto-merge
    permissions:
      contents: write
      pull-requests: write
```

Kjør manuelt: `Actions` > `Copilot Config Sync` > `Run workflow`.

**Med `APP_PRIVATE_KEY`:** PR opprettes, godkjennes og merges automatisk.
**Uten:** PR opprettes, men krever manuell review og merge.

## Collections

| Collection | Instructions | Skills |
|---|---|---|
| `common` (alltid inkludert) | security, docker, github-actions | brainstorm, conventional-commit, grill-me, nais-manifest, observability-setup, issue-management, klarsprak, pull-request, security-review, tdd, tech-stack |
| `backend` | kotlin | api-design, auth-overview, flyway-migration, kafka-topic, kotlin-ktor, kotlin-spring, postgresql-review |
| `frontend` | accessibility | aksel-design, auth-overview, lumi-survey |

Alle collections inkluderer også 7 agenter, 6 issue-maler og PR-mal.

Eksempler:
- `["backend"]` — backend-repo (common inkluderes automatisk)
- `["frontend"]` — frontend-repo
- `["backend", "frontend"]` — fullstack-repo
- Utelat — alle filer synkes

## Hva som synkes

```
agents/           → .github/agents/         (7 agenter, multi-agent-pipeline)
instructions/     → .github/instructions/   (auto-lastes basert på applyTo-mønster)
skills/           → .github/skills/         (on-demand, lastes ved behov)
issue-templates/  → .github/ISSUE_TEMPLATE/
PULL_REQUEST_TEMPLATE.md → .github/PULL_REQUEST_TEMPLATE.md
```

### Instructions vs skills

**Instructions** lastes automatisk når du redigerer matchende filer:
- `security.instructions.md` → alle filer
- `docker.instructions.md` → Dockerfiler
- `github-actions.instructions.md` → workflow-filer
- `kotlin.instructions.md` → Kotlin-filer (refererer til kotlin-spring/ktor-skills)
- `accessibility.instructions.md` → React-komponenter

**Skills** lastes on-demand for spesifikke oppgaver — detaljert veiledning, generering eller review.

## Auto-merge

Krever `AUTOMERGE_APP_PRIVATE_KEY` som **Actions secret** (ikke Dependabot secret). Workflowen bruker tre tokens:

1. **App-token** oppretter PR (trigger build via push)
2. **GITHUB_TOKEN** godkjenner PR (annen aktør enn appen)
3. **App-token** aktiverer auto-merge (trigger merge queue)

Samme begrensning som Dependabot — ingen enkelt-token kan gjøre alle tre.

## Migrering fra esyfo-cli

1. Legg til workflowen over og kjør manuelt
2. Første sync overskriver gamle filer og rydder opp `Managed by esyfo-cli`-filer
3. Slett `.github/workflows/copilot-config-auto-approve.yml` (ikke lenger nødvendig)
4. Legg til `AUTOMERGE_APP_PRIVATE_KEY` som Actions secret

## Slik fungerer det

1. Kloner dette repoet (shallow)
2. Velger filer basert på collections (eller alle hvis ikke spesifisert)
4. Sammenligner SHA-256-hasher, kopierer endrede filer, fjerner utdaterte via manifest
5. Oppretter eller oppdaterer PR på `copilot-config-sync`-branch
6. Godkjenner og merger automatisk (hvis secret er konfigurert)
