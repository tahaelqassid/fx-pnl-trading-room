"""
Loads books, trades, and market rates from CSV into Postgres.
Deliberately dumb: no calculation happens here. Ingestion only records
what happened — the engine (separately) decides what it means.
"""
import csv
import os
import psycopg2
from dotenv import load_dotenv

from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

conn = psycopg2.connect(
    host=os.getenv("DBT_HOST", "127.0.0.1"),
    port=int(os.getenv("DBT_PORT", "5432")),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)
cur = conn.cursor()


def load_books(path: str):
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            cur.execute(
                """
                INSERT INTO book (name, trader_id, accounting_currency, default_method)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (name) DO NOTHING
                """,
                (row["name"], row["trader_id"], row["accounting_currency"], row["default_method"]),
            )
    print(f"Loaded books from {path}")


def load_trades(path: str):
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            cur.execute("SELECT id FROM book WHERE name = %s", (row["book_name"],))
            book_id = cur.fetchone()
            if book_id is None:
                raise ValueError(f"Unknown book: {row['book_name']} — load books first")
            cur.execute(
                """
                INSERT INTO trade (book_id, currency_pair, direction, nominal, rate, trade_ts, confidence, source_ref)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (source_ref) DO NOTHING
                """,
                (book_id[0], row["currency_pair"], row["direction"],
                 row["nominal"], row["rate"], row["trade_ts"], row["confidence"], row["trade_ref"]),
            )
    print(f"Loaded trades from {path}")

def load_market_rates(path: str):
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            cur.execute(
                """
                INSERT INTO market_rate (currency_pair, rate_date, closing_rate, source)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (currency_pair, rate_date) DO UPDATE SET closing_rate = EXCLUDED.closing_rate
                """,
                (row["currency_pair"], row["rate_date"], row["closing_rate"], row["source"]),
            )
    print(f"Loaded market rates from {path}")


if __name__ == "__main__":
    load_books("data/books.csv")
    load_trades("data/trades.csv")
    load_market_rates("data/market_rates.csv")
    conn.commit()
    cur.close()
    conn.close()
    print("Done.")