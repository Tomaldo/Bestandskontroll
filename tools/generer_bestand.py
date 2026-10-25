"""Lager den syntetiske bestanden i data/ og fasiten som hører til.

    python tools/generer_bestand.py            # skriver data/bestand_syntetisk.csv og data/fasit.json
    python tools/generer_bestand.py --ut /tmp  # skriver til en annen mappe

Bestanden er helt syntetisk: ingen ekte personer, ingen ekte poliser. Den lages med fast
seed, så samme kjøring gir samme fil. Feilene er plantet med vilje, og fasiten beregnes
etterpå av referansereglene nederst i denne filen – uavhengig av kontrollene i pakken.
Det er poenget: fasiten er den uavhengige kontrollen av kontrollene.

Skriptet bruker bare standardbiblioteket og importerer ingenting fra pakken.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter
from dataclasses import dataclass, replace
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

SEED = 2026
ANTALL_POLISER = 600
FORSTE_POLISENR = 100001

TIDLIGSTE_START = date(1990, 1, 1)
SENESTE_START = date(2024, 12, 31)
TIDLIGSTE_FODSEL = date(1945, 1, 1)
SENESTE_FODSEL = date(2004, 12, 31)

KOLONNER = [
    "PoliseNr",
    "Fodselsdato",
    "Kjonn",
    "Ytelsestype",
    "Status",
    "Startdato",
    "Sluttdato",
    "AarligYtelse",
    "Premiereserve",
    "Pensjonsalder",
]

YTELSESTYPER = ["Alderspensjon", "Uforepensjon", "Ektefellepensjon", "Barnepensjon"]
YTELSESVEKTER = [60, 20, 12, 8]
STATUSER = ["Aktiv", "Fripolise", "UnderUtbetaling", "Opphort"]
STATUSVEKTER = [55, 25, 15, 5]

# Årlig ytelse i kroner, per ytelsestype: (fra, til)
YTELSESINTERVALL = {
    "Alderspensjon": (20_000, 400_000),
    "Uforepensjon": (50_000, 350_000),
    "Ektefellepensjon": (10_000, 150_000),
    "Barnepensjon": (5_000, 60_000),
}
# Premiereserve som multiplum av årlig ytelse, per status: (fra, til)
RESERVEFAKTOR = {
    "Aktiv": (3.0, 12.0),
    "Fripolise": (4.0, 14.0),
    "UnderUtbetaling": (8.0, 16.0),
}


@dataclass
class Rad:
    polisenr: str
    fodselsdato: date | None
    kjonn: str | None
    ytelsestype: str | None
    status: str | None
    startdato: date | None
    sluttdato: date | None
    aarlig_ytelse: Decimal | None
    premiereserve: Decimal | None
    pensjonsalder: int | None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--ut", default=str(Path(__file__).resolve().parents[1] / "data"), help="mappe å skrive til"
    )
    args = parser.parse_args()

    rng = random.Random(SEED)
    rader = lag_grunnbestand(rng)
    plantet = plant_feil(rng, rader)
    rng.shuffle(rader)

    utmappe = Path(args.ut)
    utmappe.mkdir(parents=True, exist_ok=True)
    skriv_csv(utmappe / "bestand_syntetisk.csv", rader)
    fasit = beregn_fasit(rader)
    skriv_fasit(utmappe / "fasit.json", fasit, plantet, len(rader))

    print(f"Skrev {len(rader)} rader til {utmappe / 'bestand_syntetisk.csv'}")
    for navn, poliser in fasit.items():
        print(f"  {navn:<24} {len(poliser):>3} poliser i fasit")


# ----------------------------------------------------------------------------------------
# Grunnbestand uten feil
# ----------------------------------------------------------------------------------------


def lag_grunnbestand(rng: random.Random) -> list[Rad]:
    rader = []
    for nr in range(ANTALL_POLISER):
        fodselsdato = tilfeldig_dato(rng, TIDLIGSTE_FODSEL, SENESTE_FODSEL)
        ytelsestype = rng.choices(YTELSESTYPER, YTELSESVEKTER)[0]
        status = rng.choices(STATUSER, STATUSVEKTER)[0]

        tidligste_start = max(TIDLIGSTE_START, attenaarsdag(fodselsdato))
        startdato = tilfeldig_dato(rng, tidligste_start, max(tidligste_start, SENESTE_START))

        sluttdato = None
        if status == "Opphort":
            sluttdato = startdato + timedelta(days=rng.randint(365, 15 * 365))

        fra, til = YTELSESINTERVALL[ytelsestype]
        aarlig_ytelse = Decimal(rng.randint(fra // 100, til // 100) * 100)

        if status == "Opphort":
            premiereserve = Decimal("0.00")
        else:
            lav, hoy = RESERVEFAKTOR[status]
            premiereserve = kroner(float(aarlig_ytelse) * rng.uniform(lav, hoy))

        pensjonsalder = 67 if rng.random() < 0.8 else rng.randint(62, 70)

        rader.append(
            Rad(
                polisenr=f"P-{FORSTE_POLISENR + nr}",
                fodselsdato=fodselsdato,
                kjonn=rng.choice(["K", "M"]),
                ytelsestype=ytelsestype,
                status=status,
                startdato=startdato,
                sluttdato=sluttdato,
                aarlig_ytelse=aarlig_ytelse,
                premiereserve=premiereserve,
                pensjonsalder=pensjonsalder,
            )
        )
    return rader


# ----------------------------------------------------------------------------------------
# Plantede feil. Hver feiltype får sine egne rader, så ingen rad bærer to plantede feil.
# (En plantet feil kan likevel slå ut på flere kontroller – det avgjør referansereglene.)
# ----------------------------------------------------------------------------------------


def plant_feil(rng: random.Random, rader: list[Rad]) -> dict[str, int]:
    ledige = list(range(len(rader)))
    rng.shuffle(ledige)

    def ta(antall: int, krav=lambda rad: True) -> list[int]:
        valgte = []
        for indeks in list(ledige):
            if len(valgte) == antall:
                break
            if krav(rader[indeks]):
                valgte.append(indeks)
                ledige.remove(indeks)
        if len(valgte) < antall:
            raise RuntimeError("For få ledige rader til å plante feil – øk ANTALL_POLISER.")
        return valgte

    plantet: dict[str, int] = {}

    # Negativ premiereserve
    for i in ta(7):
        rader[i].premiereserve = -kroner(rng.uniform(1_000, 500_000))
    plantet["negativ premiereserve"] = 7

    # Fødselsdato utenfor [1900-01-01, 2010-12-31]: tre for gamle, to for unge
    for i in ta(3):
        rader[i].fodselsdato = tilfeldig_dato(rng, date(1880, 1, 1), date(1899, 12, 31))
    for i in ta(2):
        rader[i].fodselsdato = tilfeldig_dato(rng, date(2012, 1, 1), date(2018, 12, 31))
    plantet["ugyldig fodselsdato"] = 5

    # Manglende obligatoriske felt
    for i in ta(2):
        rader[i].kjonn = None
    for i in ta(2):
        rader[i].ytelsestype = None
    for i in ta(1):
        rader[i].startdato = None
    for i in ta(1):
        rader[i].premiereserve = None
    plantet["manglende felt"] = 6

    # Startdato før fylte 18
    for i in ta(4, krav=lambda rad: rad.fodselsdato is not None):
        rad = rader[i]
        assert rad.fodselsdato is not None
        rad.startdato = rad.fodselsdato + timedelta(days=rng.randint(10 * 365, 17 * 365))
    plantet["startdato foer fylte 18"] = 4

    # Årlig ytelse utenfor (0, 2 000 000]: to nuller, én negativ, to tusenfeil
    for i, verdi in zip(ta(5), ["0", "0", "-12000", "2500000", "tusenfeil"]):
        rad = rader[i]
        assert rad.aarlig_ytelse is not None
        rad.aarlig_ytelse = rad.aarlig_ytelse * 1000 if verdi == "tusenfeil" else Decimal(verdi)
    plantet["ytelse utenfor intervall"] = 5

    # Opphørte poliser: sluttdato før startdato, og opphørt med reserve
    for i in ta(5, krav=lambda rad: rad.status == "Opphort"):
        rad = rader[i]
        assert rad.startdato is not None
        rad.sluttdato = rad.startdato - timedelta(days=rng.randint(30, 900))
    plantet["sluttdato foer startdato"] = 5

    for i in ta(6, krav=lambda rad: rad.status == "Opphort"):
        rader[i].premiereserve = kroner(rng.uniform(50_000, 900_000))
    plantet["opphort med reserve"] = 6

    # Duplikater: fire rene rader kopieres i sin helhet
    for i in ta(4):
        rader.append(replace(rader[i]))
    plantet["duplikat polisenr"] = 4

    return plantet


# ----------------------------------------------------------------------------------------
# Referanseregler – fasiten. Skrevet uavhengig av kontrollene i pakken.
# Samme ordlyd som i Linear-sakene. Hver regel gir mengden av PoliseNr den slår ut på.
# ----------------------------------------------------------------------------------------

OBLIGATORISKE = (
    "polisenr",
    "fodselsdato",
    "kjonn",
    "ytelsestype",
    "status",
    "startdato",
    "aarlig_ytelse",
    "premiereserve",
)


def beregn_fasit(rader: list[Rad]) -> dict[str, list[str]]:
    teller = Counter(rad.polisenr for rad in rader if rad.polisenr)

    regler = {
        # PoliseNr skal være unikt.
        "DuplikatPoliseNr": {nr for nr, antall in teller.items() if antall > 1},
        # Fødselsdato skal ligge mellom 1900-01-01 og 2010-12-31 (tom dato fanges av ManglendeFelt).
        "UgyldigFodselsdato": {
            rad.polisenr
            for rad in rader
            if rad.fodselsdato is not None
            and not (date(1900, 1, 1) <= rad.fodselsdato <= date(2010, 12, 31))
        },
        # Obligatoriske felt skal være utfylt.
        "ManglendeFelt": {
            rad.polisenr
            for rad in rader
            if any(getattr(rad, felt) in (None, "") for felt in OBLIGATORISKE)
        },
        # Premiereserve kan ikke være negativ. 0 er gyldig.
        "NegativPremiereserve": {
            rad.polisenr
            for rad in rader
            if rad.premiereserve is not None and rad.premiereserve < 0
        },
        # Sluttdato kan ikke være før startdato.
        "SluttdatoFoerStartdato": {
            rad.polisenr
            for rad in rader
            if rad.sluttdato is not None
            and rad.startdato is not None
            and rad.sluttdato < rad.startdato
        },
        # En opphørt polise skal ha premiereserve 0.
        "OpphortMedReserve": {
            rad.polisenr
            for rad in rader
            if rad.status == "Opphort" and rad.premiereserve is not None and rad.premiereserve > 0
        },
        # Startdato kan ikke være før 18-årsdagen (29. februar regnes som 1. mars).
        "StartdatoFoerFylte18": {
            rad.polisenr
            for rad in rader
            if rad.startdato is not None
            and rad.fodselsdato is not None
            and rad.startdato < attenaarsdag(rad.fodselsdato)
        },
        # Årlig ytelse skal være større enn 0 og høyst 2 000 000.
        "YtelseUtenforIntervall": {
            rad.polisenr
            for rad in rader
            if rad.aarlig_ytelse is not None
            and not (Decimal(0) < rad.aarlig_ytelse <= Decimal(2_000_000))
        },
    }
    return {navn: sorted(poliser) for navn, poliser in regler.items()}


# ----------------------------------------------------------------------------------------
# Hjelpere og skriving
# ----------------------------------------------------------------------------------------


def attenaarsdag(fodselsdato: date) -> date:
    """18-årsdagen. Den som er født 29. februar fyller år 1. mars."""
    try:
        return fodselsdato.replace(year=fodselsdato.year + 18)
    except ValueError:
        return date(fodselsdato.year + 18, 3, 1)


def tilfeldig_dato(rng: random.Random, fra: date, til: date) -> date:
    return fra + timedelta(days=rng.randint(0, (til - fra).days))


def kroner(belop: float) -> Decimal:
    return Decimal(str(belop)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def som_tekst(verdi) -> str:
    if verdi is None:
        return ""
    if isinstance(verdi, Decimal):
        return format(verdi, "f").replace(".", ",")
    if isinstance(verdi, date):
        return verdi.isoformat()
    return str(verdi)


def skriv_csv(sti: Path, rader: list[Rad]) -> None:
    with open(sti, "w", encoding="utf-8", newline="") as fil:
        skriver = csv.writer(fil, delimiter=";", lineterminator="\n")
        skriver.writerow(KOLONNER)
        for rad in rader:
            skriver.writerow(
                [
                    som_tekst(rad.polisenr),
                    som_tekst(rad.fodselsdato),
                    som_tekst(rad.kjonn),
                    som_tekst(rad.ytelsestype),
                    som_tekst(rad.status),
                    som_tekst(rad.startdato),
                    som_tekst(rad.sluttdato),
                    som_tekst(rad.aarlig_ytelse),
                    som_tekst(rad.premiereserve),
                    som_tekst(rad.pensjonsalder),
                ]
            )


def skriv_fasit(sti: Path, fasit: dict[str, list[str]], plantet: dict[str, int], antall: int) -> None:
    innhold = {
        "beskrivelse": (
            "Fasit for data/bestand_syntetisk.csv: polisene hver kontroll skal slå ut på. "
            "Beregnet av referansereglene i tools/generer_bestand.py, uavhengig av kontrollene "
            "i pakken. Fasiten er kontrakten og endres aldri for å få tester grønne."
        ),
        "generert_av": "tools/generer_bestand.py",
        "seed": SEED,
        "antall_rader": antall,
        "plantede_feil": plantet,
        "forventet": fasit,
    }
    sti.write_text(json.dumps(innhold, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
