# Bestandskontroll

Kontroller på bestandsdata for pensjon og forsikring, skrevet i Python med bare
standardbiblioteket. Repoet er laget som demo av KI-assistert utvikling styrt fra Linear:
Claude Desktop skriver sakene, Claude Code implementerer dem her, og testene mot
`data/fasit.json` avgjør om det ble riktig. Reglene Claude Code jobber etter står i
[CLAUDE.md](CLAUDE.md).

## Kom i gang

```
pip install -r requirements.txt
python -m pytest
python -m bestandskontroll data/bestand_syntetisk.csv --fasit data/fasit.json
```

Den siste kommandoen skriver en rapport med antall funn per kontroll, om funnene stemmer
med fasiten, og hvilke kontroller fasiten venter på som ikke er implementert ennå.
`--detaljer` lister hvert enkelt funn med linjenummer i filen.

## Slik henger det sammen

- **Innlesingen** (`bestandskontroll/innlesing.py`) leser filen og dømmer aldri: et felt som
  er tomt eller ikke lar seg tolke blir `None`, slik at kontrollene kan rapportere det på
  riktig polise.
- **Kontrollene** (`bestandskontroll/kontroller/`) er rene funksjoner. Hver kontroll har et
  stabilt navn, én setning som beskriver regelen, og returnerer ett funn per polise med
  avvik. Registeret `ALLE_KONTROLLER` bestemmer hva som kjøres.
- **Fasiten** (`data/fasit.json`) sier hvilke poliser hver kontroll skal slå ut på i den
  syntetiske bestanden. Den beregnes av referansereglene i `tools/generer_bestand.py`,
  uavhengig av kontrollene, og er kontrakten: `tests/test_fasit.py` sammenligner hver
  registrert kontroll med den, og plukker opp nye kontroller automatisk.

## Datagrunnlaget

`data/bestand_syntetisk.csv` er 604 helt syntetiske poliser (600 pluss 4 duplikater), laget av
`tools/generer_bestand.py` med fast seed. Ingen ekte personer, ingen ekte poliser.
Semikolonseparert, UTF-8, datoer som ÅÅÅÅ-MM-DD, beløp med desimalkomma uten tusenskille.

| Kolonne | Innhold |
|---|---|
| PoliseNr | `P-` og seks sifre, skal være unikt |
| Fodselsdato | medlemmets fødselsdato |
| Kjonn | `K` eller `M` |
| Ytelsestype | Alderspensjon, Uforepensjon, Ektefellepensjon, Barnepensjon |
| Status | Aktiv, Fripolise, UnderUtbetaling, Opphort |
| Startdato | når polisen startet |
| Sluttdato | opphørsdato, bare for Opphort |
| AarligYtelse | årlig ytelse i kroner |
| Premiereserve | premiereserve i kroner, 0 for Opphort |
| Pensjonsalder | valgfri |

Feilene er plantet med vilje, hver på sine egne rader. Fasiten viser likevel at én plantet
feil kan slå ut på flere kontroller: de to medlemmene «født» etter 2010 har også startdato
før fylte 18.

| Kontroll | Regel | Poliser i fasit | Status i repoet |
|---|---|---|---|
| DuplikatPoliseNr | PoliseNr skal være unikt | 4 | implementert |
| UgyldigFodselsdato | fødselsdato i [1900-01-01, 2010-12-31] | 5 | implementert |
| ManglendeFelt | obligatoriske felt utfylt og tolkbare | 6 | implementert |
| NegativPremiereserve | premiereserve kan ikke være negativ, 0 er gyldig | 7 | AKT-9 |
| SluttdatoFoerStartdato | sluttdato kan ikke være før startdato | 5 | AKT-10 |
| OpphortMedReserve | opphørt polise skal ha premiereserve 0 | 6 | AKT-11 |
| StartdatoFoerFylte18 | startdato kan ikke være før 18-årsdagen | 6 | AKT-12 |
| YtelseUtenforIntervall | årlig ytelse i (0, 2 000 000] | 5 | AKT-13 |

## Struktur

```
bestandskontroll/        pakken (kjøres med python -m bestandskontroll)
  kontroller/            én fil per kontroll, registeret i __init__.py
data/                    syntetisk bestand og fasit
tests/                   pytest; conftest.py har fixturen `gyldig`
tools/generer_bestand.py generator med referansereglene som gir fasiten
CLAUDE.md                arbeidsreglene for Claude Code
```
