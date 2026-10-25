"""Bestandskontroll – kontroller på bestandsdata for pensjon og forsikring.

Demo-repo for KI-assistert utvikling styrt fra Linear: Claude Desktop skriver sakene,
Claude Code implementerer dem her, og testene mot data/fasit.json avgjør om det er riktig.
"""

from bestandskontroll.modell import Alvorlighet, Funn, Polise

__all__ = ["Alvorlighet", "Funn", "Polise"]
