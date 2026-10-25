"""Kommandolinjen: kjør alle kontroller på en bestandsfil og skriv rapport.

    python -m bestandskontroll data/bestand_syntetisk.csv --fasit data/fasit.json
    python -m bestandskontroll data/bestand_syntetisk.csv --detaljer

Avslutningskode 0 når alt er i orden, 1 hvis fasiten avviker fra det kontrollene fant.
"""

from __future__ import annotations

import argparse
from typing import Sequence

from bestandskontroll.fasit import Fasit, FasitAvvik
from bestandskontroll.innlesing import BestandFormatFeil, les_bestand
from bestandskontroll.kjoring import Rapport, kjor_kontroller
from bestandskontroll.kontroller import ALLE_KONTROLLER


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m bestandskontroll",
        description="Kjører alle registrerte kontroller på en bestandsfil og skriver en rapport.",
    )
    parser.add_argument("bestandsfil", help="semikolonseparert bestandsfil (se data/)")
    parser.add_argument("--fasit", metavar="FIL", help="fasit.json å sammenligne funnene med")
    parser.add_argument("--detaljer", action="store_true", help="skriv ut hvert enkelt funn")
    args = parser.parse_args(argv)

    try:
        bestand = les_bestand(args.bestandsfil)
    except (OSError, BestandFormatFeil) as feil:
        print(f"Kunne ikke lese {args.bestandsfil}: {feil}")
        return 2

    rapport = kjor_kontroller(bestand)
    fasit = Fasit.les(args.fasit) if args.fasit else None
    print(formater_rapport(rapport, args.bestandsfil, fasit, detaljer=args.detaljer))

    if fasit is not None:
        avvik = [fasit.sammenlign(resultat) for resultat in rapport.resultater]
        return 0 if all(a.ok for a in avvik) else 1
    return 0


def formater_rapport(
    rapport: Rapport, filnavn: str, fasit: Fasit | None, *, detaljer: bool = False
) -> str:
    linjer = [
        "Bestandskontroll – rapport",
        f"Fil: {filnavn}",
        f"Poliser: {rapport.antall_poliser}   Kontroller: {len(rapport.resultater)}   "
        f"Funn: {rapport.antall_funn}",
        "",
    ]

    bredde = max([len("Kontroll"), *(len(r.kontroll.navn) for r in rapport.resultater)])
    overskrift = f"{'Kontroll':<{bredde}}  {'Alvorlighet':<11}  {'Funn':>5}"
    if fasit is not None:
        overskrift += "  Fasit"
    linjer.append(overskrift)
    linjer.append("-" * len(overskrift))

    avvik: dict[str, FasitAvvik] = {}
    for resultat in rapport.resultater:
        rad = (
            f"{resultat.kontroll.navn:<{bredde}}  "
            f"{resultat.kontroll.alvorlighet.value:<11}  {len(resultat.funn):>5}"
        )
        if fasit is not None:
            avvik[resultat.kontroll.navn] = fasit.sammenlign(resultat)
            rad += f"  {avvik[resultat.kontroll.navn].tekst()}"
        linjer.append(rad)

    if detaljer:
        for resultat in rapport.resultater:
            if not resultat.funn:
                continue
            linjer += ["", f"{resultat.kontroll.navn}: {resultat.kontroll.beskrivelse}"]
            for funn in resultat.funn:
                linjer.append(f"  linje {funn.linje:>5}  {funn.polisenr or '(mangler PoliseNr)':<10}  {funn.melding}")

    if fasit is not None:
        for a in avvik.values():
            if a.ok:
                continue
            linjer.append("")
            if a.mangler_fasit:
                linjer.append(f"{a.kontroll}: finnes ikke i fasiten – kan ikke verifiseres.")
            if a.ikke_funnet:
                linjer.append(f"{a.kontroll}: i fasit, ikke funnet: {', '.join(sorted(a.ikke_funnet))}")
            if a.uventet:
                linjer.append(f"{a.kontroll}: funnet, ikke i fasit: {', '.join(sorted(a.uventet))}")

        gjenstaar = fasit.ikke_implementert(ALLE_KONTROLLER)
        linjer.append("")
        if gjenstaar:
            linjer.append(f"Kontroller i fasit som ikke er implementert ennå ({len(gjenstaar)}):")
            linjer.append("  " + ", ".join(gjenstaar))
        else:
            linjer.append("Alle kontroller i fasiten er implementert.")

    return "\n".join(linjer)
