from decimal import Decimal

import pytest

from bestandskontroll.kontroller import ManglendeFelt


@pytest.mark.parametrize(
    "attributt, kolonne",
    [
        ("polisenr", "PoliseNr"),
        ("fodselsdato", "Fodselsdato"),
        ("kjonn", "Kjonn"),
        ("ytelsestype", "Ytelsestype"),
        ("status", "Status"),
        ("startdato", "Startdato"),
        ("aarlig_ytelse", "AarligYtelse"),
        ("premiereserve", "Premiereserve"),
    ],
)
def test_hvert_obligatorisk_felt_gir_funn_naar_det_mangler(gyldig, attributt, kolonne):
    tomt = "" if attributt == "polisenr" else None
    bestand = [gyldig(**{attributt: tomt})]

    funn = ManglendeFelt().kjor(bestand)

    assert len(funn) == 1
    assert kolonne in funn[0].melding


def test_flere_manglende_felt_gir_ett_funn_som_nevner_alle(gyldig):
    bestand = [gyldig(kjonn=None, premiereserve=None)]

    funn = ManglendeFelt().kjor(bestand)

    assert len(funn) == 1
    assert "Kjonn" in funn[0].melding
    assert "Premiereserve" in funn[0].melding


def test_valgfrie_felt_kan_vaere_tomme(gyldig):
    bestand = [gyldig(sluttdato=None, pensjonsalder=None)]

    assert ManglendeFelt().kjor(bestand) == []


def test_null_er_en_verdi_ikke_et_manglende_felt(gyldig):
    bestand = [gyldig(premiereserve=Decimal("0"), aarlig_ytelse=Decimal("0"))]

    assert ManglendeFelt().kjor(bestand) == []
