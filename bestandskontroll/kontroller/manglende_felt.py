from __future__ import annotations

from typing import Sequence

from bestandskontroll.kontroller.basis import Kontroll
from bestandskontroll.modell import Alvorlighet, Funn, Polise

# Attributt på Polise -> kolonnenavn i filen, slik meldingen snakker filens språk.
OBLIGATORISKE_FELT = {
    "polisenr": "PoliseNr",
    "fodselsdato": "Fodselsdato",
    "kjonn": "Kjonn",
    "ytelsestype": "Ytelsestype",
    "status": "Status",
    "startdato": "Startdato",
    "aarlig_ytelse": "AarligYtelse",
    "premiereserve": "Premiereserve",
}


class ManglendeFelt(Kontroll):
    navn = "ManglendeFelt"
    beskrivelse = (
        "Obligatoriske felt skal være utfylt og tolkbare: PoliseNr, Fodselsdato, Kjonn, "
        "Ytelsestype, Status, Startdato, AarligYtelse og Premiereserve. "
        "Sluttdato og Pensjonsalder er valgfrie."
    )
    alvorlighet = Alvorlighet.FEIL

    def kjor(self, bestand: Sequence[Polise]) -> list[Funn]:
        funn: list[Funn] = []
        for polise in bestand:
            mangler = [
                kolonne
                for attributt, kolonne in OBLIGATORISKE_FELT.items()
                if getattr(polise, attributt) in (None, "")
            ]
            if mangler:
                funn.append(
                    self.funn(polise, "Mangler eller kan ikke tolkes: " + ", ".join(mangler) + ".")
                )
        return funn
