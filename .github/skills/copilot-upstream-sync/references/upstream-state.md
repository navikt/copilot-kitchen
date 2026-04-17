# Upstream-sync state

Siste sjekket commit i `navikt/copilot` og hva som ble gjort.

## Siste sync

| Felt | Verdi |
|------|-------|
| SHA | `846302604b2da5ed06d64ef1258b5ed0cf032a42` |
| Dato | 2026-04-17 |
| Sjekket til og med | Alle commits t.o.m. 2026-04-17 |

## Adoptert

- **Aksel llm.md-referanse** — aksel-design og figma-workflow peker nå til `aksel.nav.no/llm.md` for live docs
- **Aksel v8-regler** — Alert deprecated, Button danger→data-color, borderRadius numerisk, CSS-prefix `.aksel-`
- **accessibility.instructions.md** — Alert→LocalAlert i ARIA-eksempel

## Vurdert og droppet

| Commit | Hva | Grunn |
|--------|-----|-------|
| `f5da16a7` | Ktor/Spring-rebalansering (transaction patterns, DI-reframing) | Relevant, men eget arbeid — oppfølgingsissue opprettet |
| `ba5bb16f` | HikariCP 40→5 | Allerede dekket — hovmester sier 3-5 i postgresql-review, kotlin-spring og nais-manifest |
| `b7e67ec3` | my-copilot hero-kodeeksempler | Intern portal — ikke relevant |
| `43414879` | forfatter guardrails | Forfatter-agent — ikke relevant |
| `7a5150a4` | april 2026 nyheter | Docs/news — ikke relevant |
| `961f8a49` | agentskills.io / gh skill install | nav-pilot tooling — ikke relevant |
| `d23d36fc`–`828261d6` | nav-pilot, my-copilot, news | Intern tooling og portal — ikke relevant |
