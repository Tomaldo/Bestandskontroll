"""Fasiten: hvilke poliser hver kontroll skal slå ut på i data/bestand_syntetisk.csv.

Fasiten er kontrakten. Den beregnes av en uavhengig referanseimplementasjon i
tools/generer_bestand.py, og endres aldri for å få en test grønn.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from bestandskontroll.kjoring import KontrollResultat
from bestandskontroll.kontroller import Kontroll


@dataclass(frozen=True, slots=True)
class FasitAvvik:
    kontroll: str
    mangler_fasit: bool
    """Kontrollen finnes ikke i fasiten – da kan den ikke verifiseres."""
    ikke_funnet: frozenset[str]
    """I fasiten, men kontrollen fant dem ikke."""
    uventet: frozenset[str]
    """Kontrollen fant dem, men de står ikke i fasiten."""

    @property
    def ok(self) -> bool:
        return not self.mangler_fasit and not self.ikke_funnet and not self.uventet

    def tekst(self) -> str:
        if self.mangler_fasit:
            return "mangler i fasit"
        if self.ok:
            return "OK"
        deler = []
        if self.ikke_funnet:
            deler.append(f"{len(self.ikke_funnet)} ikke funnet")
        if self.uventet:
            deler.append(f"{len(self.uventet)} uventet")
        return "AVVIK (" + ", ".join(deler) + ")"


@dataclass(frozen=True, slots=True)
class Fasit:
    forventet: dict[str, frozenset[str]]
    beskrivelse: str = ""
    antall_rader: int | None = None

    @classmethod
    def les(cls, sti: str | Path) -> "Fasit":
        data = json.loads(Path(sti).read_text(encoding="utf-8"))
        return cls(
            forventet={navn: frozenset(poliser) for navn, poliser in data["forventet"].items()},
            beskrivelse=data.get("beskrivelse", ""),
            antall_rader=data.get("antall_rader"),
        )

    def har(self, kontrollnavn: str) -> bool:
        return kontrollnavn in self.forventet

    def ikke_implementert(self, kontroller: Iterable[Kontroll]) -> list[str]:
        """Kontroller fasiten venter på, som ikke er registrert ennå – det som gjenstår."""
        implementert = {kontroll.navn for kontroll in kontroller}
        return [navn for navn in self.forventet if navn not in implementert]

    def sammenlign(self, resultat: KontrollResultat) -> FasitAvvik:
        navn = resultat.kontroll.navn
        if navn not in self.forventet:
            return FasitAvvik(navn, True, frozenset(), frozenset())
        forventet = self.forventet[navn]
        funnet = resultat.polisenr
        return FasitAvvik(navn, False, forventet - funnet, funnet - forventet)
