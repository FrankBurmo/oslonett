# Tekniske forbedringsforslag for www.oslo.net

> **Dokument:** Teknisk vurdering og prioriterte tiltak  
> **Dato:** 5. mai 2026  
> **Kontekst:** Historisk arkivnettsted — kulturarvressurs innlemmet i Norges dokumentarv (UNESCO)

---

## Innledning og prinsipp

Siden dette er et **historisk arkivnettsted**, ikke en aktiv applikasjon, er det avgjørende å skille mellom to typer forbedringer:

- **Infrastruktur og verktøy** (ikke-invasivt): Forbedringer av hosting, tilgjengelighet og vedlikehold som ikke endrer utseende eller opplevelse av det historiske innholdet.
- **Modernisering av visningslag** (invasivt): Endringer som påvirker brukeropplevelsen og det historiske uttrykket — bør gjøres med varsomhet og bare der det øker tilgjengeligheten.

Forslagene er rangert etter **samlet nytteverdi** vektet mot **risiko for å forstyrre arkivets historiske integritet**.

---

## Rangeringsskala

| Prioritet | Merke | Beskrivelse |
|-----------|-------|-------------|
| Kritisk | 🔴 | Bør gjøres umiddelbart |
| Høy | 🟠 | Bør gjøres innen kort tid |
| Middels | 🟡 | Nyttig, kan planlegges |
| Lav | 🟢 | Ønskelig, men ikke presserende |

---

## Prioritert liste over forbedringsforslag

---

### 🔴 P1 — Fjern CDN-avhengighet for Lunr.js

**Kategori:** Pålitelighet / Langsiktig bevaring  
**Innsats:** Lav (< 1 time)

**Problem:**  
Søkefunksjonen (`search.js`) laster Lunr.js fra en ekstern CDN:

```html
<script src="https://unpkg.com/lunr/lunr.js"></script>
```

Dette betyr at søkefunksjonen slutter å virke dersom `unpkg.com` er utilgjengelig, endrer URL-struktur, eller opphører. For et langsiktig arkiv er ekstern avhengighet en risiko.

**Løsning:**  
Last ned en spesifikk versjon av `lunr.min.js` og legg den i `/js/`-mappen. Oppdater alle script-referanser til å peke lokalt:

```html
<script src="/js/lunr.min.js"></script>
```

**Gevinst:** Nettstedet fungerer fullstendig offline/airgapped og er ikke avhengig av tredjeparter.

---

### 🔴 P2 — Erstatt inline `console.log` med betinget debug-logging

**Kategori:** Kodekvalitet / Ytelse  
**Innsats:** Svært lav (15 minutter)

**Problem:**  
`onheaders.js` inneholder en aktiv `console.log` som logger til nettleser-konsoll for alle brukere:

```javascript
console.log(imgElement.src);
```

Dette er debug-kode som ble liggende igjen og tilfører ingen verdi for sluttbrukere.

**Løsning:**  
Fjern linjen, eller erstatt med betinget logging:

```javascript
if (window.DEBUG) console.log(imgElement.src);
```

---

### 🔴 P3 — Legg til `Content Security Policy` (CSP) header

**Kategori:** Sikkerhet (OWASP A05: Security Misconfiguration)  
**Innsats:** Lav (1 time)

**Problem:**  
Nettstedet har ingen CSP-header definert. Dette øker risikoen for XSS-angrep, spesielt siden søkeresultater rendres i DOM via JavaScript.

**Løsning:**  
Legg til en `_headers`-fil i rotkatalogen (Netlify/GitHub Pages-kompatibel via Cloudflare eller egendefinert proxy):

```
/*
  Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: no-referrer-when-downgrade
```

**Alternativ for GitHub Pages:** Bruk en `vercel.json` ved evt. migrering, eller vurder Cloudflare Pages som tilbyr header-konfigurasjon.

**Gevinst:** Beskyttelse mot XSS og clickjacking. Spesielt relevant siden søkefunksjonen injiserer HTML i DOM (se P4).

---

### 🟠 P4 — Sanitering av søkeresultater mot XSS

**Kategori:** Sikkerhet (OWASP A03: Injection)  
**Innsats:** Lav–middels (1–3 timer)

**Problem:**  
`search.js` rendrer søkeresultater direkte i DOM. Dersom indeksert innhold inneholder spesialtegn, kan disse i teorien tolkes som HTML-kode. Selv om innholdet er statisk og kontrollert, er prinsippet usikkert.

