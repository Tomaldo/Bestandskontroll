"""Felles testoppsett.

`gyldig` lager en polise som ikke slår ut på noen kontroll. Hvert kall gir nytt PoliseNr og
nytt linjenummer, så en test som vil ha duplikater må be om det eksplisitt:

    def test_noe(gyldig):
        bestand = [gyldig(), gyldig(premiereserve=Decimal("-1"))]
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from itertools import count
from pathlib import Path

import pytest

from bestandskontroll.modell import Polise

ROT = Path(__file__).resolve().parents[1]
BESTANDSFIL = ROT / "data" / "bestand_syntetisk.csv"
FASITFIL = ROT / "data" / "fasit.json"


@pytest.fixture
def gyldig():
    teller = count(1)

    def lag(**endringer) -> Polise:
        nr = next(teller)
        verdier = dict(
            linje=nr + 1,
            polisenr=f"P-{100000 + nr}",
            fodselsdato=date(1975, 5, 17),
            kjonn="K",
            ytelsestype="Alderspensjon",
            status="Aktiv",
            startdato=date(2005, 1, 1),
            sluttdato=None,
            aarlig_ytelse=Decimal("120000"),
            premiereserve=Decimal("980000.50"),
            pensjonsalder=67,
        )
        verdier.update(endringer)
        return Polise(**verdier)

    return lag
