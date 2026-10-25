import io
from datetime import date
from decimal import Decimal

import pytest

from bestandskontroll.innlesing import KOLONNER, BestandFormatFeil, les_bestand, les_linjer
from tests.conftest import BESTANDSFIL

OVERSKRIFT = ";".join(KOLONNER)


def les(tekst: str):
    return les_linjer(io.StringIO(tekst))


def test_leser_en_komplett_rad():
    poliser = les(
        OVERSKRIFT + "\n"
        "P-100001;1975-05-17;K;Alderspensjon;Aktiv;2005-01-01;;120000;980000,50;67\n"
    )

    assert len(poliser) == 1
    p = poliser[0]
    assert p.linje == 2
    assert p.polisenr == "P-100001"
    assert p.fodselsdato == date(1975, 5, 17)
    assert p.kjonn == "K"
    assert p.ytelsestype == "Alderspensjon"
    assert p.status == "Aktiv"
    assert p.startdato == date(2005, 1, 1)
    assert p.sluttdato is None
    assert p.aarlig_ytelse == Decimal("120000")
    assert p.premiereserve == Decimal("980000.50")
    assert p.pensjonsalder == 67


def test_tomme_og_utolkbare_felt_blir_none_uten_at_innlesingen_stopper():
    poliser = les(
        OVERSKRIFT + "\n"
        "P-1;2031-02-30;;Alderspensjon;Aktiv;ikke en dato;;abc;1.234,50;sekstisju\n"
    )

    p = poliser[0]
    assert p.fodselsdato is None, "umulig dato blir None"
    assert p.kjonn is None, "tomt felt blir None"
    assert p.startdato is None, "tekst som ikke er dato blir None"
    assert p.aarlig_ytelse is None, "tekst som ikke er tall blir None"
    assert p.premiereserve is None, "tusenskille avvises heller enn å feiltolkes"
    assert p.pensjonsalder is None


def test_negative_belop_og_desimalkomma():
    poliser = les(OVERSKRIFT + "\nP-1;1975-05-17;M;Uforepensjon;Aktiv;2005-01-01;;-12000;-0,01;\n")

    assert poliser[0].aarlig_ytelse == Decimal("-12000")
    assert poliser[0].premiereserve == Decimal("-0.01")
    assert poliser[0].pensjonsalder is None


def test_linjenummer_teller_fra_overskriften_og_hopper_over_tomme_linjer():
    poliser = les(
        OVERSKRIFT + "\n"
        "P-1;1975-05-17;K;Alderspensjon;Aktiv;2005-01-01;;1;1;\n"
        "\n"
        "P-2;1975-05-17;K;Alderspensjon;Aktiv;2005-01-01;;1;1;\n"
    )

    assert [p.linje for p in poliser] == [2, 4]


def test_feil_overskrift_stopper_innlesingen():
    with pytest.raises(BestandFormatFeil, match="Uventet overskrift"):
        les("Polise;Fodt\nP-1;1975-05-17\n")


def test_feil_antall_kolonner_stopper_innlesingen():
    with pytest.raises(BestandFormatFeil, match="Linje 2"):
        les(OVERSKRIFT + "\nP-1;1975-05-17;K\n")


def test_tom_fil_stopper_innlesingen():
    with pytest.raises(BestandFormatFeil, match="tom"):
        les("")


def test_den_syntetiske_bestanden_kan_leses():
    poliser = les_bestand(BESTANDSFIL)

    assert len(poliser) > 500
    assert all(p.linje >= 2 for p in poliser)
