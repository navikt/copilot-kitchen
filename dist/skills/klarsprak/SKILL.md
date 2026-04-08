---
name: klarsprak
description: Norsk teknisk redaktør — klarspråk, AI-markører, anglismer, fagtermer, mikrotekst
---
# Klarspråk — norsk teknisk skriving

Retningslinjer for norsk bokmål i teknisk dokumentasjon, UI-tekst og PR-beskrivelser.

Basert på Språkrådets klarspråk-prinsipper, ISO 24495-1 og Navs språkprofil.

## Klarspråk

### Det viktigste først

Start med konklusjonen. Bakgrunn og kontekst kommer etterpå.

```
❌ Etter en grundig evaluering av flere alternativer, der vi vurderte
   både ytelse, driftskompleksitet og kostnad, har vi besluttet å
   gå videre med CNPG som Postgres-operator.

✅ Vi bruker CNPG som Postgres-operator. Den gir oss automatisk
   failover, backup og oppgradering uten nedetid.
```

### Unngå substantivsyke

```
❌ Vi foretar en gjennomgang av implementasjonen.
✅ Vi gjennomgår implementasjonen.

❌ Det er behov for en vurdering av sikkerhetsaspektene.
✅ Vi må vurdere sikkerheten.
```

### Kort over langt

- Kort setning over lang
- Vanlig ord over fancy ord
- Aktiv form over passiv ("vi bruker" ikke "det benyttes")
- Konkret over abstrakt
- Kutt fyllord: "i bunn og grunn", "i stor grad", "på mange måter"

### Struktur

- Korte avsnitt (2–4 setninger)
- Gode mellomtitler som sier hva seksjonen handler om
- Kulepunkter for lister
- Bare første ord og egennavn med stor bokstav i overskrifter

## AI-markører

Fjern mønstre som avslører KI-generert tekst.

### Svulstige ord

| AI-markør | Gjør i stedet |
|-----------|---------------|
| "banebrytende", "revolusjonerende" | Konkrete beskrivelser |
| "robust", "helhetlig", "sømløs" | Skriv om eller dropp |
| "spiller en avgjørende rolle" | Gå rett på sak |
| "effektivisere prosessen" | Si hvilken prosess og hvordan |
| "digital transformasjon" | Si hva som endres konkret |
| "sikre at" | "passe på", "gjøre X mulig" |
| "sørge for at" | "gjøre", "passe på" |
| "muliggjøre" | "gjøre mulig", "gi rom for" |
| "understreke behovet for" | Si behovet direkte |
| "hensynta" | "ta hensyn til" |
| "implementere" | "innføre", "ta i bruk", "lage" |
| "ivareta" | "ta vare på", "følge opp" |
| "tilrettelegge for" | "legge til rette for", "gjøre det enklere" |
| "understøtte" | "støtte" |

### Åpnings- og avslutningsfraser (kutt disse)

- "det er verdt å merke seg", "det er viktig å påpeke"
- "la oss utforske", "la oss dykke ned i"
- "oppsummert kan man si at", "avslutningsvis"

### Strukturelle mønstre

- Fjern oppsummeringssetninger som bare gjentar det du har skrevet
- Ikke tving balanse mellom alternativer når ett er bedre
- Varier grammatisk struktur i kulepunkter
- Ikke overforklar ting som er åpenbare for målgruppa

### Overgangsord og setningsbinding

Varier overgangene mellom setninger og avsnitt. Unngå å starte mange setninger etter hverandre med:

- "Videre", "I tillegg", "Dessuten"
- "Det er viktig å", "Det er verdt å"
- "For å sikre at", "Med tanke på"

Bruk i stedet konkrete subjekter: "Teamet ...", "Koden ...", "Tjenesten ..."

## Fagtermer

### Alltid engelsk (ikke oversett)

image, cluster, node, container, deployment, release, plugin, backup, failover, rollback, upstream, downstream, secret, namespace, pod, pipeline, workflow, runtime, framework, pull request, merge, commit, branch, rebase, endpoint, payload, token, scope, bug, hotfix, patch

### Norsk er OK for

feilsøking, oppgradering, sikkerhetskrav, vedlikehold, bidragsytere, brukervennlighet, tilgjengelighet, kodegjennomgang, avhengighet

### Sammensatte ord med engelske termer

Bruk bindestrek: `image-bygg`, `CI-pipeline`, `deploy-steg`, `Kafka-topicet`, `GitHub-repoet`

## Anglismer

### Unødvendige anglismer — bruk norsk