**Løsning:**  
Bruk alltid `textContent` i stedet for `innerHTML` der det er mulig, eller bruk en saniterer. Eksempel:

```javascript
// Usikkert:
element.innerHTML = result.title;

// Sikkert:
element.textContent = result.title;
```

For HTML-fragmenter: bruk `DOMParser` og `textContent`-ekstraksjon, eller biblioteker som `DOMPurify`.

---

### 🟠 P5 — Legg til `<meta charset="utf-8">` på alle sider uten det

**Kategori:** Tilgjengelighet / Korrekthet  
**Innsats:** Middels (automatiserbar med skript)

**Problem:**  
Mange av de eldre HTML-filene (1990-talls-sider) mangler charset-deklarasjon, eller bruker `encoding="utf8"` (feil skriving) i XML-proloGen. Moderne nettlesere kan mistolke norske tegn (æ, ø, å) uten eksplisitt charset.

Eksempel på manglende charset:
```html
<html>
<head>
 <title>Visjon</title>
 <!-- Ingen charset-meta -->
```

**Løsning:**  
Legg til `<meta charset="utf-8">` i `<head>` på alle sider. Kan gjøres med et enkelt `sed`/Python-skript.

**Gevinst:** Korrekt visning av norske tegn i alle nettlesere og alle innstillinger.

---

### 🟠 P6 — Generer og vedlikehold en `sitemap.xml`

**Kategori:** Oppdagbarhet / SEO / Bevaring  
**Innsats:** Lav (1–2 timer)

**Problem:**  
Det finnes ingen `sitemap.xml` eller `robots.txt`. Dette gjør det vanskeligere for søkemotorer, nettarkiver (Wayback Machine, Nasjonalbiblioteket) og forskere å indeksere innholdet systematisk.

**Løsning:**  
1. Generer `sitemap.xml` med alle `.html`-filer via et enkelt Python-skript eller statisk site-generator.
2. Legg til `robots.txt` som eksplisitt tillater og guider crawler:

```
User-agent: *
Allow: /
Sitemap: https://www.oslo.net/sitemap.xml
```

**Gevinst:** Bedre arkivering i Wayback Machine og andre digitale bevaringsinitiativ. Viktig for et UNESCO-anerkjent kulturarvsdokument.

---

### 🟠 P7 — Strukturer søkeindeksen som en del av byggeprosessen

**Kategori:** Vedlikeholdbarhet  
**Innsats:** Middels (3–6 timer)

**Problem:**  
Søkeindeksen (`/js/index/index-*.json`) er pre-generert og sjekket inn i git. Dette betyr at indeksen kan bli utdatert dersom innhold endres, og det er uklart hvordan den regenereres.

**Løsning:**  
1. Legg til et `package.json` med et `build`-skript som genererer indeksen fra HTML-filene.
2. Alternativt: Legg til en GitHub Actions workflow som automatisk regenererer og committer indeksen ved endringer i `.html`-filer.

Eksempel på workflow:
```yaml
name: Rebuild search index
on:
  push:
    paths: ['**/*.html']
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: node scripts/build-index.js
      - run: git commit -am "Rebuild search index" && git push
```

---

### 🟡 P8 — Legg til `<meta name="viewport">` på alle sider

**Kategori:** Mobilvisning / Tilgjengelighet  
**Innsats:** Lav (automatiserbar)

**Problem:**  
Ingen av sidene har viewport-metatag. På mobil vises nettstedet svært lite og krever zoom. Siden dette er et kulturarvnettsted som bør være tilgjengelig for alle, er dette viktig.

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

**Viktig presisering:** Legg til metatagen uten å endre den faktiske layouten — å legge til viewport-metatag alene gjør at mobil-nettlesere viser siden i sin faktiske størrelse (der tabellene vil overflow), noe som er mer korrekt enn at siden zoomes ned til uleselig størrelse. Det er en informasjonsbevaring, ikke modernisering.

---

### 🟡 P9 — Erstatt `unpkg.com`-avhengighet i Lunr med lokal kopi og integrity-sjekk

**Kategori:** Sikkerhet / Pålitelighet  
**Innsats:** Lav  
**Merk:** Delvis overlapp med P1 — dette er utdyping av sikkerhetsaspektet.

**Problem:**  
Dersom Lunr.js lastes fra CDN, bør Subresource Integrity (SRI) brukes for å verifisere at scriptet ikke er manipulert:

