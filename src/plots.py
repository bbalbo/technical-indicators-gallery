"""
Galerías de gráficos — una figura por familia de indicadores, más un gráfico
"hero" de precio. Todo con el mismo tema oscuro y colorido (theme.py).

Cada figura es una grilla de paneles que comparten el eje temporal. El objetivo
es que el catálogo completo de `ta` se lea de un vistazo y se vea bien.
"""

from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.collections import LineCollection

import theme as T


# ── Primitivas de dibujo ──────────────────────────────────────────────────────
def _fmt_dates(ax):
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))


def line(ax, x, y, color, label=None, lw=1.6, alpha=1.0, ls="-", fill=False):
    ax.plot(x, y, color=color, lw=lw, alpha=alpha, ls=ls, label=label, zorder=3)
    if fill:
        base = np.nanmin(y.values if hasattr(y, "values") else y)
        ax.fill_between(x, y, base, color=color, alpha=0.10, zorder=1, lw=0)


def diverging_bars(ax, x, y, up=T.UP, down=T.DOWN, width=None):
    """Barras verde/rojo alrededor de cero (MACD hist, Awesome Osc., etc.)."""
    y = np.asarray(y, dtype=float)
    colors = np.where(y >= 0, up, down)
    if width is None:
        width = (mdates.date2num(x[-1]) - mdates.date2num(x[0])) / max(len(x), 1) * 0.8
    ax.bar(x, y, color=colors, width=width, zorder=2, linewidth=0)
    ax.axhline(0, color=T.AXIS, lw=0.8, zorder=1)


def candles(ax, df, width_frac=0.7):
    """Velas japonesas (verde alza / rojo baja) con mecha."""
    x = mdates.date2num(df.index.to_pydatetime())
    w = (x[1] - x[0]) * width_frac if len(x) > 1 else 1.0
    o, h, l, c = df["Open"].values, df["High"].values, df["Low"].values, df["Close"].values
    up = c >= o
    col = np.where(up, T.UP, T.DOWN)
    # mechas como LineCollection (rápido)
    wicks = LineCollection([[(xi, li), (xi, hi)] for xi, li, hi in zip(x, l, h)],
                           colors=col, linewidths=0.9, zorder=2)
    ax.add_collection(wicks)
    # cuerpos
    bottom = np.minimum(o, c)
    height = np.abs(c - o)
    height[height == 0] = (h - l)[height == 0] * 0.05 + 1e-9  # dojis visibles
    ax.bar(x, height, bottom=bottom, width=w, color=col, edgecolor=col,
           linewidth=0.4, zorder=3)
    ax.xaxis_date()


def _panel(ax, title):
    T.style_axis(ax, title)
    _fmt_dates(ax)
    return ax


def _legend(ax, ncol=1, loc="upper left"):
    leg = ax.legend(loc=loc, ncol=ncol, fontsize=7.5, framealpha=0.85)
    if leg:
        for t in leg.get_texts():
            t.set_color(T.INK_2)


