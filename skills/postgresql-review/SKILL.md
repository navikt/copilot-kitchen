---
name: postgresql-review
description: PostgreSQL-gjennomgang — EXPLAIN ANALYZE, indekser, N+1-deteksjon, ytelsesproblemer og Flyway-migrasjoner
---
# PostgreSQL-gjennomgang

Gjennomgang av PostgreSQL-bruk i Nav-applikasjoner. Dekker spørringsoptimalisering, indeksering, anti-mønstre og migrasjoner.

Se [references/sql-patterns.md](references/sql-patterns.md) for alle kodeeksempler.

## EXPLAIN-analyse

Kjør alltid `EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)` på tunge spørringer. Se etter Seq Scan på store tabeller, Nested Loop med høye rader (N+1), Sort med external merge, og høy «Buffers shared read».

Se [references/sql-patterns.md](references/sql-patterns.md) for EXPLAIN-eksempler.

## Indeksstrategier

Opprett indekser på kolonner brukt i WHERE, JOIN og ORDER BY. Bruk partial indexes for vanlige filtre, covering indexes for å unngå table lookup, og GIN-indekser for JSONB. Unngå indekser på kolonner med lav kardinalitet.

Se [references/sql-patterns.md](references/sql-patterns.md) for indekseksempler.

## CONCURRENTLY-indekser i produksjon

For `CREATE INDEX CONCURRENTLY` i produksjon, se `flyway-migration`-skillen. Kort oppsummert: bruk egen migrering utenfor transaksjon for å unngå å blokkere skriving.

Se [references/migration-flyway.md](references/migration-flyway.md) for CONCURRENTLY-eksempler.

## JSONB-mønstre

Bruk `@>` containment-operator med GIN-indeks for JSONB-spørringer. Bruk `->>`-operator for spesifikke nøkkeloppslag. Unngå funksjonsbaserte spørringer uten dedikert indeks.

Se [references/sql-patterns.md](references/sql-patterns.md) for JSONB-eksempler.

## Vindusfunksjoner

Bruk window functions (ROW_NUMBER, LAG/LEAD, SUM OVER) for rangering, differanser og akkumulerte verdier uten å falle tilbake til tunge subqueries i applikasjonslaget.

Se [references/sql-patterns.md](references/sql-patterns.md) for vindusfunksjonseksempler.

## CTE (Common Table Expressions)

Bruk CTE-er for lesbarhet og stegvis transformasjon av kompleks logikk. Verifiser med `EXPLAIN ANALYZE` hvis du bruker mange CTE-er i tunge spørringer.

Se [references/sql-patterns.md](references/sql-patterns.md) for CTE-eksempler.

## Upsert / ON CONFLICT

Bruk `ON CONFLICT` når domenet tåler deterministisk deduplisering. Kontroller at konfliktmålet samsvarer med en faktisk `UNIQUE`-constraint eller unik indeks. Bruk batch inserts der mulig.

Se [references/sql-patterns.md](references/sql-patterns.md) for upsert-eksempler.

## CHECK og UNIQUE constraints

Legg domeneregler i databasen når de alltid må gjelde. Constraints beskytter både applikasjonskode, batch-jobber og manuelle scripts.

Se [references/sql-patterns.md](references/sql-patterns.md) for constraint-eksempler.

## Advisory locks

Bruk advisory locks for koordinerte jobber, singleton-prosesser eller idempotente batcher. De erstatter ikke vanlige radlåser eller gode transaksjonsgrenser.

Se [references/sql-patterns.md](references/sql-patterns.md) for advisory lock-eksempler.

## Partisjonering

Bruk `RANGE` for tidsbaserte tabeller og `LIST` når data naturlig deles på for eksempel tenant eller type. Hold omtalen kort i gjennomgangen, og spør først før du introduserer partisjonering i et eksisterende skjema.

Se [references/sql-patterns.md](references/sql-patterns.md) for partisjoneringseksempler.

## Anti-mønstre

### N+1-spørringer
Unngå N+1 ved å bruke batch-henting (`findBySakIdIn`) i stedet for én spørring per rad.

### SELECT *
Hent kun kolonnene du trenger — unngå `SELECT *` i produksjonskode.

### Manglende LIMIT
Begrens resultatsett med `LIMIT` på spørringer som kan returnere mange rader.

Se [references/sql-patterns.md](references/sql-patterns.md) for anti-mønster-eksempler.

## Tilkoblingspool

Konfigurer HikariCP med lav `maximumPoolSize` (start med 5) og juster ved behov. Sett opp SQL-instans via Nais-manifest.

Se [references/sql-patterns.md](references/sql-patterns.md) for tilkoblingspool-eksempler.

## Migrasjoner

For Flyway-migrasjoner og SQL-konvensjoner, se `flyway-migration`-skillen. Nøkkelpunkter:
- Bruk `TIMESTAMPTZ` (ikke `TIMESTAMP`) for alle tidsstempel-kolonner
- Indekser på alle FK-kolonner
- UUID-primærnøkler med `gen_random_uuid()`
- Egne migreringer for `CREATE INDEX CONCURRENTLY`
- Repeterbare migreringer (`R__*.sql`) for views, funksjoner og lignende

Se [references/migration-flyway.md](references/migration-flyway.md) for migrasjonseksempler.

## Sjekkliste

- [ ] EXPLAIN ANALYZE kjørt på tunge spørringer
- [ ] Indekser på alle FK-kolonner og hyppig brukte WHERE-kolonner
- [ ] `CREATE INDEX CONCURRENTLY` vurdert for nye prod-indekser på store tabeller
- [ ] CHECK/UNIQUE constraints brukt der domeneregler kan håndheves i databasen
- [ ] Ingen N+1-spørringer
- [ ] SELECT bare kolonner som trengs
- [ ] LIMIT på spørringer som kan returnere mange rader
- [ ] Tilkoblingspoolen er riktig dimensjonert
- [ ] Migrasjoner er reversible der mulig
- [ ] Ingen `SELECT *` i produksjonskode

## Grenser

### ✅ Alltid
- EXPLAIN ANALYZE på tunge spørringer
- Indekser på FK-kolonner og hyppige WHERE-kolonner
- TIMESTAMPTZ for alle tidsstempel-kolonner
- LIMIT på spørringer som kan returnere mange rader

### ⚠️ Spør først
- Nye indekser på store tabeller i produksjon — bruk `CONCURRENTLY` ved behov
- Endring av størrelse på tilkoblingspool
- Partisjonering eller advisory locks i eksisterende løsninger

### 🚫 Aldri
- `SELECT *` i produksjonskode
- N+1-spørringer
- `DROP TABLE` i produksjon uten backup-plan
- `TIMESTAMP` uten tidssone (bruk `TIMESTAMPTZ`)

## Referansefiler

| Fil | Innhold |
|-----|---------|
| [references/sql-patterns.md](references/sql-patterns.md) | SQL-eksempler: EXPLAIN, indekser, JSONB, vindusfunksjoner, CTE, upsert, advisory locks, partisjonering, anti-mønstre, tilkoblingspool |
| [references/migration-flyway.md](references/migration-flyway.md) | Migrasjonsmønstre: TIMESTAMPTZ, FK-indekser, UUID, CONCURRENTLY, repeterbare migreringer |
