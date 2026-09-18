"""
Generates a new trade every few seconds and inserts it live, reusing
the same insert pattern as load_csv.py. Confidence is tagged
'simulated' so it's always distinguishable from real ingested trades.
"""
import os
import random
import time
import uuid
from datetime import datetime
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

BASE_RATES = {"USD/MAD": 9.9500, "EUR/MAD": 10.8000, "EUR/USD": 1.0854}

cur.execute("SELECT id, name FROM book")
BOOKS = cur.fetchall()


def random_trade():
    book_id, book_name = random.choice(BOOKS)
    pair = "EUR/USD" if "EUR" in book_name else "USD/MAD"
    direction = random.choice(["BUY", "SELL"])
    nominal = random.choice([50_000, 100_000, 250_000])
    rate = round(BASE_RATES[pair] * (1 + random.uniform(-0.001, 0.001)), 6)
    ref = f"LIVE_{uuid.uuid4().hex[:10]}"

    cur.execute(
        """
        INSERT INTO trade (book_id, currency_pair, direction, nominal, rate, trade_ts, confidence, source_ref)
        VALUES (%s, %s, %s, %s, %s, %s, 'simulated', %s)
        """,
        (book_id, pair, direction, nominal, rate, datetime.now(), ref),
    )
    conn.commit()
    print(f"{datetime.now().strftime('%H:%M:%S')}  {book_name}  {direction} {nominal} {pair} @ {rate}")


if __name__ == "__main__":
    print("Simulating live trades — Ctrl+C to stop")
    try:
        while True:
            random_trade()
            time.sleep(random.uniform(2, 6))
    except KeyboardInterrupt:
        print("\nStopped.")
        cur.close()
        conn.close()