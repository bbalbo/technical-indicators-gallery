"""
Barrido completo del catálogo de la librería `ta` (40 indicadores).

Cada familia (momentum, trend, volatility, volume) tiene una función que recibe
el DataFrame OHLCV y devuelve un dict ordenado {nombre: Series}. `compute_all`
las junta todas. Los nombres de salida son los que consumen las galerías.

Referencia: https://technical-analysis-library-in-python.readthedocs.io
"""

from __future__ import annotations
from collections import OrderedDict
import numpy as np
import pandas as pd

import ta.momentum as tm
import ta.trend as tt
import ta.volatility as tv
import ta.volume as tvol


def momentum(df: pd.DataFrame) -> "OrderedDict[str, pd.Series]":
    h, l, c, v = df["High"], df["Low"], df["Close"], df["Volume"]
    o = OrderedDict()
    o["RSI"] = tm.RSIIndicator(c, window=14).rsi()
    stoch = tm.StochasticOscillator(h, l, c, window=14, smooth_window=3)
    o["Stoch %K"] = stoch.stoch()
    o["Stoch %D"] = stoch.stoch_signal()
    srsi = tm.StochRSIIndicator(c, window=14)
    o["StochRSI %K"] = srsi.stochrsi_k()
    o["StochRSI %D"] = srsi.stochrsi_d()
    o["Awesome Osc."] = tm.AwesomeOscillatorIndicator(h, l, 5, 34).awesome_oscillator()
    o["KAMA"] = tm.KAMAIndicator(c, window=10).kama()
    o["ROC"] = tm.ROCIndicator(c, window=12).roc()
    o["TSI"] = tm.TSIIndicator(c).tsi()
    o["Ultimate Osc."] = tm.UltimateOscillator(h, l, c).ultimate_oscillator()
    o["Williams %R"] = tm.WilliamsRIndicator(h, l, c, lbp=14).williams_r()
    ppo = tm.PercentagePriceOscillator(c)
    o["PPO"] = ppo.ppo()
    o["PPO signal"] = ppo.ppo_signal()
    o["PPO hist"] = ppo.ppo_hist()
    pvo = tm.PercentageVolumeOscillator(v)
    o["PVO"] = pvo.pvo()
    o["PVO signal"] = pvo.pvo_signal()
    o["PVO hist"] = pvo.pvo_hist()
    return o


def trend(df: pd.DataFrame) -> "OrderedDict[str, pd.Series]":
    h, l, c = df["High"], df["Low"], df["Close"]
    o = OrderedDict()
    o["SMA 20"] = tt.SMAIndicator(c, window=20).sma_indicator()
    o["EMA 20"] = tt.EMAIndicator(c, window=20).ema_indicator()
    o["WMA 20"] = tt.WMAIndicator(c, window=20).wma()
    macd = tt.MACD(c)
    o["MACD"] = macd.macd()
    o["MACD signal"] = macd.macd_signal()
    o["MACD hist"] = macd.macd_diff()
    adx = tt.ADXIndicator(h, l, c, window=14)
    o["ADX"] = adx.adx()
    o["+DI"] = adx.adx_pos()
    o["-DI"] = adx.adx_neg()
    aroon = tt.AroonIndicator(h, l, window=25)
    o["Aroon Up"] = aroon.aroon_up()
    o["Aroon Down"] = aroon.aroon_down()
    o["CCI"] = tt.CCIIndicator(h, l, c, window=20).cci()
    o["DPO"] = tt.DPOIndicator(c, window=20).dpo()
    ichi = tt.IchimokuIndicator(h, l)
    o["Ichimoku A"] = ichi.ichimoku_a()
    o["Ichimoku B"] = ichi.ichimoku_b()
    o["Ichimoku Conv."] = ichi.ichimoku_conversion_line()
    o["Ichimoku Base"] = ichi.ichimoku_base_line()
    kst = tt.KSTIndicator(c)
    o["KST"] = kst.kst()
    o["KST signal"] = kst.kst_sig()
    o["Mass Index"] = tt.MassIndex(h, l).mass_index()
    o["PSAR"] = tt.PSARIndicator(h, l, c).psar()
    o["STC"] = tt.STCIndicator(c).stc()
    o["TRIX"] = tt.TRIXIndicator(c, window=15).trix()
    vi = tt.VortexIndicator(h, l, c, window=14)
    o["Vortex +"] = vi.vortex_indicator_pos()
    o["Vortex -"] = vi.vortex_indicator_neg()
    return o


