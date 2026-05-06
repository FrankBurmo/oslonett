# Ressursaudit: Brutte lenker og ubrukte ressurser

> **Analysedato:** 5. mai 2026  
> **Analysert av:** GitHub Copilot (automatisert skript + manuell gjennomgang)  
> **Metode:** Python-skript som parser alle HTML/CSS/JS/CGI-filer for ressursreferanser og krysssjekker mot faktisk filsystem  
> **Skript:** `docs/_link_audit.py`

---

## Sammendrag

| Metrikk | Antall |
|---------|--------|
| Totalt antall filer i repoet | **10 530** |
| Kildefiler analysert (HTML/CGI/CSS/JS) | **8 593** |
| Ressursfiler analysert (alle typer) | **10 259** |
| Brutte interne referanser funnet | **12 310** |
| Ubrukte ressurser funnet | **7 517** |

**Viktig tolkning:** Tallene er store, men svært mye av dette er systemisk og lar seg forklare med noen få rotårsaker. Auditskriptet rapporterte opprinnelig ~11 361 CW-relaterte brutte referanser (92 %), men en etterfølgende manuell sjekk viser at repoet allerede inneholder en git-symlink `CW → historie/CW` (mode 120000, tilstede på `main`). Dette betyr at 7 574 av disse referansene *ikke er reelt brutte* på GitHub Pages — to av tre CW-ressurser løses automatisk via symlinken. Kun én manglende fil (`maphelp.html`) utgjør et reelt gjenstående problem (~3 787 refs).

---

## DEL 1 — Brutte interne referanser

### 1.1 Kategorioversikt

| # | Kategori | Antall refs | Antall unike filer berørt |
|---|----------|-------------|--------------------------|
| 1 | CW: `maphelp.html` mangler (sti-prefix-refs løst via symlink) | 3 787 *(var 11 361 — se §1.2)* | ~3 787 |
| 2 | Manglende innholdskategorier | 208 | ~30 |
| 3 | CGI-skript (ikke tilgjengelig på GitHub Pages) | 139 | ~20 |
| 4 | Morgenbladet bakgrunnsbilde feil sti | 111 | 111 |
| 5 | Rondo-interne mangler | 107 | ~50 |
| 6 | Gammel serversti `/me/ts/` | 75 | ~50 |
| 7 | EU-interne mangler | 61 | ~30 |
| 8 | Schibsted Nett (sn/) interne mangler | 52 | ~20 |
| 9 | EXPO94/SystemSikk-bilder | 44 | 2 |
| 10 | Newsdesk-interne mangler | 42 | ~15 |
| 11 | Gopher-protokoll (avviklet) | 20 | ~10 |
| 12 | `/NYOMP/`-sti (gammel server) | 20 | ~10 |
| 13 | SSI-komponenter eksisterer ikke | 12 | 4 |
| 14 | news:-protokoll (NNTP, avviklet) | 8 | 4 |
| 15 | WAIS-protokoll (avviklet) | 1 | 1 |
| 16 | Diverse / ukategorisert | 9 | ~8 |
| **Totalt** | | **12 310** | |

---

### 1.2 Kategori 1 — CW-filer og sti-prefix *(revidert: 3 787 gjenstående brutte refs)*

**Oppdatert status (6. mai 2026):** Auditskriptet rapporterte opprinnelig 11 361 brutte CW-referanser fordelt på tre ressurser. En manuell sjekk av git-treet viser imidlertid at repoet **allerede inneholder en git-symlink** `CW → historie/CW` (git object mode `120000`, tilstede på `main`-branchen). På GitHub Pages, som kjører på Linux og respekterer git-symlinker for statiske sider (`.nojekyll`), betyr dette at stier under `/CW/` løses korrekt.

| Sti (som artikler peker til) | Status | Berørte refs |
|------------------------------|--------|--------------|
| `/CW/gifs/artmap.gif` | ✅ Løst via symlink `CW → historie/CW` — filen finnes på `/historie/CW/gifs/artmap.gif` | 3 787 |
| `/CW/Hjelp.html` | ✅ Løst via symlink `CW → historie/CW` — filen finnes på `/historie/CW/Hjelp.html` | 3 787 |
| `/historie/CW/maphelp.html` | ❌ Eksisterer ikke i repoet — ingen symlink kan hjelpe | 3 787 |

