"""
Carga de datos de mercado (OHLCV).

Fuente principal: **yfinance** (Yahoo Finance, sin API key).
Fallback: un generador **sintético** realista (movimiento browniano geométrico
con volatilidad por regímenes), para que el proyecto corra y las galerías se
puedan reproducir aún sin conexión — útil en CI offline o para pruebas.
"""

from __future__ import annotations
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

COLUMNS = ["Open", "High", "Low", "Close", "Volume"]


def _normalizar(df: pd.DataFrame) -> pd.DataFrame:
    """Deja columnas Open/High/Low/Close/Volume y un índice de fechas limpio."""
    if isinstance(df.columns, pd.MultiIndex):
        # yfinance devuelve MultiIndex cuando hay >1 ticker; nos quedamos con el nivel 0
        df = df.copy()
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns=str.title)
    faltantes = [c for c in COLUMNS if c not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas en los datos: {faltantes}")
    df = df[COLUMNS].dropna()
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df.index.name = "Date"
    return df


def cargar_yfinance(ticker: str, period: str = "5y",
                    interval: str = "1wk") -> pd.DataFrame:
    """Descarga OHLCV desde Yahoo Finance."""
    import yfinance as yf
    logger.info("Descargando %s (%s, %s) desde Yahoo Finance...", ticker, period, interval)
    df = yf.download(ticker, period=period, interval=interval,
                     auto_adjust=True, progress=False)
    if df is None or df.empty:
        raise ValueError(f"Yahoo Finance no devolvió datos para {ticker!r}.")
    return _normalizar(df)


def generar_sintetico(n: int = 260, seed: int = 7,
                      precio_inicial: float = 100.0) -> pd.DataFrame:
    """
    Genera una serie OHLCV sintética pero realista (GBM con regímenes de
    volatilidad, tendencia suave y volumen correlacionado con el rango).
    """
    rng = np.random.default_rng(seed)

    # Fechas primero (el date_range anclado a lunes puede ajustar el conteo)
    fechas = pd.date_range(end=pd.Timestamp.today().normalize(),
                           periods=n, freq="W-MON")
    n = len(fechas)

    # Regímenes de volatilidad (baja / media / alta) que se alternan
    regimenes = rng.choice([0.015, 0.03, 0.06], size=n,
                           p=[0.5, 0.35, 0.15])
    deriva = 0.0015 + 0.004 * np.sin(np.linspace(0, 6 * np.pi, n))  # tendencia ondulante
    retornos = rng.normal(deriva, regimenes)
    close = precio_inicial * np.exp(np.cumsum(retornos))

    # Construir OHLC alrededor del close
    open_ = np.empty(n)
    open_[0] = precio_inicial
    open_[1:] = close[:-1] * (1 + rng.normal(0, 0.004, n - 1))
    rango = np.abs(rng.normal(0, regimenes, n)) * close
    high = np.maximum(open_, close) + rango * rng.uniform(0.2, 1.0, n)
    low = np.minimum(open_, close) - rango * rng.uniform(0.2, 1.0, n)

    # Volumen: sube con el rango relativo y con caídas (pánico)
    rango_rel = (high - low) / close
    caida = np.clip(-retornos, 0, None)
    vol_base = rng.lognormal(mean=15, sigma=0.35, size=n)
    volume = vol_base * (1 + 6 * rango_rel + 8 * caida)

    df = pd.DataFrame({
        "Open": open_, "High": high, "Low": low,
        "Close": close, "Volume": volume.round().astype(int),
    }, index=fechas)
    df.index.name = "Date"
    return df


def cargar(ticker: str = "MSTR", period: str = "5y", interval: str = "1wk",
           permitir_sintetico: bool = True) -> tuple[pd.DataFrame, str]:
    """
    Carga OHLCV. Intenta yfinance; si falla y `permitir_sintetico`, cae al
    generador sintético. Devuelve (df, fuente) con fuente en {"yfinance","sintetico"}.
    """
    try:
        return cargar_yfinance(ticker, period, interval), "yfinance"
    except Exception as e:  # red caída, ticker inválido, rate limit, etc.
        if not permitir_sintetico:
            raise
        logger.warning("yfinance no disponible (%s). Usando datos sintéticos.", e)
        return generar_sintetico(), "sintetico"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    df, fuente = cargar()
    print(f"Fuente: {fuente} | filas: {len(df)}")
    print(df.tail())
