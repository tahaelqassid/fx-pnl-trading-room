"""
Generates a realistic multi-day history by replaying the case-study
trades against slightly varied closing rates each day. This is
bootstrap data for the risk model's volatility estimate -- standard
practice for any new system that needs operating history before it
has real history. Clearly separated from real ingestion (load_csv.py)
so it's never mistaken for real trade data.
"""
import os
import random
from datetime import date, timedelta
from dotenv import load_dotenv
from pathlib import Path
import psycopg2

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")
random.seed(42)  # reproducible -- same run always produces the same "history"

conn = psycopg2.connect(
    host=os.getenv("DBT_HOST", "127.0.0.1"),
    port=int(os.getenv("DBT_PORT", "5432")),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)
cur = conn.cursor()

BASE_RATES = {"USD/MAD": 9.9500, "EUR/MAD": 10.8000, "EUR/USD": 1.0854}
NUM_DAYS = 15


def simulate_day(day_offset: int):
    d = date(2026, 9, 7) + timedelta(days=day_offset)
    # small realistic daily moves, +/- ~0.3%
    rates_today = {pair: round(rate * (1 + random.uniform(-0.003, 0.003)), 6)
                   for pair, rate in BASE_RATES.items()}

    for pair, rate in rates_today.items():
        cur.execute(
            """
            INSERT INTO market_rate (currency_pair, rate_date, closing_rate, source)
            VALUES (%s, %s, %s, 'simulated_history')
            ON CONFLICT (currency_pair, rate_date) DO UPDATE SET closing_rate = EXCLUDED.closing_rate
            """,
            (pair, d, rate),
        )

    cur.execute("SELECT id, default_method FROM book")
    for book_id, method in cur.fetchall():
        cur.execute(
            "SELECT currency_pair, direction, nominal, rate FROM trade WHERE book_id = %s AND confidence != 'simulated'",
            (book_id,),
        )
        trades = cur.fetchall()
        total_mtm = 0.0
        for pair, direction, nominal, traded_rate in trades:
            close = rates_today.get(pair, BASE_RATES.get(pair))
            if pair == "EUR/USD":
                close = rates_today["EUR/MAD"]
                traded_mad = float(traded_rate) * rates_today["USD/MAD"]
            else:
                traded_mad = float(traded_rate)
            diff = (close - traded_mad) if direction == "BUY" else (traded_mad - close)
            total_mtm += diff * float(nominal)

        realized = 0.0  # same trades every day here -- no new realizations in this simulation
        unrealized = round(total_mtm - realized, 2)
        cur.execute(
            """
            INSERT INTO daily_pnl (book_id, pnl_date, realized_mad, unrealized_mad, total_mad, method_used)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (book_id, pnl_date) DO UPDATE
            SET realized_mad = EXCLUDED.realized_mad, unrealized_mad = EXCLUDED.unrealized_mad,
                total_mad = EXCLUDED.total_mad
            """,
            (book_id, d, realized, unrealized, round(realized + unrealized, 2), method),
        )


if __name__ == "__main__":
    for i in range(1, NUM_DAYS + 1):
        simulate_day(i)
    conn.commit()
    cur.close()
    conn.close()
    print(f"Generated {NUM_DAYS} days of synthetic history.")