| Anglisme | Norsk alternativ |
|----------|-----------------|
| "adressere et problem" | "løse", "fikse", "ta tak i" |
| "på slutten av dagen" | "til syvende og sist" eller dropp |
| "ta eierskap til" | "ha ansvar for" |
| "delivere" | "levere" |
| "har du noen input?" | "har du innspill?" |
| "involvere" (overbrukt) | "ta med", "inkludere" |
| "deploye" | "rulle ut" |
| "shippe" | "levere", "sende ut" |
| "reviewe" | "gå gjennom", "se over" |
| "release" (som verb) | "gi ut", "rulle ut" |
| "onboarde" | "ta imot", "sette i gang" |
| "pitche" | "presentere", "foreslå" |
| "tracke" | "følge med på", "spore" |
| "booste" | "øke", "forbedre" |
| "aligne" | "samkjøre", "enes om" |
| "triage" | "prioritere", "sortere" |

## Nav-spesifikt

- **Nav** — ikke "NAV" (gammelt akronym) og ikke "nav"
- Konsekvent bokmål, ikke bland inn nynorsk
- Moderne, ledig bokmål: "framtid" over "fremtid"
- "vi" ikke "man" i interne dokumenter
- Skriv som om du forklarer til en kollega

## Teksttyper

| Teksttype | Tone | Tips |
|-----------|------|------|
| ADR | Nøytral, teknisk | Kontekst → Beslutning → Konsekvenser. Ingen salgssnakk. |
| README | Direkte, vennlig | Start med hva appen gjør, deretter oppsett. |
| UI-tekst | Enkel, handlingsrettet | Korte setninger. Brukeren er "du". |

For commit-meldinger, se `conventional-commit`-skillen. For PR-beskrivelser, se `pull-request`-skillen.

## Tegnsetting

- **Bindestrek (-)**: Sammensatte ord: `API-kall`, `deploy-steg`, `CI-pipeline`
- **Tankestrek (–)**: Mellom verdier: `kl. 08–16`, `side 3–7`
- **Komma**: Sett komma før leddsetning som starter med "som", "fordi", "slik at", "når", "dersom"
- **Kolon**: Små bokstaver etter kolon med mindre det følger en hel setning

## UI-tekst

- **Knapper**: Korte, handlingsorienterte — "Lagre", "Send inn", "Avbryt"
- **Feilmeldinger**: Si hva som gikk galt og hva brukeren kan gjøre
- **Lenketekst**: Beskrivende, ikke "klikk her" eller "les mer"
- Norsk tallformat: mellomrom som tusenskilletegn ("151 354"), mellomrom før prosenttegn ("20 %")

## Før og etter

```
❌ Det er viktig å påpeke at Kubernetes representerer et betydelig skritt
   fremover innen container-orkestrering.

✅ Kubernetes orkestrerer containere. Vi bruker det til å kjøre og
   skalere appene våre i clusteret.
```

```
❌ Vi må adressere dette problemet og ta eierskap til prosessen.

✅ Vi må fikse dette. Teamet har ansvar for å finne en løsning.
```

```
❌ Operasjonen kunne ikke gjennomføres grunnet manglende
   obligatoriske feltverdier i skjemaet.

✅ Du må fylle ut alle påkrevde felt før du kan sende inn.
```

### README → rett på sak

```
❌ Dette prosjektet representerer et innovativt verktøy som
   muliggjør effektiv håndtering av søknader. Det er utviklet
   med tanke på å sette brukeren i sentrum.

✅ Behandler søknader om foreldrepenger. Bygget med Kotlin/Ktor,
   deployes til Nais.
```

### Unødvendig oppsummering → kutt

```
❌ Vi har nå gjennomgått de ulike aspektene ved migrasjonen.
   Som vi har sett, er det flere viktige hensyn å ta. Oppsummert
   kan man si at en vellykket migrering krever grundig planlegging.

✅ (Kutt hele avsnittet. Leseren har allerede lest det du oppsummerer.)
```

## Grenser

### ✅ Alltid
- Følg klarspråk-prinsippene: det viktigste først, aktiv form, konkret språk
- Behold etablerte engelske fagtermer
- Bindestrek i sammensatte ord med engelske termer
- Konsekvent formvalg gjennom hele teksten

### ⚠️ Spør først
- Endringer som kan påvirke faglig innhold
- Omstrukturering av hele dokumenter

### 🚫 Aldri
- Endre faglig innhold eller tekniske beslutninger
- Oversette etablerte engelske fagtermer til norsk
- Innføre nynorsk i bokmålstekster

## Kilder

- [Språkrådets klarspråk-prinsipper](https://sprakradet.no/Klarsprak/)
- [ISO 24495-1](https://sprakradet.no/klarsprak/kunnskap-om-klarsprak/iso-standard-for-klarsprak/)
- [Designsystemets tekstpraksis](https://designsystemet.no/no/blog/shared-guidelines-for-text/)
