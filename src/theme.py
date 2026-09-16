"""
Tema visual del proyecto — paleta oscura, colorida y accesible.

La paleta categórica es *colorblind-safe*: el orden de los tonos está elegido
para que cada par adyacente mantenga separación suficiente bajo las principales
deficiencias de visión de color (protanopía, deuteranopía, tritanopía).

Un único punto de verdad para colores y estilo: todo el resto del proyecto
pinta "por rol" (precio, señal, banda, positivo/negativo) y nunca con hex sueltos.
"""

from __future__ import annotations
import matplotlib as mpl
import matplotlib.pyplot as plt

# ── Superficies e ink (tema oscuro) ───────────────────────────────────────────
SURFACE = "#1a1a19"     # fondo de cada gráfico
PLANE = "#0d0d0d"       # fondo de la figura
INK = "#ffffff"         # texto primario
INK_2 = "#c3c2b7"       # texto secundario
MUTED = "#898781"       # ejes / etiquetas tenues
GRID = "#2c2c2a"        # rejilla (hairline)
AXIS = "#383835"        # línea base / spines

# ── Paleta categórica (orden fijo, validado para CVD) ─────────────────────────
# Nunca se cicla ni se reordena: el orden ES el mecanismo de seguridad.
CATEGORICAL = [
    "#3987e5",  # 1 azul
    "#d95926",  # 2 naranja
    "#199e70",  # 3 aqua
    "#c98500",  # 4 amarillo
    "#d55181",  # 5 magenta
    "#008300",  # 6 verde
    "#9085e9",  # 7 violeta
    "#e66767",  # 8 rojo
]

# ── Roles semánticos ──────────────────────────────────────────────────────────
PRICE = "#e8e6df"       # línea/velas de precio (neutro claro)
UP = "#0ca30c"          # velas / barras al alza (verde estado)
DOWN = "#d03b3b"        # velas / barras a la baja (rojo estado)
SIGNAL = "#c98500"      # líneas de señal (ej. MACD signal)
BAND = "#3987e5"        # bandas / canales (azul)
ACCENT = "#d55181"      # acento secundario (magenta)
WARN = "#fab219"        # zona de alerta (amarillo estado)

# Sub-rampa azul para gradientes/relleno (sequential, claro→oscuro)
BLUE_RAMP = ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#104281"]


def color(i: int) -> str:
    """Color categórico por índice, en orden fijo (envuelve con módulo)."""
    return CATEGORICAL[i % len(CATEGORICAL)]


def apply_theme() -> None:
    """Aplica el tema oscuro a matplotlib globalmente."""
    mpl.rcParams.update({
        "figure.facecolor": PLANE,
        "savefig.facecolor": PLANE,
        "axes.facecolor": SURFACE,
        "axes.edgecolor": AXIS,
        "axes.labelcolor": INK_2,
        "axes.titlecolor": INK,
        "axes.linewidth": 0.8,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "grid.alpha": 1.0,
        "text.color": INK,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "legend.facecolor": SURFACE,
        "legend.edgecolor": AXIS,
        "legend.framealpha": 0.9,
        "legend.fontsize": 8.5,
        "font.family": ["DejaVu Sans", "sans-serif"],
        "font.size": 10,
        "figure.titlesize": 15,
        "figure.titleweight": "bold",
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "lines.linewidth": 1.6,
        "lines.solid_capstyle": "round",
        "savefig.dpi": 140,
        "savefig.bbox": "tight",
    })


def style_axis(ax, title: str | None = None):
    """Estiliza un eje: spines tenues, rejilla suave, título consistente."""
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(AXIS)
    ax.grid(True, color=GRID, linewidth=0.6, alpha=1.0)
    ax.set_axisbelow(True)
    if title:
        ax.set_title(title, color=INK, fontsize=11, fontweight="bold",
                     loc="left", pad=8)
    return ax


def zone(ax, low, high, color_hex=WARN, alpha=0.08):
    """Sombrea una banda horizontal (ej. sobrecompra/sobreventa del RSI)."""
    ax.axhspan(low, high, color=color_hex, alpha=alpha, zorder=0, lw=0)


def watermark(fig, text):
    """Firma discreta en la esquina inferior derecha de la figura."""
    fig.text(0.995, 0.004, text, ha="right", va="bottom",
             color=MUTED, fontsize=7.5, alpha=0.8)
