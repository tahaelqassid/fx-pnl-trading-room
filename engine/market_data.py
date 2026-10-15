"""
Market Data Engine.
Provides historical and intraday candlestick series for FX pairs and Commodities.
Supports live Twelve Data API if configured, with an offline generator anchored
to current market rates (including Gold crossing above 4,000 USD/oz).
"""
import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

API_KEY = os.getenv("TWELVE_DATA_KEY")
BASE_URL = "https://api.twelvedata.com/time_series"


def _generate_synthetic_candles(symbol: str, interval: str, outputsize: int) -> pd.DataFrame:
    """
    Generates realistic candlestick series for charting and backtesting.
    Anchored to realistic market prices:
    - XAU/USD: Crossing the $4,000 mark (breaking out from 3,980 to 4,035+)
    - USD/MAD: BAM fixing corridor ~ 9.9200 - 9.9650
    - EUR/MAD: BAM fixing corridor ~ 10.7700 - 10.8200
    - EUR/USD: ~ 1.0820 - 1.0880
    """
    now = datetime.now()
    step_minutes = 15 if interval == "15min" else (60 if interval == "1h" else (240 if interval == "4h" else 1440))
    timestamps = [now - timedelta(minutes=step_minutes * i) for i in range(outputsize)]
    timestamps.reverse()

    if "XAU" in symbol or "GOLD" in symbol.upper():
        np.random.seed(101)
        # Gold starts below 4000 and crosses above 4000
        trend = np.linspace(-25.0, 32.0, outputsize)
        noise = np.cumsum(np.random.normal(0.2, 1.8, outputsize))
        base_series = 3995.0 + trend + noise
        decimals = 2
    elif "USD/MAD" in symbol:
        np.random.seed(42)
        noise = np.cumsum(np.random.normal(0.0001, 0.003, outputsize))
        base_series = 9.9400 + noise
        decimals = 4
    elif "EUR/MAD" in symbol:
        np.random.seed(55)
        noise = np.cumsum(np.random.normal(0.0001, 0.0035, outputsize))
        base_series = 10.7950 + noise
        decimals = 4
    else:  # EUR/USD default
        np.random.seed(77)
        noise = np.cumsum(np.random.normal(0.00005, 0.0008, outputsize))
        base_series = 1.0840 + noise
        decimals = 5

    candles = []
    for i, t in enumerate(timestamps):
        close_p = round(base_series[i], decimals)
        intra_spread = abs(np.random.normal(0, 0.0015 if decimals > 2 else 3.5))
        open_p = round(base_series[i - 1] if i > 0 else close_p - 0.0005, decimals)
        high_p = round(max(open_p, close_p) + intra_spread, decimals)
        low_p = round(min(open_p, close_p) - intra_spread, decimals)
        volume = int(np.random.uniform(1500, 12000))

        candles.append({
            "datetime": t,
            "open": open_p,
            "high": high_p,
            "low": low_p,
            "close": close_p,
            "volume": volume
        })

    return pd.DataFrame(candles)


def get_candles(symbol: str, interval: str = "15min", outputsize: int = 100) -> pd.DataFrame:
    """
    Retrieves candlestick series from live API or realistic fallback generator.
    """
    if API_KEY:
        try:
            resp = requests.get(BASE_URL, params={
                "symbol": symbol, "interval": interval, "outputsize": outputsize, "apikey": API_KEY,
            }, timeout=4)
            data = resp.json()
            if "values" in data:
                df = pd.DataFrame(data["values"])
                df["datetime"] = pd.to_datetime(df["datetime"])
                for col in ["open", "high", "low", "close"]:
                    df[col] = df[col].astype(float)
                return df.sort_values("datetime").reset_index(drop=True)
        except Exception:
            pass

    return _generate_synthetic_candles(symbol, interval, outputsize)