def volatility(df: pd.DataFrame) -> "OrderedDict[str, pd.Series]":
    h, l, c = df["High"], df["Low"], df["Close"]
    o = OrderedDict()
    o["ATR"] = tv.AverageTrueRange(h, l, c, window=14).average_true_range()
    bb = tv.BollingerBands(c, window=20, window_dev=2)
    o["BB high"] = bb.bollinger_hband()
    o["BB mid"] = bb.bollinger_mavg()
    o["BB low"] = bb.bollinger_lband()
    dc = tv.DonchianChannel(h, l, c, window=20)
    o["Donchian high"] = dc.donchian_channel_hband()
    o["Donchian mid"] = dc.donchian_channel_mband()
    o["Donchian low"] = dc.donchian_channel_lband()
    kc = tv.KeltnerChannel(h, l, c, window=20)
    o["Keltner high"] = kc.keltner_channel_hband()
    o["Keltner mid"] = kc.keltner_channel_mband()
    o["Keltner low"] = kc.keltner_channel_lband()
    o["Ulcer Index"] = tv.UlcerIndex(c, window=14).ulcer_index()
    return o


def volume(df: pd.DataFrame) -> "OrderedDict[str, pd.Series]":
    h, l, c, v = df["High"], df["Low"], df["Close"], df["Volume"]
    o = OrderedDict()
    o["OBV"] = tvol.OnBalanceVolumeIndicator(c, v).on_balance_volume()
    o["Acc/Dist"] = tvol.AccDistIndexIndicator(h, l, c, v).acc_dist_index()
    o["CMF"] = tvol.ChaikinMoneyFlowIndicator(h, l, c, v, window=20).chaikin_money_flow()
    o["Force Index"] = tvol.ForceIndexIndicator(c, v, window=13).force_index()
    o["MFI"] = tvol.MFIIndicator(h, l, c, v, window=14).money_flow_index()
    o["Ease of Move."] = tvol.EaseOfMovementIndicator(h, l, v, window=14).ease_of_movement()
    o["VPT"] = tvol.VolumePriceTrendIndicator(c, v).volume_price_trend()
    o["NVI"] = tvol.NegativeVolumeIndexIndicator(c, v).negative_volume_index()
    o["VWAP"] = tvol.VolumeWeightedAveragePrice(h, l, c, v, window=14).volume_weighted_average_price()
    return o


FAMILIAS = {
    "momentum": momentum,
    "trend": trend,
    "volatility": volatility,
    "volume": volume,
}


def _alinear(s: pd.Series, index: pd.Index) -> pd.Series:
    """
    Fuerza una serie de indicador al índice del precio. Algunos indicadores de
    `ta` (p. ej. PSAR) devuelven una serie con índice propio y largo distinto;
    nos quedamos con los primeros len(index) valores, en orden.
    """
    arr = np.asarray(s, dtype=float)
    n = len(index)
    if len(arr) >= n:
        arr = arr[:n]
    else:
        arr = np.concatenate([np.full(n - len(arr), np.nan), arr])
    return pd.Series(arr, index=index)


def compute_all(df: pd.DataFrame) -> "OrderedDict[str, OrderedDict]":
    """Devuelve {familia: {nombre: Series}} con todo el catálogo calculado."""
    out = OrderedDict()
    for fam, fn in FAMILIAS.items():
        crudo = fn(df)
        out[fam] = OrderedDict((k, _alinear(v, df.index)) for k, v in crudo.items())
    return out


def contar(res) -> int:
    """Cuenta indicadores lógicos (agrupando sub-series como MACD/BB)."""
    return sum(len(v) for v in res.values())


if __name__ == "__main__":
    from data import cargar
    df, fuente = cargar(permitir_sintetico=True)
    res = compute_all(df)
    for fam, d in res.items():
        print(f"{fam}: {len(d)} series -> {list(d)[:5]}...")
    print("total series:", contar(res))
