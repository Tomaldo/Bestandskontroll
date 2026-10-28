from decimal import Decimal

import pytest

from bestandskontroll.kontroller import NegativPremiereserve


@pytest.mark.parametrize("premiereserve", ["-0.01", "-12345", "-980000.50"])
def test_negativ_premiereserve_gir_funn(gyldig, premiereserve):
    bestand = [gyldig(premiereserve=Decimal(premiereserve))]

    funn = NegativPremiereserve().kjor(bestand)

    assert len(funn) == 1
    assert funn[0].kontroll == "NegativPremiereserve"
    assert funn[0].polisenr == bestand[0].polisenr


def test_meldingen_oppgir_belopet_med_desimalkomma(gyldig):
    funn = NegativPremiereserve().kjor([gyldig(premiereserve=Decimal("-12345"))])

    assert funn[0].melding == "Premiereserve er -12345,00."


def test_minste_negative_belop_oppgis_med_to_desimaler(gyldig):
    funn = NegativPremiereserve().kjor([gyldig(premiereserve=Decimal("-0.01"))])

    assert "-0,01" in funn[0].melding


@pytest.mark.parametrize("premiereserve", ["0", "0.00", "1", "980000.50"])
def test_null_og_positiv_premiereserve_er_gyldig(gyldig, premiereserve):
    assert NegativPremiereserve().kjor([gyldig(premiereserve=Decimal(premiereserve))]) == []


def test_tom_premiereserve_er_ikke_denne_kontrollens_ansvar(gyldig):
    assert NegativPremiereserve().kjor([gyldig(premiereserve=None)]) == []


def test_ett_funn_per_polise_i_filens_rekkefolge(gyldig):
    bestand = [
        gyldig(premiereserve=Decimal("-5")),
        gyldig(),
        gyldig(premiereserve=Decimal("-1")),
    ]

    funn = NegativPremiereserve().kjor(bestand)

    assert [f.polisenr for f in funn] == [bestand[0].polisenr, bestand[2].polisenr]
