"""Datamodellen: én polise slik den står i filen, og ett funn fra én kontroll."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum


class Alvorlighet(Enum):
    ADVARSEL = "Advarsel"
    FEIL = "Feil"


@dataclass(frozen=True, slots=True)
class Polise:
    """Én rad i bestandsfilen, slik den ble lest.

    Felt som er tomme i filen, eller som ikke lot seg tolke, er None.
    Innlesingen dømmer aldri – det gjør kontrollene.
    """

    linje: int
    """Linjenummer i filen (overskriften er linje 1), så et funn kan slås opp i Excel."""
    polisenr: str
    """Tom streng hvis raden mangler PoliseNr."""
    fodselsdato: date | None
    kjonn: str | None
    ytelsestype: str | None
    status: str | None
    startdato: date | None
    sluttdato: date | None
    aarlig_ytelse: Decimal | None
    premiereserve: Decimal | None
    pensjonsalder: int | None


@dataclass(frozen=True, slots=True)
class Funn:
    """Ett avvik funnet av én kontroll på én polise."""

    kontroll: str
    """Navnet på kontrollen som fant avviket – samme nøkkel som i data/fasit.json."""
    polisenr: str
    linje: int
    melding: str
    """Kort forklaring, skrevet for den som skal rette feilen."""