```html
<!-- Med SRI (midlertidig til lokal kopi er på plass): -->
<script 
  src="https://unpkg.com/lunr/lunr.js" 
  integrity="sha384-[HASH]" 
  crossorigin="anonymous">
</script>
```

Best: flytt til lokal kopi (se P1).

---

### 🟡 P10 — Legg til `<html lang="no">` der det mangler

**Kategori:** Tilgjengelighet (WCAG 2.1 — 3.1.1 Language of Page)  
**Innsats:** Lav (automatiserbar)

**Problem:**  
Mange 1990-tallssider mangler `lang`-attributt eller har `lang="en"` på norskspråklige sider (trolig fra HTML Tidy defaults). Eksempel fra `historie/index.html`:

```html
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
```

Dette er feil — siden er på norsk.

**Løsning:**  
Oppdater alle norskspråklige sider til `lang="no"`. Filen `index.html` (roten) er korrekt:
```html
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="no" lang="no">
```

**Gevinst:** Skjermlesere leser nettstedet med korrekt norsk uttale. Viktig for tilgjengelighet.

---

### 🟡 P11 — Legg til åpne graph (`og:`)-metadata og Twitter/X Card-tags

**Kategori:** Synlighet / Deling  
**Innsats:** Lav–middels

**Problem:**  
Forsiden og historiesidene mangler Open Graph-metadata. Når noen deler lenker til nettstedet på sosiale medier, vises ingen forhåndsvisning (thumbnail, tittel, beskrivelse).

**Løsning:**  
Legg til i `<head>` på minst forsiden og de viktigste historiesidene:

```html
<meta property="og:title" content="Oslonett — Norges første internettselskap" />
<meta property="og:description" content="Historisk arkiv fra Oslonett AS (1991–1995), Norges første kommersielle internettselskap." />
<meta property="og:image" content="https://www.oslo.net/img/on.gif" />
<meta property="og:url" content="https://www.oslo.net/" />
<meta property="og:type" content="website" />
```

---

### 🟡 P12 — Legg til broken-link-sjekk i CI/CD

**Kategori:** Vedlikeholdbarhet / Brukeropplevelse  
**Innsats:** Lav (1–2 timer)

**Problem:**  
Mange lenker i nettstedet peker til ressurser som ikke lenger eksisterer. Det er ingen automatisk sjekk av dette.

**Løsning:**  
Legg til en GitHub Actions workflow med et verktøy som `lychee` eller `linkchecker`:

```yaml
name: Check links
on:
  schedule:
    - cron: '0 6 * * 1'  # Ukentlig mandag
  workflow_dispatch:

jobs:
  linkcheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check links
        uses: lycheeverse/lychee-action@v1
        with:
          args: --verbose --no-progress './**/*.html'
```

---

### 🟡 P13 — Dokumenter bygge- og vedlikeholdsprosedyrer

**Kategori:** Vedlikeholdbarhet  
**Innsats:** Lav (1–2 timer)

**Problem:**  
Det er ingen teknisk dokumentasjon av:
- Hvordan søkeindeksen genereres/regenereres
- Hvilke avhengigheter som brukes
- Hvordan man setter opp lokalt utviklingsmiljø

**Løsning:**  
Utvid `README.md` med en «For utviklere»-seksjon, eller opprett `CONTRIBUTING.md` med:
- Forutsetninger (Node.js-versjon for indeksgenerering)
- Kommandoer for å regenerere søkeindeks
- Lokal testing (f.eks. `npx serve .`)

---

### 🟢 P14 — Vurder å legge til `<link rel="canonical">` på duplikatsider

**Kategori:** SEO / Tilgjengelighet  
**Innsats:** Lav

**Problem:**  
Noen sider finnes i flere versjoner (f.eks. `Homes.html` og `Homes.html-orig` i `/Aksess/`). Søkemotorer kan se disse som duplikatinnhold.

**Løsning:**  
Legg til canonical-tag på ikke-primærsider:
```html
<link rel="canonical" href="https://www.oslo.net/Aksess/Homes.html" />
```

---

### 🟢 P15 — Erstatt `<font>`-tagger og attributt-basert styling med CSS

**Kategori:** Kodekvalitet / Langsiktig vedlikehold  
**Innsats:** Høy — **med stor varsomhet**

**Problem:**  
De eldre 1990-tallssidene bruker `<font size="+2">`, `<center>`, `bgcolor`-attributter osv. — teknologier som er fjernet fra HTML5.

