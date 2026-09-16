"""
Punto de entrada: genera la galería completa de indicadores.

    python src/gallery.py --ticker MSTR --period 5y --interval 1wk

Descarga los datos (yfinance; si no hay red, usa datos sintéticos), computa el
catálogo completo de `ta` y escribe las figuras en figures/.
"""

from __future__ import annotations
import argparse
import logging
from pathlib import Path

from data import cargar
from indicators import compute_all, contar
import plots

FIG_DIR = Path(__file__).resolve().parent.parent / "figures"


def main():
    ap = argparse.ArgumentParser(description="Technical Indicators Gallery")
    ap.add_argument("--ticker", default="MSTR")
    ap.add_argument("--period", default="5y")
    ap.add_argument("--interval", default="1wk")
    ap.add_argument("--no-synthetic", action="store_true",
                    help="Falla si yfinance no está disponible (no usa datos sintéticos).")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    FIG_DIR.mkdir(exist_ok=True)

    df, fuente = cargar(args.ticker, args.period, args.interval,
                        permitir_sintetico=not args.no_synthetic)
    logging.info("Fuente de datos: %s | %d filas", fuente, len(df))

    ind = compute_all(df)
    logging.info("Indicadores calculados: %d series en %d familias",
                 contar(ind), len(ind))

    plots.plot_hero(df, ind, args.ticker, fuente, FIG_DIR / "00_hero.png")
    for fam, fn in plots.GALERIAS.items():
        fn(df, ind, FIG_DIR / f"{fam}.png")
        logging.info("Figura lista: figures/%s.png", fam)

    print("\nGalería generada en:", FIG_DIR)
    print("Fuente:", fuente, "| ticker:", args.ticker)


if __name__ == "__main__":
    main()
