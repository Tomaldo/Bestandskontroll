from datetime import date

import pytest

from bestandskontroll.kontroller import UgyldigFodselsdato


@pytest.mark.parametrize(
    "fodselsdato",
    [date(1899, 12, 31), date(1850, 6, 1), date(2011, 1, 1), date(2030, 1, 1)],
    ids=str,
)
def test_fodselsdato_utenfor_intervallet_gir_funn(gyldig, fodselsdato):
    bestand = [gyldig(fodselsdato=fodselsdato)]

    funn = UgyldigFodselsdato().kjor(bestand)

    assert len(funn) == 1
    assert fodselsdato.isoformat() in funn[0].melding


@pytest.mark.parametrize(
    "fodselsdato",
    [date(1900, 1, 1), date(1975, 5, 17), date(2010, 12, 31)],
    ids=str,
)
def test_grensene_er_inkludert(gyldig, fodselsdato):
    assert UgyldigFodselsdato().kjor([gyldig(fodselsdato=fodselsdato)]) == []


def test_tom_fodselsdato_er_ikke_denne_kontrollens_ansvar(gyldig):
    assert UgyldigFodselsdato().kjor([gyldig(fodselsdato=None)]) == []