**Gjenstående konsekvens:**
- `artmap.gif` og `Hjelp.html` fungerer sannsynligvis korrekt på live-nettstedet via symlinken
- Imagemap-navigasjonen er trolig funksjonell
- `maphelp.html` er ikke-funksjonell (hjelp-lenke) — dette er det eneste gjenværende CW-problemet

**Gjenstående fiks:** `maphelp.html` må enten gjenopprettes fra backup eller opprettes på nytt for å fikse de resterende 3 787 brutte referansene.

---

### 1.3 Kategori 2 — Manglende innholdskategorier *(208 brutte refs)*

Oslonetts innholdskatalog (`/innhold/`) refererte til en rekke underkategorier under `/nl/`, `/gs/`, `/uh/` osv. som ikke er bevart i repoet.

| Manglende sti | Type | Refs |
|--------------|------|------|
| `/nl/adv/` | Næringsliv: Advokater | 10 |
| `/nl/dt/` | Næringsliv: Data/teknologi | 10 |
| `/gs/` | Gul/hvit side-tjeneste | 10 |
| `/nl/fi/` | Næringsliv: Finans | 10 |
| `/nl/kons/` | Næringsliv: Konsulenter | 10 |
| `/nl/mes/` | Næringsliv: Messe | 10 |
| `/me/ts/ne/` | Media: Nettsteder | 10 |
| `/nl/oi/` | Næringsliv: Olje/industri | 10 |
| `/nl/ndiv/` | Næringsliv: Diverse | 10 |
| `/nl/rek/` | Næringsliv: Reklame | 10 |
| `/nl/ja/` | Næringsliv: Jus/advokat | 10 |
| `/uh/` | Underholdning (toppnivå) | 7 |
| `/sp/` | Sport | 7 |
| `/nl/` | Næringsliv | 7 |
| `/rl/` | Reiseliv | 7 |
| `/sh/` | Kjøp og salg | 7 |
| `/me/` | Media | 7 |
| `/div/` | Diverse | 7 |
| `/org/` | Organisasjoner | 6 |

**Årsak:** Disse kategorisidene var dynamisk generert via CGI (søkeindeks) og ble aldri bevart som statiske filer. Innholdet i `/innhold/`-mappen har en katalogstruktur, men selve underkategori-sidene er borte.

---

### 1.4 Kategori 3 — CGI-skript ikke tilgjengelig *(139 brutte refs)*

GitHub Pages støtter ikke server-side kode. Alle CGI-skript i nettstedet er utilgjengelige.

| CGI-endpoint | Funksjon | Refs |
|-------------|---------|------|
| `/cgi-bin/SN-wdeskwais.pl` | WAIS-søk for Newsdesk | 53 |
| `$ENV{'...'}` / `$_` | Perl-variabler i CGI-templates (ikke ekte URLs) | 22 |
| `/oslonett/cgi/search.cgi` | Fulltekstsøk (erstattet av Lunr.js) | 5 |
| `/cgi-bin/mailit` | E-post CGI | 6 |
| Andre `.cgi`-referanser | Diverse | 53 |

**Merk:** `$ENV{...}` og `$_`-verdier er Perl-variabler i CGI-maler som ved en feil har blitt fanget opp som URL-verdier av parseren. Disse er ikke reelle brutte lenker, men viser at noen CGI-templates er bevart ukompilert.

---

### 1.5 Kategori 4 — Morgenbladet bakgrunnsbilde feil sti *(111 brutte refs)*

Samtlige 111 Morgenbladet-artikler i `/historie/MB/utg/9524/` og `/historie/MB/utg/9525/` har denne feilen på linje 6:

```html
<body background="/me/ts/historie/MB/gifs/mb-bg.gif">
```

Stien `/me/ts/` var et prefiks på den gamle Schibsted Nett-serveren og eksisterer ikke her. Bildefilen `mb-bg.gif` finnes i `/historie/MB/gifs/mb-bg.gif`.

**Enkel fiks:** Endre `/me/ts/historie/MB/gifs/mb-bg.gif` → `/historie/MB/gifs/mb-bg.gif` i alle 111 filer (automatiserbart med sed/skript).

---

### 1.6 Kategori 5 — Rondo-interne mangler *(107 brutte refs)*

