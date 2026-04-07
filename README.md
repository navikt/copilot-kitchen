# copilot-kitchen

Copilot customization files (agents, skills, instructions) distributed via a reusable GitHub Actions workflow.

## Quick start

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
      collections: "common,backend"  # Or "common,frontend", or omit for all
    secrets:
      APP_PRIVATE_KEY: ${{ secrets.AUTOMERGE_APP_PRIVATE_KEY }}  # Optional: enables auto-merge
    permissions:
      contents: write
      pull-requests: write
```

Run manually: `Actions` > `Copilot Config Sync` > `Run workflow`.

**With `APP_PRIVATE_KEY`:** PR is created, approved, and queued for merge automatically.
**Without:** PR is created but requires manual review and merge.

## Collections

| Collection | Content |
|---|---|
| `common` | Agents, security instructions, docker, github-actions, nais-manifest, observability-setup, and process skills. Always included. |
| `backend` | Kotlin instructions + backend skills (api-design, kafka-topic, flyway-migration, etc.) |
| `frontend` | Frontend skills (aksel-design, accessibility, lumi-survey, etc.) |

Examples:
- `collections: "common,backend"` — backend repo
- `collections: "common,frontend"` — frontend repo
- `collections: "common,backend,frontend"` — fullstack repo
- Omit `collections` — get all files

### Exclude

```yaml
exclude: "tech-stack,kafka-topic"  # Skip these regardless of collections
```

## What gets synced

- **Agents** — Multi-agent orchestration pipeline (hovmester, souschef, kokk, konditor, mattilsynet, inspektorer)
- **Skills** — 23 on-demand skills (lazy-loaded by Copilot CLI)
- **Instructions** — Minimal always-loaded guidance (security, kotlin)
- **Issue templates** and **PR template**

## Auto-merge

Requires `AUTOMERGE_APP_PRIVATE_KEY` as an **Actions secret** (not Dependabot secret). The workflow uses three tokens:

1. **App token** creates the PR (triggers build via push event)
2. **GITHUB_TOKEN** approves the PR (different actor than the app)
3. **App token** enables auto-merge (triggers merge queue)

This is the same constraint Dependabot faces — no single token can do all three.

## Migrating from esyfo-cli

1. Add the workflow above and run manually
2. First sync overwrites old files and cleans up legacy `Managed by esyfo-cli` files
3. Delete `.github/workflows/copilot-config-auto-approve.yml` (no longer needed)
4. Add `AUTOMERGE_APP_PRIVATE_KEY` as Actions secret for auto-merge

## How it works

1. Shallow-clones this repo
2. Resolves files from collections (or all if not specified)
3. Compares SHA-256 hashes, copies changed/new files, removes stale via manifest
4. Creates or updates PR on `copilot-config-sync` branch
5. (If secret provided) Approves and queues for merge
