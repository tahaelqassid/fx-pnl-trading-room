"""
Reads trades from Postgres, runs them through the tested FIFO/WAC engine,
and writes the result into daily_pnl — the table with the
total = realized + unrealized constraint.
"""
import os
import psycopg2
from datetime import date
from dotenv import load_dotenv
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

from engine.pnl_engine import Trade, Direction, realized_fifo, realized_wac

conn = psycopg2.connect(
    host=os.getenv("DBT_HOST", "127.0.0.1"),
    port=int(os.getenv("DBT_PORT", "5432")),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)
cur = conn.cursor()


def fetch_trades_for_book(book_id: int):
    cur.execute(
        """
        SELECT id, currency_pair, direction, nominal, rate, trade_ts
        FROM trade WHERE book_id = %s ORDER BY trade_ts
        """,
        (book_id,),
    )
    return [
        Trade(str(r[0]), r[5], r[1], Direction(r[2]), float(r[3]), float(r[4]))
        for r in cur.fetchall()
    ]


def compute_and_store(book_id: int, method: str, pnl_date: date):
    trades = fetch_trades_for_book(book_id)
    buys = [t for t in trades if t.direction == Direction.BUY]
    sells = [t for t in trades if t.direction == Direction.SELL]

    total_realized = 0.0
    for sell in sells:
        if method == "FIFO":
            realized, _ = realized_fifo(buys, sell)
        else:
            realized, _, _ = realized_wac(buys, sell)
        total_realized += realized

    cur.execute("SELECT SUM(mtm_pnl_mad) FROM fact_trade_mtm WHERE book_id = %s", (book_id,))
    total_mtm = float(cur.fetchone()[0] or 0)
    unrealized = round(total_mtm - total_realized, 2)

    cur.execute(
        """
        INSERT INTO daily_pnl (book_id, pnl_date, realized_mad, unrealized_mad, total_mad, method_used)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (book_id, pnl_date) DO UPDATE
        SET realized_mad = EXCLUDED.realized_mad,
            unrealized_mad = EXCLUDED.unrealized_mad,
            total_mad = EXCLUDED.total_mad,
            method_used = EXCLUDED.method_used
        """,
        (book_id, pnl_date, round(total_realized, 2), unrealized,
         round(total_realized + unrealized, 2), method),
    )
    conn.commit()
    print(f"Book {book_id}: realized={total_realized}, unrealized={unrealized}")


if __name__ == "__main__":
    cur.execute("SELECT id, default_method FROM book")
    for book_id, method in cur.fetchall():
        compute_and_store(book_id, method, date(2026, 9, 7))
    cur.close()
    conn.close()