# ── HERO: precio + medias + Bollinger + Ichimoku + PSAR + volumen ─────────────
def plot_hero(df, ind, ticker, fuente, out):
    T.apply_theme()
    fig, (axp, axv) = plt.subplots(
        2, 1, figsize=(15, 9), height_ratios=[3.2, 1], sharex=True,
        gridspec_kw={"hspace": 0.06})

    x = df.index
    tr, vol = ind["trend"], ind["volatility"]

    # Nube Ichimoku
    a, b = tr["Ichimoku A"], tr["Ichimoku B"]
    axp.fill_between(x, a, b, where=(a >= b), color=T.UP, alpha=0.10, lw=0, zorder=0)
    axp.fill_between(x, a, b, where=(a < b), color=T.DOWN, alpha=0.10, lw=0, zorder=0)

    # Bandas de Bollinger
    axp.fill_between(x, vol["BB high"], vol["BB low"], color=T.BAND,
                     alpha=0.08, lw=0, zorder=0)
    line(axp, x, vol["BB high"], T.BAND, lw=0.9, alpha=0.6, ls="--")
    line(axp, x, vol["BB low"], T.BAND, lw=0.9, alpha=0.6, ls="--")

    candles(axp, df)

    # Medias móviles
    line(axp, x, tr["SMA 20"], T.color(3), "SMA 20", lw=1.4)
    line(axp, x, tr["EMA 20"], T.color(1), "EMA 20", lw=1.4)
    line(axp, x, tr["WMA 20"], T.color(6), "WMA 20", lw=1.2, alpha=0.9)

    # PSAR (puntos)
    axp.scatter(x, tr["PSAR"], s=6, color=T.ACCENT, alpha=0.8, zorder=4, label="PSAR")

    _panel(axp, f"{ticker} — Precio, medias móviles, Bollinger, Ichimoku y PSAR")
    axp.set_ylabel("Precio")
    _legend(axp, ncol=2)

    # Volumen coloreado por dirección
    up = df["Close"].values >= df["Open"].values
    axv.bar(x, df["Volume"], width=(mdates.date2num(x[-1]) - mdates.date2num(x[0])) / len(x) * 0.8,
            color=np.where(up, T.UP, T.DOWN), alpha=0.7, linewidth=0)
    _panel(axv, "Volumen")
    axv.set_ylabel("Vol.")

    etiqueta = "datos sintéticos (demo)" if fuente == "sintetico" else "datos: Yahoo Finance"
    fig.suptitle(f"Technical Indicators Gallery · {ticker}", color=T.INK, x=0.09, ha="left")
    T.watermark(fig, f"librería ta · {etiqueta}")
    fig.savefig(out)
    plt.close(fig)
    return out


# ── Utilidad: grilla de paneles ───────────────────────────────────────────────
def _grid(nrows, ncols, figsize):
    T.apply_theme()
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize,
                             gridspec_kw={"hspace": 0.35, "wspace": 0.18})
    return fig, np.array(axes).reshape(-1)


# ── MOMENTUM ──────────────────────────────────────────────────────────────────
def plot_momentum(df, ind, out):
    m = ind["momentum"]
    x = df.index
    fig, ax = _grid(4, 3, (15, 12))

    _panel(ax[0], "RSI (14)")
    T.zone(ax[0], 70, 100, T.DOWN, 0.10); T.zone(ax[0], 0, 30, T.UP, 0.10)
    line(ax[0], x, m["RSI"], T.color(0), fill=True); ax[0].set_ylim(0, 100)

    _panel(ax[1], "Stochastic")
    T.zone(ax[1], 80, 100, T.DOWN, 0.10); T.zone(ax[1], 0, 20, T.UP, 0.10)
    line(ax[1], x, m["Stoch %K"], T.color(0), "%K")
    line(ax[1], x, m["Stoch %D"], T.color(3), "%D", lw=1.1); _legend(ax[1])

    _panel(ax[2], "Stochastic RSI")
    line(ax[2], x, m["StochRSI %K"], T.color(0), "%K")
    line(ax[2], x, m["StochRSI %D"], T.color(3), "%D", lw=1.1); _legend(ax[2])

    _panel(ax[3], "Awesome Oscillator")
    diverging_bars(ax[3], x, m["Awesome Osc."])

    _panel(ax[4], "KAMA vs Close")
    line(ax[4], x, df["Close"], T.PRICE, "Close", lw=1.0, alpha=0.7)
    line(ax[4], x, m["KAMA"], T.color(1), "KAMA"); _legend(ax[4])

    _panel(ax[5], "Rate of Change (12)")
    line(ax[5], x, m["ROC"], T.color(4), fill=True); ax[5].axhline(0, color=T.AXIS, lw=0.8)

    _panel(ax[6], "True Strength Index")
    line(ax[6], x, m["TSI"], T.color(6), fill=True); ax[6].axhline(0, color=T.AXIS, lw=0.8)

    _panel(ax[7], "Ultimate Oscillator")
    T.zone(ax[7], 70, 100, T.DOWN, 0.10); T.zone(ax[7], 0, 30, T.UP, 0.10)
    line(ax[7], x, m["Ultimate Osc."], T.color(2), fill=True)

    _panel(ax[8], "Williams %R")
    line(ax[8], x, m["Williams %R"], T.color(7), fill=True)

    _panel(ax[9], "PPO — Percentage Price Osc.")
    diverging_bars(ax[9], x, m["PPO hist"])
    line(ax[9], x, m["PPO"], T.color(0), "PPO"); line(ax[9], x, m["PPO signal"], T.color(3), "signal", lw=1.1)
    _legend(ax[9])

    _panel(ax[10], "PVO — Percentage Volume Osc.")
    diverging_bars(ax[10], x, m["PVO hist"])
    line(ax[10], x, m["PVO"], T.color(0), "PVO"); line(ax[10], x, m["PVO signal"], T.color(3), "signal", lw=1.1)
    _legend(ax[10])

    ax[11].axis("off")
    fig.suptitle("Momentum — 11 indicadores", color=T.INK, x=0.09, ha="left")
    T.watermark(fig, "librería ta · familia momentum")
    fig.savefig(out); plt.close(fig)
    return out


