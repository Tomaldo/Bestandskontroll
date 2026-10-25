# Bestandskontroll – arbeidsregler for Claude Code

Dette repoet kjører kontroller på bestandsdata for pensjon og forsikring. Hver oppgave er en
sak i Linear-prosjektet **Bestandskontroll** (team Aktuardemo, saker `AKT-n`). Les saken
(bakgrunn, regel, akseptkriterier, «ikke i scope») før du starter, og rapporter tilbake på
saken når du er ferdig.

## Kommandoer

| Hva | Kommando |
|---|---|
| Alle tester (må være grønne før du rapporterer) | `python -m pytest` |
| Rapport mot fasit | `python -m bestandskontroll data/bestand_syntetisk.csv --fasit data/fasit.json` |
| Rapport med hvert funn | `python -m bestandskontroll data/bestand_syntetisk.csv --detaljer` |
| Regenerere data og fasit | `python tools/generer_bestand.py` – **bare** når saken endrer spesifikasjonen, aldri for å få tester grønne |

Avhengigheter: Python 3.10+ og pytest (`pip install -r requirements.txt`). Ingen andre.

## Struktur

```
bestandskontroll/
  modell.py              Polise og Funn (frosne dataklasser)
  innlesing.py           les_bestand(): semikolon, desimalkomma, tomt/utolkbart felt -> None
  kontroller/
    basis.py             Kontroll (grunnklasse): navn, beskrivelse, alvorlighet, kjor()
    __init__.py          ALLE_KONTROLLER – registeret. Ikke registrert = ikke i bruk.
    <en fil per kontroll>
  kjoring.py             kjor_kontroller() -> Rapport
  fasit.py               Fasit.les(), sammenlign()
  cli.py                 python -m bestandskontroll
data/
  bestand_syntetisk.csv  604 syntetiske poliser med plantede feil
  fasit.json             hvilke poliser hver kontroll skal slå ut på – kontrakten
tests/
  conftest.py            fixturen `gyldig` lager en polise ingen kontroll slår ut på
  test_fasit.py          kjører automatisk for alt i ALLE_KONTROLLER
tools/
  generer_bestand.py     lager data/ med fast seed; referansereglene som gir fasiten står nederst
```

## Slik legger du til en kontroll

1. Ny modul `bestandskontroll/kontroller/<snake_case>.py` med klassen `<PascalCase>(Kontroll)`.
   `navn` er lik klassenavnet og lik nøkkelen i `data/fasit.json`. `beskrivelse` er regelen
   med samme ordlyd som i saken. Følg `ugyldig_fodselsdato.py` som mal.
2. Registrer en instans i `ALLE_KONTROLLER` i `bestandskontroll/kontroller/__init__.py`,
   og legg klassen til i `__all__`.
3. Enhetstester i `tests/test_<snake_case>.py` med `gyldig`-fixturen: minst ett tilfelle som
   gir funn, ett som ikke gir funn, og grensetilfellene saken nevner. `None` i feltet
   kontrollen ser på skal ikke gi funn – det er `ManglendeFelt` sitt ansvar.
4. Kjør `python -m pytest`. `test_fasit.py` plukker opp den nye kontrollen av seg selv; den er
   grønn når kontrollen slår ut på nøyaktig polisene fasiten sier, verken flere eller færre.
5. Kjør rapportkommandoen og se at kontrollen står med `Fasit = OK`.

## Regler

- Kontroller er rene funksjoner: ingen I/O, ingen `date.today()`, ingen tilstand mellom kall.
  Ett funn per polise per kontroll, i filens rekkefølge, med en melding skrevet for den som
  skal rette feilen (ta med verdien som var gal).
- `data/fasit.json` er kontrakten. Den endres **aldri** for å få tester grønne. Mener du at
  fasiten er feil: stopp, og skriv hvorfor som kommentar på saken.
- `innlesing.py`, `modell.py` og datafilen endres ikke uten at saken sier det eksplisitt.
- Hold deg til saken. Ser du noe annet som burde fikses: nevn det i rapporten, ikke fiks det.
- Norsk i navn, meldinger, tester og kommentarer. ASCII i identifikatorer
  (`fodselsdato`, `kjonn`, `aarlig_ytelse`), æøå i tekst som leses av mennesker.
- Ingen nye avhengigheter utover standardbiblioteket og pytest.
- Ved tvil om regelen: spør på saken i stedet for å gjette. En presis avgrensning i saken
  er verdt mer enn en rask implementasjon.

## Arbeidsflyt mot Linear

1. Hent saken fra Linear (prosjekt «Bestandskontroll»). Sett den til *In Progress*.
2. Arbeid på en gren: `akt-<saksnummer>-<kort-navn>`, for eksempel `akt-9-negativ-premiereserve`.
   Små commits med beskrivende meldinger på norsk.
3. Når akseptkriteriene er oppfylt og `python -m pytest` er grønn: skriv rapporten under som
   kommentar på saken og sett saken til *In Review*. Lag PR hvis repoet har en fjernkopi;
   ellers nevn grenen i kommentaren.
4. Ikke lukk saken selv. Det gjør den som bestilte den, etter gjennomgang.

### Mal for rapport på saken

```
**Ferdig til gjennomgang**

Endret: <filer>

Akseptkriterier:
- <kriterium 1>: oppfylt – <hvordan>
- <kriterium 2>: oppfylt – <hvordan>
- ...

Tester: `python -m pytest` → <N> passed. Fasit for <Kontroll>: OK (<antall> poliser).

Utenfor scope / observasjoner: <alt du så, men ikke rørte – eller «ingen»>

Gren: <grennavn> (PR: <lenke>, hvis laget)
```
