from __future__ import annotations

from datetime import date
from typing import Sequence

from bestandskontroll.kontroller.basis import Kontroll
from bestandskontroll.modell import Alvorlighet, Funn, Polise

TIDLIGSTE_FODSELSDATO = date(1900, 1, 1)
SENESTE_FODSELSDATO = date(2010, 12, 31)


class UgyldigFodselsdato(Kontroll):
    navn = "UgyldigFodselsdato"
    beskrivelse = (
        "Fødselsdato skal ligge mellom 1900-01-01 og 2010-12-31. "
        "Tom eller utolkbar fødselsdato fanges av ManglendeFelt, ikke her."
    )
    alvorlighet = Alvorlighet.FEIL

    def kjor(self, bestand: Sequence[Polise]) -> list[Funn]:
        return [
            self.funn(
                polise,
                f"Fødselsdato {polise.fodselsdato.isoformat()} er utenfor "
                f"[{TIDLIGSTE_FODSELSDATO.isoformat()}, {SENESTE_FODSELSDATO.isoformat()}].",
            )
            for polise in bestand
            if polise.fodselsdato is not None
            and not (TIDLIGSTE_FODSELSDATO <= polise.fodselsdato <= SENESTE_FODSELSDATO)
        ]
