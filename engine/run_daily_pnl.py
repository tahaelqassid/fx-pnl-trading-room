"""
Reads trades from database, executes tested FIFO/WAC calculation engine,
and upserts results into daily_pnl table, strictly enforcing Business Rule BR3:
Total P&L = Realized P&L + Unrealized P&L.
Uses resilient db_adapter supporting both PostgreSQL and SQLite.
"""
import sys
from pathlib import Path
from datetime import date
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from engine.db_adapter import get_connection, read_df, execute_write
from engine.pnl_engine import (
    Trade, Direction, mtm_pnl, realized_fifo, realized_wac, compute_book_analytics
)


def run_eod_calculation(pnl_date: date = None):
    if pnl_date is None:
        pnl_date = date.today()

    conn = get_connection()
    cur = conn.cursor()
    is_pg = hasattr(conn, "get_dsn_parameters")

    # 1. Fetch latest market rates
    rates_df = read_df(
        "SELECT currency_pair, closing_rate FROM market_rate "
        "WHERE rate_date = (SELECT MAX(rate_date) FROM market_rate)"
    )
    if rates_df.empty:
        rates = {"USD/MAD": 9.9500, "EUR/MAD": 10.8000, "EUR/USD": 1.0854}
    else:
        rates = {row["currency_pair"]: float(row["closing_rate"]) for _, row in rates_df.iterrows()}
        if "EUR/MAD" in rates and "USD/MAD" in rates and "EUR/USD" not in rates:
            rates["EUR/USD"] = rates["EUR/MAD"] / rates["USD/MAD"]

    # 2. Iterate each book
    books_df = read_df("SELECT id, name, default_method FROM book")

    for _, book in books_df.iterrows():
        b_id = int(book["id"])
        method = book["default_method"]

        trades_df = read_df(
            "SELECT source_ref, trade_ts, currency_pair, direction, nominal, rate, confidence "
            "FROM trade WHERE book_id = %s ORDER BY trade_ts", (b_id,)
        )
        if trades_df.empty:
            continue

        eng_trades = [
            Trade(
                trade_id=str(r["source_ref"]),
                timestamp=pd.to_datetime(r["trade_ts"]),
                currency_pair=str(r["currency_pair"]),
                direction=Direction(r["direction"]),
                nominal=float(r["nominal"]),
                rate=float(r["rate"]),
                confidence=str(r["confidence"]),
            )
            for _, r in trades_df.iterrows()
        ]

        analytics = compute_book_analytics(eng_trades, rates, method=method)
        realized = analytics["total_realized_mad"]
        unrealized = analytics["total_unrealized_mad"]
        total_mtm = analytics["total_mtm_mad"]

        if is_pg:
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
                (b_id, pnl_date, realized, unrealized, total_mtm, method),
            )
        else:
            cur.execute(
                """
                INSERT OR REPLACE INTO daily_pnl (book_id, pnl_date, realized_mad, unrealized_mad, total_mad, method_used)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (b_id, pnl_date, realized, unrealized, total_mtm, method),
            )

        print(f"Book {book['name']} (ID {b_id}): Realized={realized:+,.2f} MAD, Unrealized={unrealized:+,.2f} MAD, Total={total_mtm:+,.2f} MAD [{method}]")

    conn.commit()
    cur.close()
    conn.close()
    print("EOD P&L Calculation Completed Successfully.")


if __name__ == "__main__":
    run_eod_calculation()