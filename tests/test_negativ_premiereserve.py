from decimal import Decimal

import pytest

from bestandskontroll.kontroller import NegativPremiereserve


@pytest.mark.parametrize("premiereserve", ["-0.01", "-12345", "-500000.50"])
def test_negativ_premiereserve_gir_funn(gyldig, premiereserve):
    bestand = [gyldig(premiereserve=Decimal(premiereserve))]

    funn = NegativPremiereserve().kjor(bestand)

    assert len(funn) == 1


def test_melding_oppgir_belopet_med_desimalkomma(gyldig):
    funn = NegativPremiereserve().kjor([gyldig(premiereserve=Decimal("-12345"))])

    assert "Premiereserve er -12345,00" in funn[0].melding


def test_grensen_minus_ett_ore_gir_funn(gyldig):
    funn = NegativPremiereserve().kjor([gyldig(premiereserve=Decimal("-0.01"))])

    assert len(funn) == 1
    assert "-0,01" in funn[0].melding


@pytest.mark.parametrize("premiereserve", ["0", "0.00", "1"])
def test_null_og_positiv_gir_ikke_funn(gyldig, premiereserve):
    assert NegativPremiereserve().kjor([gyldig(premiereserve=Decimal(premiereserve))]) == []


def test_tom_premiereserve_er_ikke_denne_kontrollens_ansvar(gyldig):
    assert NegativPremiereserve().kjor([gyldig(premiereserve=None)]) == []


def test_ett_funn_per_polise_i_filens_rekkefolge(gyldig):
    bestand = [
        gyldig(premiereserve=Decimal("-2")),
        gyldig(),
        gyldig(premiereserve=Decimal("-1")),
    ]

    funn = NegativPremiereserve().kjor(bestand)

    assert [f.polisenr for f in funn] == [bestand[0].polisenr, bestand[2].polisenr]
