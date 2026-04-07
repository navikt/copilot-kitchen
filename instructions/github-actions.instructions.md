---
description: "GitHub Actions CI/CD-standarder — SHA-pinning, Nais deploy, sikkerhet og Team eSyfos gjenbrukbare workflows"
applyTo: ".github/workflows/**"
---

# GitHub Actions — Team eSyfo

Standarder for CI/CD-workflows med GitHub Actions på Nais.

## Team eSyfos gjenbrukbare workflows

Team eSyfo har et felles repo med gjenbrukbare workflows: [`navikt/teamesyfo-github-actions-workflows`](https://github.com/navikt/teamesyfo-github-actions-workflows)

### Tilgjengelige workflows

| Workflow | Bruksområde |
|----------|-------------|
| `boot-jar-app.yaml` | Spring Boot / Ktor backend (JAR) |
| `jar-app.yaml` | Generisk JAR-app |
| `fss-boot-jar-app.yaml` | FSS Spring Boot-app |
| `next-app-v2.yaml` | Next.js frontend |
| `next-app.yaml` | Next.js frontend (legacy) |
| `vite-mikrofrontend.yaml` | Vite-basert mikrofrontend |
| `dependabot-automerge.yaml` | Auto-merge Dependabot PR-er |
| `merge-dependabot-pr.yaml` | Merge Dependabot PR |
| `label-dependabot-pr.yaml` | Label Dependabot PR |

### Tilgjengelige actions (composite)

| Action | Bruksområde |
|--------|-------------|
| `boot-jar-to-docker` | Bygg Spring Boot JAR → Docker image |
| `jar-to-docker` | Bygg JAR → Docker image |
| `build-next-app` | Bygg Next.js-app |
| `next-to-docker` | Next.js → Docker image |
| `gradle-cached` | Gradle-bygg med caching |
| `npm-cached` | npm install med caching |
| `setup-pnpm` | pnpm-oppsett |
| `playwright-e2e` | Playwright E2E-tester |

### Bruk i workflow

```yaml
jobs:
  build-and-deploy:
    uses: navikt/teamesyfo-github-actions-workflows/.github/workflows/boot-jar-app.yaml@main
    secrets: inherit
```

**Sjekk alltid repoet for oppdatert dokumentasjon og tilgjengelige inputs.**

## Action Pinning

Pin alle actions til full commit SHA:

```yaml
# ✅ Pinnet til SHA
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
- uses: nais/deploy/actions/deploy@bf80eb8dba46797adb4909901e629bca8595a027 # v2

# ❌ Upinnet tag kan kompromitteres
- uses: actions/checkout@v4
```

> **Unntak**: `nais/*`-actions (f.eks. `nais/docker-build-push`, `nais/deploy`) er interne Nav-actions som bruker stabile semver-tags. Disse trenger ikke SHA-pinning, men bør ha versjonskommentar.

## Minimale tilganger

```yaml
permissions:
  contents: read
  id-token: write

# ❌ Aldri
permissions: write-all
```

## Nais Deploy

```yaml
name: Build and deploy
on:
  push:
    branches: [main]

permissions:
  contents: read
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image: ${{ steps.docker-build-push.outputs.image }}
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
      - uses: nais/docker-build-push@v0
        id: docker-build-push
        with:
          team: team-esyfo

  deploy-dev:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
      - uses: nais/deploy/actions/deploy@v2
        env:
          CLUSTER: dev-gcp
          RESOURCE: .nais/nais.yaml
          VAR: image=${{ needs.build.outputs.image }}

  deploy-prod:
    needs: [build, deploy-dev]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
      - uses: nais/deploy/actions/deploy@v2
        env:
          CLUSTER: prod-gcp
          RESOURCE: .nais/nais.yaml
          VAR: image=${{ needs.build.outputs.image }}
```

## Caching

```yaml
# Gradle
- uses: actions/setup-java@v4 # erstatt med SHA i produksjon
  with:
    distribution: temurin
    java-version: 21
    cache: gradle

# Node/pnpm
- uses: actions/setup-node@v4 # erstatt med SHA i produksjon
  with:
    node-version: 22
    cache: pnpm
```

## Sikkerhet

```yaml
# Concurrency — unngå parallelle deploys
concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: true

# Timeout
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 15

# Scanning
- uses: aquasecurity/trivy-action@0.28.0 # pin SHA
  with:
    scan-type: fs
    severity: HIGH,CRITICAL
    exit-code: 1

# GitHub Actions security scanning
- run: pipx run zizmor .github/workflows/
```

## Grenser

### Alltid
- Pin actions til SHA med kommentar for versjon
- Sett eksplisitte `permissions` per job
- Bruk `timeout-minutes` på alle jobs
- Bruk `concurrency` for deploy-workflows
- Sjekk teamesyfo-github-actions-workflows for gjenbrukbare workflows før du skriver egen

### Spør først
- Nye secrets eller environment variables
- Endringer i deploy-rekkefølge (dev → prod)
- Nye gjenbrukbare workflows

### Aldri
- `permissions: write-all`
- Upinnede 3rd-party action-versjoner uten SHA (unntak: `nais/*`-actions)
- Logg secrets i workflow-output
- `pull_request_target` med `actions/checkout` av PR-branch (code injection)