`/historie/Rondo/` inneholder Oslonetts «Rondo»-tjeneste (URL of the Week + nyhetsstrøm). Flere ressurser mangler:

| Manglende ressurs | Refs | Merknad |
|------------------|------|---------|
| `uotw.html` | 8 | «URL of the Week»-sider, ikke bevart |
| `/historie/Rondo/URL-archive/URL-.html` | 7 | Indeksfil med tomt nummer (mønster-URL) |
| `/Rondo/gifs/eng.gif` | 3 | Feil sti — bør være `/historie/Rondo/gifs/eng.gif` |
| `/Rondo/gifs/tshirt-8.50.gif` | 3 | Feil sti |
| `Rondo.html` | 4 | Ikke bevart |
| `NEI!` / `nei!` | 7 | **Plassholdere** — href-attributter satt til `NEI!` som dummy-verdi |
| `BASTIAN` | 2 | Plassholder-tekst i href |
| `Kommer snart!` | 2 | Plassholder-tekst i href |
| `test` | 2 | Tesverdi i href |
| `www.fagpressen.no` | 2 | Ekstern URL uten protokoll-prefiks |

**Interessant funn:** Verdier som `NEI!`, `BASTIAN`, `Kommer snart!` og `test` i `href`-attributter avslører at Rondo-nettstedet hadde uferdig innhold da det ble bevart — dette er et autentisk historisk snapshot.

---

### 1.7 Kategori 6 — Gammel serversti `/me/ts/` *(75 brutte refs)*

Stier som starter med `/me/ts/` peker til en gammel Schibsted-server-struktur:

| Manglende sti | Refs |
|--------------|------|
| `/me/ts/cw/` | 16 |
| `/me/ts/ne/` | 10 |
| `/me/ts/mb/` | 2 |
| `/me/ts/historie/MB/gifs/mb-bg.gif` | 111 (se kat. 4) |

Disse ressursene ble aldri migrert fra Schibsted Nett sin server til GitHub Pages.

---

### 1.8 Kategori 7–8 — EU og Schibsted Nett mangler *(113 brutte refs)*

**EU (61 refs):** Resultat-tjenesten fra EU-avstemningen 1994 mangler interne lenker — sannsynligvis ikke bevart fullt ut.

**Schibsted Nett/sn/ (52 refs):**

| Manglende ressurs | Refs | Type |
|------------------|------|------|
| `/on/www/` | 5 | Oslonett-tjenester, ikke bevart |
| `aboform.html` | 2 | Abonnementsskjema |
| `konsform.html` | 2 | Konsulentkontakt-skjema |
| `/me/ts/mb/`, `/me/ts/cw/` | 4 | Gammel serversti |
| `/cgi-bin/mailit` | 2 | CGI-skript |
| `oslonett-nett.gif` | 1 | Manglende bilde |
| `ip.map` | 1 | Manglende imagemap-fil |
| `/Internett/index.html` | 1 | Ikke bevart |
| Diverse | ~35 | Ulike tjenestesider |

---

### 1.9 Kategori 9 — EXPO94/SystemSikk-bilder *(44 brutte refs)*

Filen `EXPO94/lev/SystemSikk/ss_info.html` (og en kopi i `orginaler/`-undermappen) lenker til 22 bilder med navnemønster `ss_info1.gif` til `ss_info22.gif`. Ingen av disse bildene er bevart i repoet.

Dette er en foredragspresentasjon fra EXPO '94 om systemsikkerhet — bildene var antakelig diaslide-illustrasjoner som ikke ble tatt med.

---

### 1.10 Kategori 10 — Newsdesk-interne mangler *(42 brutte refs)*

| Manglende ressurs | Refs | Merknad |
|------------------|------|---------|
| `/cgi-bin/SN-wdeskwais.pl` | 53 | WAIS-søk (CGI) |
| `$ENV{...}` Perl-variabler | 14 | CGI-template-variabler |
| `/newsdesk/html/960206-07.html` | 3 | Artikkel ikke bevart |
| `/newsdesk/html/960211-02.html` | 3 | Artikkel ikke bevart |
| `/newsdesk/html/960206-04.html` | 2 | Artikkel ikke bevart |
| `/newsdesk/html/960207-08.html` | 2 | Artikkel ikke bevart |

---

### 1.11 Kategori 11–14 — Avviklede protokoller *(29 brutte refs)*

