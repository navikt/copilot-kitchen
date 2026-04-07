# Projects V2 felthåndtering

## Automatisk prosjekttilknytning via templates

Issue-templates i `.github/ISSUE_TEMPLATE/` har `projects: ["navikt/157"]` som automatisk legger nye issues i Team eSyfo-prosjektet når de opprettes via web UI. En prosjekt-workflow setter deretter Status til **Backlog** automatisk (kun issues, ikke PRs). Ved programmatisk opprettelse (API, CLI, MCP) må prosjektet settes manuelt — se under.

## MCP (primær)

Bruk MCP `projects_write` først for å legge issues i prosjekt og oppdatere felter.

- Krever at `projects`-toolset er aktivert
- Team eSyfo-kontekst: `owner=navikt`, prosjekt: **Team eSyfo**
- Standardverdier som brukes i prosjektet:
  - **Statuser:** `Backlog`, `Plukk meg! 🙌`, `Jeg jobbes med! ⚒️`, `Monday epics 🎯`, `Done`
  - **Typer:** `Bug`, `Epic`, `Feature`, `Story`, `Task`

## Fallback (gh project)

Når MCP ikke er tilgjengelig, bruk `gh project`-kommandoer.

### Komplett workflow

1. Finn prosjektnummer
```bash
gh project list --owner navikt --format json
```

2. Hent field-IDs og option-IDs
```bash
gh project field-list N --owner navikt --format json
```

3. Legg issue inn i prosjektet
```bash
gh project item-add N --owner navikt --url ISSUE_URL --format json
```

4. Sett felt (single select)
```bash
gh project item-edit \
  --id ITEM_ID \
  --field-id FIELD_ID \
  --project-id PROJECT_ID \
  --single-select-option-id OPTION_ID
```

### Notat

`FIELD_ID` og `OPTION_ID` er stabile over tid og kan caches for raskere operasjoner.

### Token scopes

`gh project`-kommandoer krever at tokenet har `read:project` (les) og `project` (skriv) scopes. Hvis du får tilgangsfeil:

```bash
gh auth refresh -s read:project,project
```
