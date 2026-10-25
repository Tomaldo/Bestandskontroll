"""Fasittesten: hver registrert kontroll skal slå ut på nøyaktig de polisene fasiten sier.

Testen plukker opp nye kontroller automatisk når de registreres i ALLE_KONTROLLER.
Fasiten (data/fasit.json) er kontrakten og endres aldri for å få denne testen grønn.
"""

import pytest

from bestandskontroll.fasit import Fasit
from bestandskontroll.innlesing import les_bestand
from bestandskontroll.kjoring import kjor_kontroller
from bestandskontroll.kontroller import ALLE_KONTROLLER
from tests.conftest import BESTANDSFIL, FASITFIL


@pytest.fixture(scope="module")
def bestand():
    return les_bestand(BESTANDSFIL)


@pytest.fixture(scope="module")
def fasit():
    return Fasit.les(FASITFIL)


@pytest.mark.parametrize("kontroll", ALLE_KONTROLLER, ids=lambda k: k.navn)
def test_kontrollen_stemmer_med_fasiten(kontroll, bestand, fasit):
    assert fasit.har(kontroll.navn), (
        f"{kontroll.navn} mangler i data/fasit.json. Fasiten er kontrakten og skrives før "
        f"kontrollen – stopp og ta det opp på saken."
    )

    funnet = {funn.polisenr for funn in kontroll.kjor(bestand)}
    forventet = fasit.forventet[kontroll.navn]

    assert funnet == forventet, (
        f"{kontroll.navn}: i fasit men ikke funnet {sorted(forventet - funnet)}, "
        f"funnet men ikke i fasit {sorted(funnet - forventet)}"
    )


def test_fasiten_gjelder_denne_filen(bestand, fasit):
    assert fasit.antall_rader == len(bestand), (
        "data/fasit.json og data/bestand_syntetisk.csv er ikke generert sammen"
    )


def test_rapporten_sammenligner_likt_med_testen(bestand, fasit):
    rapport = kjor_kontroller(bestand)

    for resultat in rapport.resultater:
        assert fasit.sammenlign(resultat).ok, resultat.kontroll.navn


def test_alle_kontroller_har_unikt_navn_lik_klassenavnet():
    navn = [kontroll.navn for kontroll in ALLE_KONTROLLER]

    assert len(navn) == len(set(navn)), "to kontroller har samme navn"
    for kontroll in ALLE_KONTROLLER:
        assert kontroll.navn == type(kontroll).__name__
        assert kontroll.beskrivelse.strip(), f"{kontroll.navn} mangler beskrivelse"