Disse er historisk interessante funn — protokoller som ble brukt på 1990-tallet men er nå avviklet:

| Protokoll | Refs | Eksempler |
|-----------|------|-----------|
| `gopher://` | 20 | `gopher://drs.uninett.no/11/uninettdb/`, `gopher://gopher.enews.com/11/` |
| `news:` | 8 | `news:news.announce.newusers`, `news:news.answers` |
| `wais://` | 1 | `wais://quake.think.com:210/directory-of-servers` |

Disse er i `/Aksess/Internet/`-seksjonene og `/historie/IV/kurs/`-kursmaterialet — primært som eksempler på internettjenester fra 1994.

---

### 1.12 Kategori 13 — SSI-komponenter *(12 brutte refs i 4 filer)*

Filene `alumni.html`, `paamelding.html`, `program.html` og `mozilla_4_7.html` refererer til SSI-komponenter:

| SSI-komponent | Refs | Funksjon |
|--------------|------|---------|
| `/ssi/head_main.html` | 3 | Toppmeny-komponent |
| `/ssi/left_historie.html` | 3 | Venstre-meny-komponent |
| `/ssi/address_main.html` | 3 | Footer-komponent |
| `/ssi/thanks.html` | 1 | Takkeside etter påmelding |

Disse er Server Side Include-filer som aldri ble bevart — de ble aldri synlig som egne filer (de ble prosessert server-side). GitHub Pages prosesserer ikke SSI, så de ville ikke virket uansett.

---

## DEL 2 — Ubrukte ressurser

### 2.1 Oversikt per filtype

| Filtype | Antall ubrukte | Andel av totalt |
|---------|----------------|-----------------|
| `.html` | 6 154 | 60 % |
| `.gif` | 1 159 | 11 % |
| `.txt` | 57 | 1 % |
| `.jpg` | 44 | < 1 % |
| `.pl` (Perl) | 30 | < 1 % |
| `.xbm` (X BitMap) | 19 | < 1 % |
| `.cgi` | 17 | < 1 % |
| `.json` | 17 | < 1 % |
| `.map` | 12 | < 1 % |
| `.htm` | 3 | < 1 % |
| `.zip` | 2 | < 1 % |
| `.ppm` | 2 | < 1 % |
| `.css` | 1 | < 1 % |
| **Totalt** | **7 517** | |

---

### 2.2 Ubrukte HTML-filer (6 154 filer)

#### De største grupperingene

| Mappe | Antall ubrukte HTML | Årsak |
|-------|---------------------|-------|
| `historie/OL/meldinger/` | 1 129 | Se analyse under |
| `historie/CW/utg/9605/` | 74 | CW-artikler ikke lenket |
| `historie/CW/utg/9545/` | 66 | CW-artikler ikke lenket |
| `historie/CW/utg/9541/` | 65 | CW-artikler ikke lenket |
| `historie/CW/utg/9547/` | 61 | CW-artikler ikke lenket |
| `historie/CW/utg/9343/` | 60 | CW-artikler ikke lenket |
| `historie/CW/utg/9430/` | 60 | CW-artikler ikke lenket |
| `historie/CW/utg/9537/` | 58 | CW-artikler ikke lenket |
| `historie/CW/utg/9543/` | 58 | CW-artikler ikke lenket |
| `historie/CW/utg/9511/` | 56 | CW-artikler ikke lenket |
| `historie/CW/utg/9514/` | 56 | CW-artikler ikke lenket |
| `historie/CW/utg/9604/` | 53 | CW-artikler ikke lenket |
| `historie/CW/utg/9606/` | 52 | CW-artikler ikke lenket |
| `historie/CW/utg/9507/` | 51 | CW-artikler ikke lenket |
| `historie/CW/utg/9431/` | 49 | CW-artikler ikke lenket |
| *(mange flere CW-utgaver)* | ~2 000+ | CW-artikler ikke lenket |

#### OL/meldinger — 1 129 ubrukte HTML-filer

Mappen `historie/OL/meldinger/` inneholder 1 129 nummererte HTML-filer (fra `1.html` til `>600.html`). Dette er individuelle pressemeldinger og nyhetsoppdateringer fra OL '94 i Lillehammer. 

