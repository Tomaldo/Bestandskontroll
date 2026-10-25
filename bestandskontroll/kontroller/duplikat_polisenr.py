from __future__ import annotations

from typing import Sequence

from bestandskontroll.kontroller.basis import Kontroll
from bestandskontroll.modell import Alvorlighet, Funn, Polise


class DuplikatPoliseNr(Kontroll):
    navn = "DuplikatPoliseNr"
    beskrivelse = (
        "PoliseNr skal være unikt i bestanden. Ett funn per PoliseNr som forekommer "
        "mer enn én gang. Rader uten PoliseNr fanges av ManglendeFelt."
    )
    alvorlighet = Alvorlighet.FEIL

    def kjor(self, bestand: Sequence[Polise]) -> list[Funn]:
        grupper: dict[str, list[Polise]] = {}
        for polise in bestand:
            if polise.polisenr:
                grupper.setdefault(polise.polisenr, []).append(polise)

        return [
            self.funn(
                rader[0],
                f"PoliseNr forekommer {len(rader)} ganger "
                f"(linje {', '.join(str(rad.linje) for rad in rader)}).",
            )
            for rader in grupper.values()
            if len(rader) > 1
        ]
