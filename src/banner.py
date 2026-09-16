"""
Genera la imagen de portada (social preview) del repo: 1280×640 px.
Se sube en GitHub → Settings → Social preview, y es lo que LinkedIn muestra
en la tarjeta de "Destacado".

    python src/banner.py
"""
from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt

from data import cargar
from indicators import compute_all
import theme as T
import plots as P

OUT = Path(__file__).resolve().parent.parent / "docs" / "social-preview.png"


def main():
    T.apply_theme()
    df, _ = cargar(permitir_sintetico=True)   # banner reproducible sin red
    ind = compute_all(df)
    x = df.index

    fig = plt.figure(figsize=(12.8, 6.4))
    fig.patch.set_facecolor(T.PLANE)

    # Título
    fig.text(0.045, 0.83, "Technical Indicators Gallery",
             color=T.INK, fontsize=30, fontweight="bold", ha="left")
    fig.text(0.046, 0.72,
             "40 indicadores técnicos de la librería  ta  ·  datos reales  ·  Python",
             color=T.INK_2, fontsize=13.5, ha="left")
    fig.text(0.046, 0.655,
             "momentum · tendencia · volatilidad · volumen",
             color=T.color(0), fontsize=12, ha="left", fontweight="bold")

    # Cuatro mini-paneles representativos
    specs = [0.045, 0.285, 0.525, 0.765]
    w = 0.19
    axes = [fig.add_axes([lx, 0.10, w, 0.42]) for lx in specs]
    for a in axes:
        T.style_axis(a)
        a.set_xticks([]); a.set_yticks([])

    # 1) Velas + Bollinger
    P.candles(axes[0], df.iloc[-70:], width_frac=0.7)
    v = ind["volatility"]
    axes[0].plot(x[-70:], v["BB high"].iloc[-70:], color=T.BAND, lw=0.8, ls="--", alpha=0.7)
    axes[0].plot(x[-70:], v["BB low"].iloc[-70:], color=T.BAND, lw=0.8, ls="--", alpha=0.7)
    axes[0].set_title("Precio + Bollinger", color=T.INK_2, fontsize=9, loc="left", pad=4)

    # 2) RSI con zonas
    m = ind["momentum"]
    T.zone(axes[1], 70, 100, T.DOWN, 0.14); T.zone(axes[1], 0, 30, T.UP, 0.14)
    axes[1].plot(x, m["RSI"], color=T.color(0), lw=1.4)
    axes[1].fill_between(x, m["RSI"], 0, color=T.color(0), alpha=0.10)
    axes[1].set_ylim(0, 100)
    axes[1].set_title("RSI", color=T.INK_2, fontsize=9, loc="left", pad=4)

    # 3) MACD histograma divergente
    t = ind["trend"]
    P.diverging_bars(axes[2], x, t["MACD hist"])
    axes[2].plot(x, t["MACD"], color=T.color(0), lw=1.0)
    axes[2].plot(x, t["MACD signal"], color=T.color(3), lw=1.0)
    axes[2].set_title("MACD", color=T.INK_2, fontsize=9, loc="left", pad=4)

    # 4) OBV con relleno
    vol = ind["volume"]
    axes[3].plot(x, vol["OBV"], color=T.color(2), lw=1.4)
    axes[3].fill_between(x, vol["OBV"], vol["OBV"].min(), color=T.color(2), alpha=0.12)
    axes[3].set_title("On-Balance Volume", color=T.INK_2, fontsize=9, loc="left", pad=4)

    T.watermark(fig, "github.com/bbalbo/technical-indicators-gallery")
    OUT.parent.mkdir(exist_ok=True)
    fig.savefig(OUT, dpi=100, facecolor=T.PLANE)
    plt.close(fig)
    print("Banner:", OUT, "->", f"{OUT.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
