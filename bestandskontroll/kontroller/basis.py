"""Grunnklassen alle kontroller arver fra."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, Sequence

from bestandskontroll.modell import Alvorlighet, Funn, Polise


class Kontroll(ABC):
    """En kontroll leser hele bestanden og returnerer ett funn per avvik.

    Kontroller er rene funksjoner: ingen I/O og ingen avhengighet av dagens dato.
    Regelen står i `beskrivelse`, med samme ordlyd som i Linear-saken.
    """

    navn: ClassVar[str]
    """Stabil nøkkel. Skal være lik klassenavnet og nøkkelen i data/fasit.json."""

    beskrivelse: ClassVar[str]
    """Én eller to setninger om regelen, skrevet for en aktuar."""

    alvorlighet: ClassVar[Alvorlighet] = Alvorlighet.FEIL

    @abstractmethod
    def kjor(self, bestand: Sequence[Polise]) -> list[Funn]:
        """Returnerer funnene i den rekkefølgen polisene står i filen."""

    def funn(self, polise: Polise, melding: str) -> Funn:
        """Lager et funn for denne kontrollen på gitt polise."""
        return Funn(self.navn, polise.polisenr, polise.linje, melding)
