---
name: brainstorm
description: Utforsk et problem og land på et design før planlegging. Brukes for å forstå hva som skal bygges, vurdere alternativer og bli enig om tilnærming — FØR kode skrives eller plan lages.
---

# Brainstorm — fra idé til design

Hjelper med å gjøre en vag idé om til et konkret, gjennomtenkt design gjennom naturlig dialog.

## Når brukes denne?

- Før Souschef lager plan (medium/store oppgaver)
- Når utvikleren sier "jeg tenker på...", "hva om vi...", "hvordan bør vi..."
- Når det finnes flere mulige tilnærminger og man trenger å velge

## Prosess

### 1. Forstå konteksten

Utforsk kodebasen før du stiller spørsmål:
- Les relevante filer og dokumentasjon
- Sjekk eksisterende mønstre
- Forstå rammer og avhengigheter

### 2. Avklarende spørsmål

Still spørsmål **ett om gangen**. Foretrekk flervalg:

> Hva er det viktigste kravet her?
> A) Ytelse — dette kjører tusenvis av ganger
> B) Enkelhet — dette skal være lett å vedlikeholde
> C) Fleksibilitet — kravene vil endre seg

Fokuser på: formål, rammer, suksesskriterier.

### 3. Foreslå 2-3 tilnærminger

Presenter alternativer med avveininger og din anbefaling:

```
### A: [Navn] ⭐ anbefalt
- Fordeler: ...
- Ulemper: ...

### B: [Navn]
- Fordeler: ...
- Ulemper: ...

### C: [Navn]
- Fordeler: ...
- Ulemper: ...

**Min anbefaling:** A, fordi [begrunnelse].
```

Led med anbefalingen. Forklar hvorfor.

### 4. Presenter designet

Når tilnærmingen er valgt, presenter designet seksjon for seksjon:
- Arkitektur og komponenter
- Dataflyt og grensesnitt
- Feilhåndtering
- Testing

Spør etter hver seksjon: "Ser dette riktig ut?"

### 5. Overlevering

Når designet er godkjent:
- Oppsummer avgjørelsene som ble tatt
- List konkrete filer som vil endres
- Overlever til Souschef (via Hovmester) for detaljert planlegging

## Prinsipper

- **Ett spørsmål om gangen** — ikke overbelast
- **YAGNI** — fjern unødvendige funksjoner fra alle forslag
- **Utforsk alternativer** — aldri gå rett til løsning
- **Inkrementell validering** — få godkjenning underveis
- **Følg eksisterende mønstre** — ikke foreslå omskriving uten grunn
