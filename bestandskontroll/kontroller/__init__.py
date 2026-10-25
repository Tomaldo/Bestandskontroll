"""Registeret over kontroller.

En ny kontroll er ikke i bruk før den står i ALLE_KONTROLLER. Rekkefølgen her er
rekkefølgen i rapporten. Fasittesten (tests/test_fasit.py) kjører automatisk for alt
som står i listen.
"""

from bestandskontroll.kontroller.basis import Kontroll
from bestandskontroll.kontroller.duplikat_polisenr import DuplikatPoliseNr
from bestandskontroll.kontroller.manglende_felt import ManglendeFelt
from bestandskontroll.kontroller.negativ_premiereserve import NegativPremiereserve
from bestandskontroll.kontroller.ugyldig_fodselsdato import UgyldigFodselsdato

ALLE_KONTROLLER: list[Kontroll] = [
    DuplikatPoliseNr(),
    UgyldigFodselsdato(),
    ManglendeFelt(),
    NegativPremiereserve(),
]

__all__ = [
    "ALLE_KONTROLLER",
    "Kontroll",
    "DuplikatPoliseNr",
    "ManglendeFelt",
    "NegativPremiereserve",
    "UgyldigFodselsdato",
]
