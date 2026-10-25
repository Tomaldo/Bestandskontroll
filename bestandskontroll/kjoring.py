"""Kjører et sett kontroller på en bestand og samler resultatet i en rapport."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from bestandskontroll.kontroller import ALLE_KONTROLLER, Kontroll
from bestandskontroll.modell import Funn, Polise


@dataclass(frozen=True, slots=True)
class KontrollResultat:
    kontroll: Kontroll
    funn: tuple[Funn, ...]

    @property
    def polisenr(self) -> frozenset[str]:
        """Polisene kontrollen slo ut på – det fasiten sammenligner mot."""
        return frozenset(f.polisenr for f in self.funn)


@dataclass(frozen=True, slots=True)
class Rapport:
    antall_poliser: int
    resultater: tuple[KontrollResultat, ...]

    @property
    def antall_funn(self) -> int:
        return sum(len(resultat.funn) for resultat in self.resultater)


def kjor_kontroller(
    bestand: Sequence[Polise], kontroller: Iterable[Kontroll] | None = None
) -> Rapport:
    """Kjører kontrollene (alle registrerte hvis ingen er oppgitt) og returnerer rapporten."""
    valgte = ALLE_KONTROLLER if kontroller is None else list(kontroller)
    return Rapport(
        antall_poliser=len(bestand),
        resultater=tuple(
            KontrollResultat(kontroll, tuple(kontroll.kjor(bestand))) for kontroll in valgte
        ),
    )
