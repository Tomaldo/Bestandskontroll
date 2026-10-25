from bestandskontroll.kontroller import DuplikatPoliseNr


def test_to_rader_med_samme_polisenr_gir_ett_funn(gyldig):
    bestand = [gyldig(polisenr="P-1"), gyldig(), gyldig(polisenr="P-1")]

    funn = DuplikatPoliseNr().kjor(bestand)

    assert [f.polisenr for f in funn] == ["P-1"]
    assert "2 ganger" in funn[0].melding
    assert funn[0].linje == bestand[0].linje, "funnet peker på første forekomst"


def test_unike_polisenr_gir_ingen_funn(gyldig):
    assert DuplikatPoliseNr().kjor([gyldig(), gyldig(), gyldig()]) == []


def test_tre_like_gir_fortsatt_ett_funn(gyldig):
    bestand = [gyldig(polisenr="P-9") for _ in range(3)]

    funn = DuplikatPoliseNr().kjor(bestand)

    assert len(funn) == 1
    assert "3 ganger" in funn[0].melding


def test_tomt_polisenr_regnes_ikke_som_duplikat(gyldig):
    bestand = [gyldig(polisenr=""), gyldig(polisenr="")]

    assert DuplikatPoliseNr().kjor(bestand) == []