**Viktig presisering:**  
Dette forslaget er rangert **lavt** av en god grunn: Å erstatte `<font>`-tagger og tabellbasert layout på 1990-tallssidene vil **endre det historiske uttrykket**. Nettstedet er et arkiv, og det visuelle uttrykket er en del av det historiske dokumentet. 

**Anbefaling:**  
Dersom dette gjøres, gjør det kun på jubileumsinnholdet fra 2001 og nyere (f.eks. `index.html`, `alumni.html`, `referat.html`) — ikke på originalsidene fra 1993–1997.

---

### 🟢 P16 — Vurder å migrere til en statisk site-generator

**Kategori:** Vedlikeholdbarhet / Skalerbarhet  
**Innsats:** Høy — **valgfritt**

**Problem:**  
I dag er navigasjonsmenyen (topptabellen med lenker) duplisert i nesten alle HTML-filer. Enhver endring i navigasjonen krever manuell oppdatering av alle filer.

**Løsning:**  
Bruk en statisk site-generator (f.eks. **Eleventy/11ty**, Hugo eller Jekyll) med templates. Den historiske HTML-en kan bevares som «rå»-inkluderinger med en wrapper-template.

**Gevinst:** Enklere vedlikehold av felles elementer (header, footer, søkeboks).

**Risiko:** Stor ombygging; krever at man ikke endrer det arkiverte innholdet.

---

## Oppsummering og prioriteringsoversikt

| Prioritet | ID | Tiltak | Kategori | Innsats |
|-----------|-----|--------|----------|---------|
| 🔴 Kritisk | P1 | Fjern CDN-avhengighet for Lunr.js | Pålitelighet | Lav |
| 🔴 Kritisk | P2 | Fjern debug `console.log` | Kodekvalitet | Svært lav |
| 🔴 Kritisk | P3 | Legg til Content Security Policy | Sikkerhet | Lav |
| 🟠 Høy | P4 | Sanitering av søkeresultater mot XSS | Sikkerhet | Lav–middels |
| 🟠 Høy | P5 | Legg til `<meta charset>` der det mangler | Korrekthet | Lav |
| 🟠 Høy | P6 | Generer `sitemap.xml` og `robots.txt` | Bevaring/SEO | Lav |
| 🟠 Høy | P7 | Strukturer søkeindeks som byggeprosess | Vedlikehold | Middels |
| 🟡 Middels | P8 | Legg til `<meta name="viewport">` | Tilgjengelighet | Lav |
| 🟡 Middels | P9 | SRI-sjekk på CDN-script | Sikkerhet | Lav |
| 🟡 Middels | P10 | Rett `lang`-attributt til norsk | Tilgjengelighet | Lav |
| 🟡 Middels | P11 | Open Graph-metadata | Synlighet | Lav–middels |
| 🟡 Middels | P12 | Broken-link-sjekk i CI | Vedlikehold | Lav |
| 🟡 Middels | P13 | Dokumenter bygge-/vedlikeholdsprosess | Vedlikehold | Lav |
| 🟢 Lav | P14 | Canonical-tagger på duplikatsider | SEO | Lav |
| 🟢 Lav | P15 | Erstatt `<font>`-tagger med CSS | Kodekvalitet | Høy |
| 🟢 Lav | P16 | Migrering til statisk site-generator | Arkitektur | Høy |

---

## Spesielle hensyn for et kulturarvnettsted

Dette nettstedet er ikke en vanlig webapplikasjon. Det er et **historisk dokument** med nasjonal og internasjonal (UNESCO) kulturarvsstatus. Tekniske forbedringer bør alltid veies mot følgende prinsipper:

1. **Minimalisme**: Gjør bare det som er nødvendig for at nettstedet skal fungere og overleve.
2. **Gjennomsiktighet**: Dokumenter tydelig hva som er originalt innhold og hva som er moderne tillegg.
3. **Reversibilitet**: Alle endringer bør være enkelt reverserbare.
4. **Separasjon**: Hold infrastrukturlag (CSP, sitemap, CI) adskilt fra presentasjonslaget (HTML/CSS).

De kritiske og høye prioriteringene (P1–P7) berører ikke den historiske HTML-en direkte, men styrker pålitelighet, sikkerhet og langsiktig bevaring av arkivet.

---

*Vurdering basert på analyse av kildefilene i skibohemen/oslonett, mai 2026.*