# ── TREND ─────────────────────────────────────────────────────────────────────
def plot_trend(df, ind, out):
    t = ind["trend"]
    x = df.index
    fig, ax = _grid(4, 3, (15, 12))

    _panel(ax[0], "MACD")
    diverging_bars(ax[0], x, t["MACD hist"])
    line(ax[0], x, t["MACD"], T.color(0), "MACD"); line(ax[0], x, t["MACD signal"], T.color(3), "signal", lw=1.1)
    _legend(ax[0])

    _panel(ax[1], "ADX / DMI")
    line(ax[1], x, t["ADX"], T.PRICE, "ADX", lw=1.8)
    line(ax[1], x, t["+DI"], T.UP, "+DI", lw=1.1); line(ax[1], x, t["-DI"], T.DOWN, "-DI", lw=1.1)
    _legend(ax[1])

    _panel(ax[2], "Aroon")
    line(ax[2], x, t["Aroon Up"], T.UP, "Up"); line(ax[2], x, t["Aroon Down"], T.DOWN, "Down")
    _legend(ax[2])

    _panel(ax[3], "CCI (20)")
    T.zone(ax[3], 100, ax[3].get_ylim()[1] if False else 300, T.DOWN, 0.08)
    line(ax[3], x, t["CCI"], T.color(4)); ax[3].axhline(0, color=T.AXIS, lw=0.8)

    _panel(ax[4], "DPO — Detrended Price Osc.")
    diverging_bars(ax[4], x, t["DPO"])

    _panel(ax[5], "KST — Know Sure Thing")
    line(ax[5], x, t["KST"], T.color(0), "KST", fill=True)
    line(ax[5], x, t["KST signal"], T.color(3), "signal", lw=1.1); _legend(ax[5])

    _panel(ax[6], "Mass Index")
    line(ax[6], x, t["Mass Index"], T.color(6))
    ax[6].axhline(27, color=T.WARN, lw=0.9, ls="--", alpha=0.7)

    _panel(ax[7], "STC — Schaff Trend Cycle")
    line(ax[7], x, t["STC"], T.color(5), fill=True); ax[7].set_ylim(0, 100)

    _panel(ax[8], "TRIX")
    line(ax[8], x, t["TRIX"], T.color(1), fill=True); ax[8].axhline(0, color=T.AXIS, lw=0.8)

    _panel(ax[9], "Vortex")
    line(ax[9], x, t["Vortex +"], T.UP, "VI+"); line(ax[9], x, t["Vortex -"], T.DOWN, "VI-")
    _legend(ax[9])

    _panel(ax[10], "Ichimoku Kinko Hyo")
    a, b = t["Ichimoku A"], t["Ichimoku B"]
    ax[10].fill_between(x, a, b, where=(a >= b), color=T.UP, alpha=0.15, lw=0)
    ax[10].fill_between(x, a, b, where=(a < b), color=T.DOWN, alpha=0.15, lw=0)
    line(ax[10], x, df["Close"], T.PRICE, "Close", lw=1.0, alpha=0.7)
    line(ax[10], x, t["Ichimoku Conv."], T.color(0), "Conversion", lw=1.0)
    line(ax[10], x, t["Ichimoku Base"], T.color(4), "Base", lw=1.0); _legend(ax[10])

    _panel(ax[11], "PSAR vs Close")
    line(ax[11], x, df["Close"], T.PRICE, "Close", lw=1.0, alpha=0.7)
    ax[11].scatter(x, t["PSAR"], s=7, color=T.ACCENT, label="PSAR"); _legend(ax[11])

    fig.suptitle("Trend — 15 indicadores", color=T.INK, x=0.09, ha="left")
    T.watermark(fig, "librería ta · familia trend")
    fig.savefig(out); plt.close(fig)
    return out


