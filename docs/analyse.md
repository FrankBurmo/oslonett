# Analyse av www.oslo.net — Oslonett historisk arkiv

> **Analysedato:** 5. mai 2026  
> **Analysert av:** GitHub Copilot  
> **Repository:** [skibohemen/oslonett](https://github.com/skibohemen/oslonett)  
> **Live nettsted:** [www.oslo.net](https://www.oslo.net)

---

## 1. Oversikt og formål

Dette repoet er et **historisk webarkiv** som dokumenterer og bevarer Oslonett — Norges første kommersielle internettselskap. Arkivet ble opprinnelig satt opp i 2001 i anledning Oslonetts 10-årsjubileum (12. desember 2001), og er i dag hostet på GitHub Pages under domenet `www.oslo.net`.

Nettstedet har en dobbel identitet:

1. **Et jubileums- og arkivnettsted** (2001–i dag): Primært formål er historisk dokumentasjon, med foredragsreferat, alumni-registrering og historisk kontekst om Oslonett og norsk internetthistorie.
2. **En autentisk gjengivelse av 1990-tallswebber**: Store deler av nettstedet er direkte gjenbruk og bevaring av originalinnholdet fra Oslonetts aktive periode 1993–1997, inkludert ISP-tjenestersider, nyhetsredaksjon og webtjenester.

### Historisk status

I **2014 ble Oslonetts nettsider innlemmet i Norges dokumentarv** — som første digitale «dokument» i UNESCO-programmet for dokumentarv. Nettstedet er dermed ikke bare et hobbyprosjekt, men en kulturarvressurs av nasjonal betydning.

---

## 2. Historisk bakgrunn

### Oslonett AS (1991–1995)

- **Stiftet:** 12. desember 1991
- **Initiativtaker:** Kjell Øystein Arisland (sendte invitasjonsmail 9. desember 1991)
- **Grunnleggere:** 16 informatikere fra Institutt for informatikk (UiO), Norsk Regnesentral og Universitetets Senter for Informasjonsteknologi (USIT)
- **Formål:** Kommersialisering av internettjenester i Norge
- **Opphørt:** 1. september 1995 — kjøpt opp av Schibsted AS

### Schibsted Nett AS (1995–1997)

Etter oppkjøpet ble selskapet omdøpt til Schibsted Nett AS. Visjonen var å «skape et tilbud av elektroniske tjenester som skal være ryggraden, nervesystemet og hjertet i det norske samfunn». Schibsted Nett forløpte til sist ut i SOL (Schibsteds Online) rundt 1996–1997.

### Arkivnettstedet (2001–i dag)

Innholdet ble hentet fra gamle backuper hos SOL System og satt opp på en privat webserver. Etter noen år gikk sidene offline, og er nå gjenopprettet på GitHub Pages uten forsøk på modernisering av utseende eller kode.

---

## 3. Tidslinje over milepæler

| År | Hendelse |
|----|----------|
| 1991 | Oslonett AS stiftet 12. desember |
| 1993 | Første webserver i Norge (etter NR, Ifi, TF, UiT) — `www.oslonett.no` |
| 1994 | OL '94 Lillehammer-webtjeneste (mye omtalt, nominert «Best of The Web» 1994) |
| 1994 | EU-avstemningsresultat-tjeneste i sanntid |
| 1993–1995 | ComputerWorld (CW) på web |
| 1994 | Kvasir søkemotor opprettet |
| 1995 | Oppkjøp av Schibsted AS — Oslonett AS ble Schibsted Nett AS |
| 1995–1996 | Newsdesk/SN Horisont nyhetsredaksjon |
| 1996 | Morgenbladet på web |
| 1996–1997 | SOL (Schibsteds Online) etableres |
| 2001 | 10-årsjubileum med seminarer ved Universitetet i Oslo — arkivnettsted opprettes |
| 2014 | Innlemmet i Norges dokumentarv (UNESCO) som første digitale dokument |

---

## 4. Teknisk stack og arkitektur

### 4.1 Markup

Nettstedet inneholder to distinkte generasjoner HTML:

| Generasjon | Teknologi | Eksempel |
|-----------|-----------|---------|
| **1990-talls originalsider** | HTML 2.0/3.2 uten DOCTYPE, rene `<font>`, `<center>`, `<table>`-basert layout, attributter som `bgcolor`, `border` direkte på elementer | `sn/visjon.html`, `Aksess/info.html` |
| **Jubileumssider (2001/nyere)** | XHTML 1.0 Transitional, processert med HTML Tidy 5.6.0 for Linux | `index.html`, `historie/index.html`, `alumni.html` |

Noen sider har `xml:lang="no"` og `<?xml version="1.0"?>` prolog — et tydelig XHTML-preg. Sidene er kodet med tabellbasert layout gjennomgående.

### 4.2 CSS

- **`/css/oslonett.css`**: Primær stilark for arkivnettstedet. Definerer klasser som `.whiteonblue`, `.menuframe`, `.frame`, `.ingress`, `.bodytext`, `.sokmatch` m.fl.
- **`/css/on-pres.css`**: Presentasjons-CSS (trolig brukt til foredragspresentasjon).
- **`/css/present.css`**: Ytterligere presentasjonsstil.

CSS-en bruker font-stacking med Arial/Verdana/Helvetica. Det er ingen responsivt design — nettstedet er designet for bredskjerm med fast bredde i prosent på `<table>`-elementer.

### 4.3 JavaScript

To moderne JavaScript-filer er lagt til i arkivnettstedet (ikke originale 1990-tallsfiler):

#### `js/onheaders.js`

Implementerer tidssensitivt header-bilde. Bytter automatisk bilde basert på tidspunkt:

```
00:00–04:59 → home_natt.gif
05:00–08:59 → home_morgen.gif
09:00–18:59 → home_dag.gif
19:00–23:59 → home_aften.gif
```

Bruker `DOMContentLoaded`, `setTimeout` og schedule-til-neste-time logikk. Dette er en reimplementering av opprinnelig Perl CGI-logikk.

#### `js/search.js`

Klient-side søk via **Lunr.js** (lastet fra `unpkg.com` CDN). Søkeindeksen er fordelt på 15 chunks (`index-0.json` til `index-14.json`) med 600 dokumenter per chunk, definert i `manifest.json`. Søket:

- Søker i 23+ filer
- Har debounce (200 ms) på input
- Viser resultater i en modal
- Stenger med Escape-tast eller klikk utenfor

### 4.4 Backend (CGI-scripts — historiske, ikke aktive)

| Fil | Språk | Funksjon |
|-----|-------|---------|
| `cgi/mailto.cgi` | Perl | Generell e-postformular-håndterer med mal-støtte |
| `cgi/paameld.cgi` | Perl | Påmelding til jubileumsforedrag |
| `cgi/search.cgi` | Perl | WAIS-basert fulltekstsøk (erstattet av Lunr.js) |
| `cgi/tell.cgi` | Perl | Tellingsfunksjon |
| `rndlogo.cgi` | Perl | Tilfeldig logo-velger |
| `rndtopp.cgi` | Perl | Tidssensitiv header-bildevisning (erstattet av JS) |

CGI-scriptene bruker `lib mySSI` (egenutviklet Server Side Includes-bibliotek), `CGI.pm`, `URI::Escape`, og `POSIX`. De er fra CVS-repository (se `$Id:`-tags med datoer rundt 1996–1998) og fungerer ikke i dagens hosting-miljø (GitHub Pages støtter ikke Perl/CGI).

### 4.5 Hosting

- **Platform:** GitHub Pages (statisk hosting)
- **Domene:** `www.oslo.net` (via CNAME-fil)
- **CDN-avhengigheter:** Lunr.js fra `unpkg.com`

### 4.6 Søkeindeks

Søkeindeksen er pre-generert som JSON og lagret i `/js/index/`:
- `manifest.json`: `{"chunks": 15, "chunk_size": 600}`
- `index-0.json` til `index-14.json`: Lunr.js-indeksdeler
- `docs.json`: Dokumentmetadata

---

## 5. Innholdsstruktur

### 5.1 Toppnivåstruktur

```
/                    → Startside (jubileum/arkiv)
/README.html         → Om nettstedet
/alumni.html         → Alumni-registrering (historisk skjema)
/referat.html        → Referat fra 10-årsjubileum
/program.html        → Program for jubileumsforedrag
/paamelding.html     → Påmelding til foredrag
/search.html         → Søkeside
/help.html           → Hjelpeside
```

### 5.2 Historisk seksjon (`/historie/`)

Dokumenterer Oslonetts virke med egne bakgrunnssider for hvert prosjekt:

- `arisland_mail.html` — Invitasjonsmailen som startet det hele (9. desember 1991)
- `hvem.html` — Stifterne av Oslonett
- `verdt.html` — Facts og episoder
- `www1993-info.html` — Første webserver (1993–1996)
- `aa-info.html` — Arctic Adventours («Best of The Web» 1994)
- `ol94-info.html` — OL '94 Lillehammer-tjeneste
- `eu94-info.html` — EU-avstemning 1994
- `cw-info.html` — ComputerWorld på web
- `kvasir-info.html` — Kvasir søkemotor
- `mb-info.html` — Morgenbladet på web
- `iv-info.html` — Intervett/internettkurs
- `omp-info.html` — Oslonett Markedsplassen
- `rondo-info.html` — Rondo
- `www.sn.no.html` — Schibsted Nett (1996–97)

### 5.3 Oslonett Aksess (`/Aksess/`)

Komplett gjengivelse av ISP-tjenestesidene fra 1990-tallet:

- `Aksess.html` — Internett-tilgang via dial-up og SLIP/PPP
- `Homes.html` — Hjemmesider for kunder
- `info.html` — Generell informasjon om tjenestene
- `PrivatWWW.html` — Privat WWW-hosting
- `SisteNytt.html` — Siste nytt fra Aksess
- `/Hjelp/` — FAQ og hjelpedokumentasjon
- `/Internet/` — Internettressurser og -tjenester
- `/Mac/` — Mac-spesifikk programvare og konfigurasjons-veiledning
- `/Win/` — Windows-spesifikk konfigurasjon (Eudora, Mosaic)

### 5.4 Schibsted Nett AS (`/sn/`)

Innhold fra den etterfølgende eieren 1995–1997:

- `index.html` — Startsiden for Schibsted Nett (med gammelt design)
- `visjon.html` — Selskapets visjon (bevart originalinnhold)
- `ansatte.html` — Ansatteliste med navn og e-post (44 ansatte i 1995)
- `historie.html` — Bedriftens historie
- `snnett.html` — SNNett produktomtale

### 5.5 Innholdsportal (`/innhold/`)

Oslonetts web-katalog med 8 kategorier:
- `uh/` — Underholdning
- `sp/` — Sport
- `nl/` — Næringsliv
- `org/` — Organisasjoner
- `rl/` — Reiseliv
- `sh/` — Kjøp og salg
- `me/` — Media
- `div/` — Diverse

### 5.6 Newsdesk (`/newsdesk/`)

Bevart nyhetsredaksjonssystem fra februar 1996. Inneholder:
- Avisartikler med auto-publiseringssystem
- Tematiske saker (bl.a. Tsjetsjenia-dekning)
- Arkivsystem med tidsstempel

### 5.7 ComputerWorld (`/CW` — fil, ikke mappe)

Katalogfil som peker til `/historie/CW/` — inneholder digitaliserte utgaver av ComputerWorld fra 1993–1995.

### 5.8 EXPO94 (`/EXPO94/`)

Nettstedsmateriale fra en utstilling i 1994, med kart, messeoversikt og konferansekatalog.

---

## 6. Funksjonelle egenskaper

### 6.1 Søk

Klient-side fulltekstsøk med Lunr.js dekker 23+ sider, inkludert ComputerWorld-arkivinnholdet. Dette er en moderne reimplementering av det opprinnelige WAIS-baserte søket fra 1990-tallet.

### 6.2 Tidssensitive bilder

Header-bildet på forsiden endres automatisk etter tidspunkt (natt, morgen, dag, aften) — en funksjon som opprinnelig ble gjort via Perl CGI (`rndtopp.cgi`) og nå er reimplementert i JavaScript (`onheaders.js`).

### 6.3 Alumni-registrering

`alumni.html` inneholder et skjema for tidligere ansatte og eiere til å registrere seg til en mailingliste. CGI-backend (`paameld.cgi`) er ikke aktiv, men skjemaet er bevart historisk.

### 6.4 Imagemaps

Klikbare bildekart (HTML `<ismap>`) brukes til navigasjon på flere sider — en karakteristisk 1990-talls teknikk.

### 6.5 Server Side Includes (SSI)

Mange sider inneholder SSI-direktiver som `<!--#config timefmt="%d.%m.%y, kl %H:%M" -->`. Disse er ikke aktive (GitHub Pages støtter ikke SSI), men er bevart i kildekoden.

---

## 7. Grafisk design og estetikk

Nettstedet gjenspeiler tydelig 1990-tallets webdesign:

- **Fargepalett**: Hvit tekst på mørk/blå bakgrunn (`.whiteonblue`-klassen)
- **Tabellbasert layout**: All posisjonering gjøres med `<table>`, `width`-attributter og `valign`/`align`
- **Grafikkformat**: GIF (animerte), JPEG, XBM (X BitMap — svært sjeldent format)
- **Font-stack**: Arial, Verdana, Helvetica, Helvetica, sans-serif
- **Navigasjon**: Imagemaps og tekstlenker side om side
- **Ingen responsivt design**: Faste breddeangivelser i prosent på tabeller

---

## 8. Sentrale personer

Basert på dokumenterte stiftere og ansatte:

| Navn | Rolle |
|------|-------|
| Kjell Øystein Arisland | Initiativtaker, sendte stiftelsesmailen 9.12.1991 |
| Tore Solvar Karlsen | Administrerende direktør |
| Steinar Kjærnsrød | Leder webavdeling |
| Gisle Hannemyr | Aksess-tjenester |
| Hans Petter Holen | Nettverksutvikling |
| Knut Falchenberg | Direktør Profesjonelle tjenester |

---

## 9. Teknisk tilstand og observasjoner

### 9.1 Hva fungerer i dag

- Statisk HTML vises uten problemer i moderne nettlesere
- CSS-styling fungerer (med forbehold for manglende responsivitet)
- JavaScript søkefunksjon (Lunr.js) fungerer
- Tidssensitiv header-logikk fungerer via `onheaders.js`
- Navigasjon mellom sider fungerer der lenker ikke er brutte

### 9.2 Hva ikke fungerer

- **CGI-scripts** er ikke aktive — GitHub Pages støtter ikke server-side kode
- **SSI-direktiver** vises ikke — `<!--#config-->` etc. prosesseres ikke
- **WAIS-søket** (`search.cgi`) er erstattet av Lunr.js
- **Skjemainnsending** (alumni, påmelding) fungerer ikke uten backend
- **Mange interne lenker** er trolig brutte (til ressurser som ikke ble migrert)
- **Imagemaps** basert på eksterne kartfiler kan ha brutte lenker

### 9.3 Kodekvalitet

Koden reflekterer teknikkene fra sin tid:
- Ingen semantisk HTML (ingen `<nav>`, `<article>`, `<main>` osv.)
- Layout-tabeller i stedet for CSS
- Inline-attributter for styling (`bgcolor`, `border`, `align`)
- Blanding av XHTML og HTML4-syntaks
- Noen filer har `<?xml version="1.0"?>` prolog mens andre bruker ren HTML2-syntaks

---

## 10. Kulturell og historisk signifikans

Nettstedet er unikt i norsk digital kulturarv:

1. **Første komersielle internettselskap i Norge** — Oslonett ble stiftet bare noen måneder etter at WWW ble offentlig tilgjengelig (Tim Berners-Lee annonserte WWW i august 1991)
2. **Pionerprosjekter** bevart: OL '94-tjenesten, EU-avstemningsresultat i sanntid, tidlig nettavis (CW), søkemotor (Kvasir)
3. **UNESCO-anerkjennelse** via Norges dokumentarv
4. **Teknologisk tidskapsel**: Kodebasen er en autentisk representasjon av webutviklingspraksis fra 1993–1997

Dette nettstedet er både en utstilling av historisk innhold og et historisk artefakt i seg selv.

---

*Analysert fra kildefilene i repoet skibohemen/oslonett, mai 2026.*
