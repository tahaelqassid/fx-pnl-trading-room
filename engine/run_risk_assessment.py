"""
Reads each book's real daily_pnl history from Postgres, computes
volatility from it, and assesses today's breach probability against
the book's real stop-loss threshold.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

from engine.risk_model import assess_book

conn = psycopg2.connect(
    host=os.getenv("DBT_HOST", "127.0.0.1"),
    port=int(os.getenv("DBT_PORT", "5432")),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)
cur = conn.cursor()


def get_history(book_id: int) -> list[float]:
    cur.execute(
        "SELECT unrealized_mad FROM daily_pnl WHERE book_id = %s ORDER BY pnl_date",
        (book_id,),
    )
    return [float(r[0]) for r in cur.fetchall()]


def get_book(book_id: int):
    cur.execute("SELECT stop_loss_threshold_mad FROM book WHERE id = %s", (book_id,))
    return float(cur.fetchone()[0])


if __name__ == "__main__":
    cur.execute("SELECT id, name FROM book")
    books = cur.fetchall()

    for book_id, name in books:
        history = get_history(book_id)
        if len(history) < 2:
            print(f"{name}: not enough history yet")
            continue

        threshold = get_book(book_id)
        current_unrealized = history[-1]
        result = assess_book(book_id, current_unrealized, threshold, history)

        print(f"{name}: unrealized={result.current_unrealized_mad}, "
              f"volatility={round(result.estimated_daily_volatility_mad, 2)}, "
              f"breach_probability={result.breach_probability}")

    cur.close()
    conn.close()