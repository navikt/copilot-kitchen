---
name: presentasjon
description: Lag, review eller forbedre tekniske presentasjoner — sterkere narrativ, mindre tekst, bedre visuals og tryggere live-demo.
---

# Tech Talk Design

Hjelper med å gjøre tekniske presentasjoner skarpere, mer visuelle og enklere å fremføre.

## Når brukes denne?

- Når en bruker lager eller forbedrer en teknisk presentasjon
- Når decken handler om arkitektur, AI, kode, plattform, devtools eller live-demo
- Når brukeren ber om review, grilling, story arc, slide-kutt, visuell løfting eller speaker notes

## Prosess

### 1. Finn hovedpåstanden

Før du designer slides, formuler talken som én setning:

> Etter denne talken skal publikum forstå at ...

Hvis hovedpåstanden er uklar, hjelp brukeren å velge én. Ikke optimaliser slides før
budskapet er stramt.

### 2. Lag en talk arc

Bruk en enkel rytme:

1. Premiss: hva er problemet?
2. Friksjon: hvorfor holder ikke standardmåten?
3. Modell: hvilken mental modell løser det?
4. Bevis: demo, konkret case eller diff
5. Transfer: hvordan kan publikum bruke dette selv?

For live-demo: start demoen tidlig hvis den trenger tid, kom tilbake til resultatet senere,
og ha en eksplisitt fallback.

### 3. Gjør slide-inventory

For hver slide, noter:

- Hovedpoeng på maks én setning
- Hva publikum skal se på skjermen
- Hva taleren skal si, men som ikke bør stå på sliden
- Om sliden kan kuttes, slås sammen eller flyttes til speaker notes

Kutt først. Pynt etterpå.

### 4. Bytt tekst mot visuelle former

Bruk dette som standard-transformasjoner:

- Bulletliste → prosess, systemdiagram eller før/etter
- Tabell → capability map, heatmap eller prioritert matrise
- Abstrakt begrensning → gauge, budsjett, meter eller flaskehals
- Arkitektur → bokser + flyt + eierskap, ikke paragraf
- Beslutning → tradeoff-kort med anbefaling
- Distribusjon/oppsett → én tydelig call-to-action

En slide bør bestå tresekunders-testen: publikum skjønner hovedpoenget før de rekker å lese alt.

### 5. Review hardt

Grill decken på:

- Er dette én idé per slide?
- Kan poenget forstås visuelt?
- Har sliden tekst taleren uansett kommer til å si muntlig?
- Er demoen en del av historien, ikke et appendiks?
- Har talken variasjon mellom konsept, diagram, konkret artefakt og live-visning?
- Er avslutningen en handling publikum kan ta?

## Visuell retning

Velg en tydelig estetikk som matcher tema og publikum. For utviklerpublikum fungerer ofte:
terminal/ops, blueprint, packet trace, system map, diff view eller debugger. Unngå generisk
AI-gradient og dekor som ikke forklarer noe.

Prioriter lesbarhet på projektor: store titler, høy kontrast, få ord, tydelige former.

## Prinsipper

Bruk [references/presentation-principles.md](./references/presentation-principles.md) når du
trenger teori eller begrunnelse bak en anbefaling.
