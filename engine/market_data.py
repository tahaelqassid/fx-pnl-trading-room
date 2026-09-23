"""
Real-time-ish market data fetcher (Twelve Data free tier).
Pulls candlestick series for EUR/USD and XAU/USD — real market data,
not generated.
"""
import os
import requests
import pandas as pd

API_KEY = os.getenv("TWELVE_DATA_KEY")
BASE_URL = "https://api.twelvedata.com/time_series"


def get_candles(symbol: str, interval: str = "15min", outputsize: int = 100) -> pd.DataFrame:
    resp = requests.get(BASE_URL, params={
        "symbol": symbol, "interval": interval, "outputsize": outputsize, "apikey": API_KEY,
    }, timeout=10)
    data = resp.json()
    if "values" not in data:
        raise RuntimeError(f"Twelve Data error for {symbol}: {data}")
    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)
    return df.sort_values("datetime").reset_index(drop=True)