# ── VOLATILITY ────────────────────────────────────────────────────────────────
def plot_volatility(df, ind, out):
    v = ind["volatility"]
    x = df.index
    fig, ax = _grid(3, 2, (15, 10))

    def _channel(a, title, hband, mband, lband, col):
        _panel(a, title)
        candles(df=df, ax=a); a.set_ylabel("Precio")
        a.fill_between(x, hband, lband, color=col, alpha=0.10, lw=0)
        line(a, x, hband, col, lw=1.0, ls="--", alpha=0.8)
        line(a, x, mband, col, lw=1.1)
        line(a, x, lband, col, lw=1.0, ls="--", alpha=0.8)

    _channel(ax[0], "Bollinger Bands (20, 2σ)", v["BB high"], v["BB mid"], v["BB low"], T.color(0))
    _channel(ax[1], "Keltner Channel (20)", v["Keltner high"], v["Keltner mid"], v["Keltner low"], T.color(3))
    _channel(ax[2], "Donchian Channel (20)", v["Donchian high"], v["Donchian mid"], v["Donchian low"], T.color(4))

    _panel(ax[3], "Average True Range (14)")
    line(ax[3], x, v["ATR"], T.color(1), fill=True)

    _panel(ax[4], "Ulcer Index (14)")
    line(ax[4], x, v["Ulcer Index"], T.color(7), fill=True)

    ax[5].axis("off")
    fig.suptitle("Volatility — 5 indicadores", color=T.INK, x=0.09, ha="left")
    T.watermark(fig, "librería ta · familia volatility")
    fig.savefig(out); plt.close(fig)
    return out


# ── VOLUME ────────────────────────────────────────────────────────────────────
def plot_volume(df, ind, out):
    vol = ind["volume"]
    x = df.index
    fig, ax = _grid(3, 3, (15, 11))

    _panel(ax[0], "On-Balance Volume")
    line(ax[0], x, vol["OBV"], T.color(0), fill=True)

    _panel(ax[1], "Accumulation / Distribution")
    line(ax[1], x, vol["Acc/Dist"], T.color(2), fill=True)

    _panel(ax[2], "Chaikin Money Flow (20)")
    diverging_bars(ax[2], x, vol["CMF"])

    _panel(ax[3], "Force Index (13)")
    line(ax[3], x, vol["Force Index"], T.color(4)); ax[3].axhline(0, color=T.AXIS, lw=0.8)

    _panel(ax[4], "Money Flow Index (14)")
    T.zone(ax[4], 80, 100, T.DOWN, 0.10); T.zone(ax[4], 0, 20, T.UP, 0.10)
    line(ax[4], x, vol["MFI"], T.color(5), fill=True); ax[4].set_ylim(0, 100)

    _panel(ax[5], "Ease of Movement (14)")
    diverging_bars(ax[5], x, vol["Ease of Move."])

    _panel(ax[6], "Volume Price Trend")
    line(ax[6], x, vol["VPT"], T.color(6), fill=True)

    _panel(ax[7], "Negative Volume Index")
    line(ax[7], x, vol["NVI"], T.color(1), fill=True)

    _panel(ax[8], "VWAP vs Close")
    line(ax[8], x, df["Close"], T.PRICE, "Close", lw=1.0, alpha=0.7)
    line(ax[8], x, vol["VWAP"], T.color(3), "VWAP"); _legend(ax[8])

    fig.suptitle("Volume — 9 indicadores", color=T.INK, x=0.09, ha="left")
    T.watermark(fig, "librería ta · familia volume")
    fig.savefig(out); plt.close(fig)
    return out


GALERIAS = {
    "momentum": plot_momentum,
    "trend": plot_trend,
    "volatility": plot_volatility,
    "volume": plot_volume,
}
