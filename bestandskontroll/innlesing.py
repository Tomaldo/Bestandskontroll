"""Innlesing av bestandsfilen.

Formatet er semikolonseparert UTF-8 med én overskriftslinje, datoer som ÅÅÅÅ-MM-DD og
beløp med desimalkomma og uten tusenskille (f.eks. 123456,50).

Innlesingen er bevisst tolerant: et felt som er tomt eller ikke lar seg tolke blir None,
slik at kontrollene kan rapportere det som et funn på riktig polise. Bare feil som gjør
filen umulig å lese som helhet (feil overskrift, feil antall kolonner) stopper innlesingen.
"""

from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable

from bestandskontroll.modell import Polise

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
SKILLETEGN = ";"


class BestandFormatFeil(ValueError):
    """Filen kan ikke leses som en bestandsfil."""


def les_bestand(sti: str | Path) -> list[Polise]:
    """Leser en bestandsfil fra disk."""
    with open(sti, encoding="utf-8-sig", newline="") as fil:
        return les_linjer(fil)


def les_linjer(linjer: Iterable[str]) -> list[Polise]:
    """Leser bestanden fra en strøm av tekstlinjer (fil, StringIO, liste av strenger)."""
    leser = csv.reader(linjer, delimiter=SKILLETEGN)
    try:
        overskrift = [kolonne.strip() for kolonne in next(leser)]
    except StopIteration:
        raise BestandFormatFeil("Filen er tom.") from None
    if overskrift != KOLONNER:
        raise BestandFormatFeil(
            f"Uventet overskrift: {SKILLETEGN.join(overskrift)}. "
            f"Forventet: {SKILLETEGN.join(KOLONNER)}."
        )

    poliser: list[Polise] = []
    for rad in leser:
        if not rad or all(not verdi.strip() for verdi in rad):
            continue  # tomme linjer, typisk på slutten av filen
        linje = leser.line_num
        if len(rad) != len(KOLONNER):
            raise BestandFormatFeil(
                f"Linje {linje}: {len(rad)} kolonner, forventet {len(KOLONNER)}."
            )
        felt = dict(zip(KOLONNER, (verdi.strip() for verdi in rad)))
        poliser.append(
            Polise(
                linje=linje,
                polisenr=felt["PoliseNr"],
                fodselsdato=_dato(felt["Fodselsdato"]),
                kjonn=_tekst(felt["Kjonn"]),
                ytelsestype=_tekst(felt["Ytelsestype"]),
                status=_tekst(felt["Status"]),
                startdato=_dato(felt["Startdato"]),
                sluttdato=_dato(felt["Sluttdato"]),
                aarlig_ytelse=_belop(felt["AarligYtelse"]),
                premiereserve=_belop(felt["Premiereserve"]),
                pensjonsalder=_heltall(felt["Pensjonsalder"]),
            )
        )
    return poliser


def _tekst(verdi: str) -> str | None:
    return verdi or None


def _dato(verdi: str) -> date | None:
    if not verdi:
        return None
    try:
        return date.fromisoformat(verdi)
    except ValueError:
        return None


def _belop(verdi: str) -> Decimal | None:
    """Beløp med desimalkomma. Punktum og mellomrom avvises, fordi «1.234,50» og «1,234.50»
    ikke kan skilles trygt fra hverandre – da er feltet heller utolkbart enn feil tolket."""
    if not verdi or "." in verdi or " " in verdi:
        return None
    try:
        tall = Decimal(verdi.replace(",", "."))
    except InvalidOperation:
        return None
    return tall if tall.is_finite() else None


def _heltall(verdi: str) -> int | None:
    if not verdi:
        return None
    try:
        return int(verdi)
    except ValueError:
        return None