**Årsak til at de er ubrukte:** De ble opprinnelig vist via et CGI-basert meldingslister-skript som genererte en indeks dynamisk. Ingen statisk `index.html` lenker til de individuelle meldingsfilene. Filene er komplett bevart, men utilgjengelige for brukere som ikke kjenner URL-mønsteret direkte.

#### CW-artikler — ~3 800+ ubrukte HTML-filer

ComputerWorld-artiklene er lagret i `historie/CW/utg/YYUU/` (år+uke-format, f.eks. `9430` = 1994, uke 30). Artiklene er ikke lenket fra noen fungerende navigasjon fordi:
1. CW-imagemap-navigasjonen er brutt (se Del 1, kategori 1)
2. Den opprinnelige søkefunksjonen (CGI/WAIS) er ikke tilgjengelig
3. De statiske utgaveindeksene peker til `/CW/...`-stier som er feil

---

### 2.3 Ubrukte bildefiler (1 224 bilder)

#### De største grupperingene

| Mappe | Antall ubrukte bilder | Merknad |
|-------|----------------------|---------|
| `historie/OL/gifs/` | 339 | OL '94-bilder, ikke lenket fra noen HTML |
| `graphics/` | 144 | Blanding av XBM-ikoner og GIF |
| `img/` | 73 | Diverse bilder inkl. gamle header-varianter |
| `gifs/on/` | 66 | Oslonett-logoer og ikoner |
| `EXPO94/gifs/` | 48 | Foredragsfoto og messemateriell |
| `img/margmeny/` | 34 | Meny-bilder ikke lenger brukt |
| `graphics/people/` | 31 | Personbilder (ansatte?) |
| `historie/Rondo/eng/gifs/` | 26 | Rondo engelsk versjon |
| `historie/gifs/` | 26 | Diverse historiske bilder |
| `graphics/medlem/` | 25 | Medlemsikoner |
| `historie/IV/gifs/` | 25 | Internettkurs-bilder |
| `img/hovedmeny/` | 22 | Hovedmeny-bilder |
| `Aksess/graphics/` | 21 | ISP-tjeneste-ikoner |
| `EXPO94/lev/Coltux/` | 21 | EXPO '94 leverandørmateriell |
| `historie/AA/` | 21 | Arctic Adventours bilder |

#### Eksempler på interessante ubrukte bilder

**`Aksess/graphics/`** (21 bilder — ikke referert):
- `Aksess-icon.gif`, `Aksess.gif`, `Internet.gif`, `ON.gif`
- `apple_logo.gif`, `win_logo.gif`, `globus.gif`
- `xmas.lites.gif` (julepynt-animasjon!)
- `construction.gif` (den ikoniske 1990-talls «under construction»-GIF)

**`EXPO94/gifs/`** (48 bilder — ikke referert):
- `3com.gif`, `Ballmer.gif`, `Hamilton.gif`, `Mandeville.gif`, `Metcalfe.gif`
- Foredragsholder-bilder fra EXPO '94

**`graphics/people/`** (31 bilder — ikke referert):
- Sannsynligvis ansatte-bilder

---

### 2.4 Andre ubrukte ressurser

| Type | Antall | Eksempler |
|------|--------|-----------|
| Perl-skript (`.pl`) | 30 | CGI-hjelpebiblioteker, søkeskript |
| Tekst-filer (`.txt`) | 57 | Diverse dokumentasjon |
| X BitMap (`.xbm`) | 19 | `graphics/binary.xbm`, `ftp.xbm` — FTP-katalogikoner |
| CGI-skript (`.cgi`) | 17 | Ikke tilgjengelig og ikke referert |
| JSON-filer (`.json`) | 17 | Lunr.js søkeindeks (disse *er* i bruk, men ikke via HTML-refs — falsk positiv) |
| Imagemap-filer (`.map`) | 12 | Klikk-kart-koordinatfiler |
| Zip-filer (`.zip`) | 2 | Ukjent innhold |
| PPM-bilder (`.ppm`) | 2 | Råbildefiler (ikke nettleser-visbare) |
| CSS-fil (`.css`) | 1 | `present.css` — mulig duplikat/gammel |

**Merk om JSON-filer:** Lunr.js søkeindeks-chunkene (`js/index/index-0.json` til `index-14.json`) fanges opp som «ubrukte» fordi de lastes dynamisk via `fetch()` i JavaScript, ikke via statiske HTML-referanser. Dette er en forventet falsk positiv i analysen.

