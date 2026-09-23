"""
Structural signal engine — market-structure based, not ML.

Identifies break-of-structure (BOS) and simple trend bias using swing
highs/lows. This is a technical-analysis signal, explicitly labeled
as such — not a trading recommendation, and honestly scoped to what
can actually be justified from price data alone.
"""
import pandas as pd


def find_swings(df: pd.DataFrame, lookback: int = 3) -> pd.DataFrame:
    df = df.copy()
    df["swing_high"] = df["high"][(df["high"] == df["high"].rolling(lookback * 2 + 1, center=True).max())]
    df["swing_low"] = df["low"][(df["low"] == df["low"].rolling(lookback * 2 + 1, center=True).min())]
    return df


def structure_signal(df: pd.DataFrame) -> dict:
    df = find_swings(df)
    swing_highs = df.dropna(subset=["swing_high"])
    swing_lows = df.dropna(subset=["swing_low"])

    if len(swing_highs) < 2 or len(swing_lows) < 2:
        return {"bias": "insufficient data", "detail": "not enough swing points yet"}

    last_close = df["close"].iloc[-1]
    last_high = swing_highs["swing_high"].iloc[-1]
    last_low = swing_lows["swing_low"].iloc[-1]
    prev_high = swing_highs["swing_high"].iloc[-2]
    prev_low = swing_lows["swing_low"].iloc[-2]

    if last_close > prev_high:
        bias = "bullish BOS"
        detail = f"price broke above prior swing high {prev_high:.5f}"
    elif last_close < prev_low:
        bias = "bearish BOS"
        detail = f"price broke below prior swing low {prev_low:.5f}"
    elif last_high > prev_high and last_low > prev_low:
        bias = "bullish structure"
        detail = "higher highs, higher lows"
    elif last_high < prev_high and last_low < prev_low:
        bias = "bearish structure"
        detail = "lower highs, lower lows"
    else:
        bias = "ranging"
        detail = "no clear structural bias"

    return {"bias": bias, "detail": detail, "last_close": round(last_close, 5)}