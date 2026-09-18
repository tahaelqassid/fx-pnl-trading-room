"""
Pulls real, current FX rates from a live market data source (open.er-api.com,
no API key required) and writes them into market_rate — replacing synthetic
rates with the real thing for today's date.
"""
import os
import requests
from datetime import date
from pathlib import Path
from dotenv import load_dotenv
import psycopg2

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

conn = psycopg2.connect(
    host=os.getenv("DBT_HOST", "127.0.0.1"),
    port=int(os.getenv("DBT_PORT", "5432")),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)
cur = conn.cursor()


def fetch_real_rates() -> dict:
    resp = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if data.get("result") != "success":
        raise RuntimeError(f"Rate provider returned an error: {data}")

    usd_mad = data["rates"]["MAD"]       # MAD per 1 USD
    usd_eur = data["rates"]["EUR"]       # EUR per 1 USD
    eur_mad = usd_mad / usd_eur          # MAD per 1 EUR, derived honestly, not invented
    eur_usd = 1 / usd_eur                # USD per 1 EUR

    return {"USD/MAD": usd_mad, "EUR/MAD": eur_mad, "EUR/USD": eur_usd}


def store_rates(rates: dict, rate_date: date):
    for pair, rate in rates.items():
        cur.execute(
            """
            INSERT INTO market_rate (currency_pair, rate_date, closing_rate, source)
            VALUES (%s, %s, %s, 'open.er-api.com (real)')
            ON CONFLICT (currency_pair, rate_date) DO UPDATE
            SET closing_rate = EXCLUDED.closing_rate, source = EXCLUDED.source
            """,
            (pair, rate_date, round(rate, 6)),
        )
    conn.commit()


if __name__ == "__main__":
    rates = fetch_real_rates()
    store_rates(rates, date.today())
    for pair, rate in rates.items():
        print(f"{pair}: {rate:.4f}  (real market rate)")
    cur.close()
    conn.close()