---

## DEL 3 — Oppsummering og anbefalinger

### 3.1 Høy-prioriterte mangler som lar seg fikse

| # | Problem | Berørte filer | Kompleksitet | Gevinst |
|---|---------|--------------|--------------|---------|
| A | ~~Feil sti-prefix på CW-filer (`/CW/` → `/historie/CW/`)~~ | ~~3 787 CW-artikler~~ | ✅ **Allerede løst** — git-symlink `CW → historie/CW` finnes på `main` | Fikser 7 574 refs (allerede gjort) |
| B | `maphelp.html` eksisterer ikke | 3 787 CW-artikler | Middels (gjenopprette fil) | Fikser 3 787 brutte refs |
| C | Morgenbladet bakgrunnsbilde feil sti | 111 MB-filer | Lav (skript-søk/erstatning) | Fikser 111 brutte refs |
| D | OL/meldinger-filer ikke lenket | 1 129 HTML-filer | Middels (statisk indeks) | Gjør 1 129 filer tilgjengelige |
| E | SSI-komponenter mangler | 4 jubileumssider | Middels (inline innhold) | Fikser 12 brutte refs |

### 3.2 Naturlig ufikserbare mangler (aksepterte brudd)

Disse er forventet og akseptert som konsekvens av at arkivet er bevart fra en annen tid:

| Kategori | Begrunnelse |
|----------|-------------|
| CGI-skript ikke tilgjengelig | GitHub Pages støtter ikke server-side kode. Forventes. |
| Avviklede protokoller (gopher, news, wais) | Protokollene eksisterer ikke lenger. Historisk korrekt å beholde. |
| Manglende innholdskategorier | Dynamisk CGI-innhold som aldri eksisterte som statiske filer. |
| Rondo-plassholdere (`NEI!`, `BASTIAN`) | Autentisk historisk snapshot av uferdig innhold. |
| `/me/ts/`-stier | Gammel serverstruktur som ikke ble migrert. Historisk korrekt. |

### 3.3 Vurdering av ubrukte ressurser

| Gruppe | Anbefaling |
|--------|-----------|
| OL/meldinger (1 129 HTML) | Lag en statisk indeks-side som lenker til alle meldingene |
| CW-artikler (~3 800+ HTML) | Fixes indirekte ved å fikse sti-problemet (punkt A) |
| OL/gifs (339 GIF) | Tilhører OL/meldinger-systemet — fikses med indeksen |
| EXPO94/gifs (48 GIF) | Vurder å lage en gallerisside |
| Aksess/graphics (21 GIF) | Bevaring som de er — de var del av ISP-sidene |
| graphics/people (31 GIF) | Identifiser og integrer i hvem.html eller alumniside |
| Lunr.js JSON-indeks (17) | Falske positive — faktisk i bruk |
| Perl-skript og CGI (47) | Bevar som historiske artefakter, rydd ikke opp |

---

## Tekniske noter om analysen

### Hva skriptet gjør
1. Scanner alle `.html`, `.htm`, `.cgi`, `.pl`, `.css`, `.js`-filer
2. Ekstraherer alle `href`, `src`, `action`, `background`, `usemap`-attributter
3. Ekstraherer SSI-includes (`<!--#include ...-->`)
4. Ekstraherer CSS `url(...)`-referanser
5. Normaliserer rot-relative (`/path`) og relative (`../path`) URLer
6. Sjekker om den normaliserte stien eksisterer på filsystemet
7. Identifiserer alle filer som aldri refereres

### Begrensninger
- **Dynamiske referanser:** Ressurser lastet via `fetch()` eller `XHR` i JavaScript fanges ikke opp (forklarer de 17 «ubrukte» JSON-filene)
- **CGI-genererte lenker:** Ressurser som bare refereres via CGI-output fanges ikke opp
- **Imagemap-stier:** `.map`-filer kan bli markert som «ubrukte» selv om de brukes via `usemap`-attributt på en annen måte
- **Ekstern-til-intern redirect:** GitHub Pages CNAME-omdirigering fanges ikke opp
- **Perl-variabler i URLs:** Noen `$ENV{...}`-verdier ble plukket opp som URL-er og genererer falske brutte referanser

---

*Analyse utført med `docs/_link_audit.py` mot filsystemet i skibohemen/oslonett, mai 2026.*
