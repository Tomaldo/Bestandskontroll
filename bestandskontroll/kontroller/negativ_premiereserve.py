from __future__ import annotations

from decimal import Decimal
from typing import Sequence

from bestandskontroll.kontroller.basis import Kontroll
from bestandskontroll.modell import Alvorlighet, Funn, Polise


def _belop(verdi: Decimal) -> str:
    """Beløp med to desimaler og desimalkomma, som i bestandsfilen."""
    return f"{verdi:.2f}".replace(".", ",")


class NegativPremiereserve(Kontroll):
    navn = "NegativPremiereserve"
    beskrivelse = (
        "Premiereserve kan ikke være negativ. 0 er gyldig (opphørte poliser). "
        "Tom eller utolkbar premiereserve fanges av ManglendeFelt og skal ikke gi funn her."
    )
    alvorlighet = Alvorlighet.FEIL

    def kjor(self, bestand: Sequence[Polise]) -> list[Funn]:
        return [
            self.funn(polise, f"Premiereserve er {_belop(polise.premiereserve)}.")
            for polise in bestand
            if polise.premiereserve is not None and polise.premiereserve < 0
        ]
