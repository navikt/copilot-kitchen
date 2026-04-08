# SQL-mønstre og eksempler

Kodeeksempler for PostgreSQL-gjennomgang. Se [SKILL.md](../SKILL.md) for prinsipper og sjekkliste.

## EXPLAIN-analyse

```sql
-- Alltid kjør EXPLAIN ANALYZE på tunge spørringer
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM vedtak WHERE bruker_id = '...' AND status = 'AKTIV';

-- Se etter:
-- • Seq Scan på store tabeller → mangler indeks
-- • Nested Loop med høye rader → N+1-problem
-- • Sort med external merge → mangler minne eller indeks
-- • Buffers shared read høy → data ikke i cache
```

## Indeksstrategier

```sql
-- ✅ Indeks på kolonner brukt i WHERE, JOIN, ORDER BY
CREATE INDEX idx_vedtak_bruker_status ON vedtak (bruker_id, status);

-- ✅ Partial index for vanlige filtre
CREATE INDEX idx_vedtak_aktiv ON vedtak (bruker_id) WHERE status = 'AKTIV';

-- ✅ Covering index (unngår table lookup)
CREATE INDEX idx_vedtak_covering ON vedtak (bruker_id) INCLUDE (opprettet, status);

-- ✅ GIN-indeks for JSONB
CREATE INDEX idx_metadata_gin ON dokument USING gin (metadata);

-- ❌ Indeks på kolonner med lav kardinalitet
CREATE INDEX idx_vedtak_status ON vedtak (status); -- bare 3-4 verdier
```

## JSONB-mønstre

```sql
-- ✅ Spørringer mot JSONB med GIN-indeks
SELECT * FROM dokument WHERE metadata @> '{"type": "søknad"}';

-- ✅ Spesifikk nøkkeloppslag
SELECT metadata->>'type' FROM dokument WHERE id = '...';

-- ❌ Funksjonsbasert spørring uten indeks
SELECT * FROM dokument WHERE metadata->>'type' = 'søknad';
```

## Vindusfunksjoner

```sql
-- ✅ ROW_NUMBER for paginering/dedup
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY bruker_id ORDER BY opprettet DESC) AS rn
    FROM vedtak
) t WHERE rn = 1;

-- ✅ LAG/LEAD for tidsserier
SELECT dato, verdi, verdi - LAG(verdi) OVER (ORDER BY dato) AS endring
FROM metrikk;

-- ✅ Running total per bruker
SELECT bruker_id, dato, belop,
       SUM(belop) OVER (PARTITION BY bruker_id ORDER BY dato) AS running_total
FROM utbetaling;
```

## CTE (Common Table Expressions)

```sql
-- ✅ Del opp kompleks logikk i navngitte steg
WITH aktive_vedtak AS (
    SELECT id, bruker_id, opprettet
    FROM vedtak
    WHERE status = 'AKTIV'
), siste_per_bruker AS (
    SELECT bruker_id, MAX(opprettet) AS siste_opprettet
    FROM aktive_vedtak
    GROUP BY bruker_id
)
SELECT a.*
FROM aktive_vedtak a
JOIN siste_per_bruker s
  ON s.bruker_id = a.bruker_id
 AND s.siste_opprettet = a.opprettet;
```

## Upsert / ON CONFLICT

```sql
-- ✅ Batch insert
INSERT INTO hendelse (id, type, data)
VALUES
    ($1, $2, $3),
    ($4, $5, $6),
    ($7, $8, $9);

-- ✅ Upsert
INSERT INTO bruker_innstilling (bruker_id, tema, verdi)
VALUES ($1, $2, $3)
ON CONFLICT (bruker_id, tema) DO UPDATE SET verdi = EXCLUDED.verdi, updated_at = NOW();

-- ✅ Insert ignore
INSERT INTO hendelse (id, type, data) VALUES ($1, $2, $3)
ON CONFLICT (id) DO NOTHING;
```

## CHECK og UNIQUE constraints

```sql
ALTER TABLE vedtak ADD CONSTRAINT chk_status CHECK (status IN ('AKTIV', 'AVSLUTTET', 'KANSELLERT'));
ALTER TABLE bruker ADD CONSTRAINT unq_bruker_fnr UNIQUE (fnr);
```

## Advisory locks

```sql
-- ✅ Prøv å ta en applås uten å blokkere
SELECT pg_try_advisory_lock(42);

-- ✅ Transaksjonsbundet lås
BEGIN;
SELECT pg_advisory_xact_lock(123456);
UPDATE jobb SET status = 'RUNNING' WHERE id = ?;
COMMIT;
```

## Partisjonering

```sql
-- ✅ Range partitioning for store tidsserier
CREATE TABLE audit_log (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL,
    payload JSONB NOT NULL
) PARTITION BY RANGE (created_at);

CREATE TABLE audit_log_2025_01 PARTITION OF audit_log
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

## Anti-mønstre

### N+1-spørringer

```kotlin
// ❌ N+1: én spørring per vedtak
val saker = sakRepository.findAll()
saker.forEach { sak ->
    val vedtak = vedtakRepository.findBySakId(sak.id) // N ekstra spørringer
}

// ✅ Batch-henting
val saker = sakRepository.findAll()
val vedtakBySakId = vedtakRepository.findBySakIdIn(saker.map { it.id })
    .groupBy { it.sakId }
```

### SELECT *

```sql
-- ❌ Henter alle kolonner
SELECT * FROM vedtak WHERE bruker_id = '...';

-- ✅ Hent kun det du trenger
SELECT id, status, opprettet FROM vedtak WHERE bruker_id = '...';
```

### Manglende LIMIT

```sql
-- ❌ Kan returnere millioner av rader
SELECT * FROM hendelse WHERE type = 'SYKMELDING';

-- ✅ Begrens resultatsettet
SELECT * FROM hendelse WHERE type = 'SYKMELDING'
ORDER BY opprettet DESC LIMIT 100;
```

## Tilkoblingspool

```yaml
# Nais — HikariCP-konfigurasjon
spec:
  gcp:
    sqlInstances:
      - type: POSTGRES_15
        databases:
          - name: myapp-db
            envVarPrefix: DB
```

```kotlin
// ✅ HikariCP-defaults for Nav
HikariConfig().apply {
    maximumPoolSize = 5  // Start lavt, øk ved behov
    minimumIdle = 2
    connectionTimeout = 10_000
    idleTimeout = 300_000
    maxLifetime = 600_000
}
```
