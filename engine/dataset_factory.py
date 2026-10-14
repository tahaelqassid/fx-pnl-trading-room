"""
Dataset Factory & Ingestion Pipeline for FX Trading Room.
Provides:
1. 'reference_case_study': The official 4-trade textbook dataset from PFE PDF.
2. 'production_kaggle_extended': A high-volume, 30-day realistic trading room dataset
   spanning 4 trading desks, 180+ trades, realistic Bank Al-Maghrib rates,
   and corresponding Back-Office settlement records.
"""
from datetime import datetime, date, timedelta
import random
from typing import List, Dict, Any
import pandas as pd
from engine.db_adapter import get_connection, execute_write, read_df, init_database


def load_reference_case_study():
    """
    Loads the exact 4-trade dataset from Section 2.2 of the PFE specification:
    Trade 1: USD/MAD BUY 1,000,000 @ 9.9200
    Trade 2: USD/MAD SELL 500,000 @ 9.9600
    Trade 3: EUR/MAD BUY 800,000 @ 10.7700
    Trade 4: EUR/USD BUY 600,000 @ 1.0820
    Rates: USD/MAD 9.9500, EUR/MAD 10.8000, EUR/USD 1.0854
    """
    init_database()
    conn = get_connection()
    cur = conn.cursor()
    is_pg = hasattr(conn, "get_dsn_parameters")

    # Clear current tables safely
    cur.execute("DELETE FROM daily_pnl")
    cur.execute("DELETE FROM backoffice_settlement")
    cur.execute("DELETE FROM trade")
    cur.execute("DELETE FROM market_rate")
    cur.execute("DELETE FROM book")
    conn.commit()

    # 1. Books
    books = [
        ("USD_DESK", "trader_taha", "MAD", "FIFO", 50000.0),
        ("EUR_DESK", "trader_sarah", "MAD", "FIFO", 60000.0),
    ]
    for b in books:
        if is_pg:
            cur.execute(
                "INSERT INTO book (name, trader_id, accounting_currency, default_method, stop_loss_threshold_mad) "
                "VALUES (%s, %s, %s, %s, %s) ON CONFLICT (name) DO NOTHING", b
            )
        else:
            cur.execute(
                "INSERT INTO book (name, trader_id, accounting_currency, default_method, stop_loss_threshold_mad) "
                "VALUES (?, ?, ?, ?, ?)", b
            )
    conn.commit()

    # Get book IDs
    cur.execute("SELECT id, name FROM book")
    book_map = {name: b_id for b_id, name in cur.fetchall()}

    # 2. Market Rates
    ref_date = date(2026, 9, 7)
    rates = [
        ("USD/MAD", ref_date, 9.9500, "Bank Al-Maghrib (BAM Fixing)"),
        ("EUR/MAD", ref_date, 10.8000, "Bank Al-Maghrib (BAM Fixing)"),
        ("EUR/USD", ref_date, 1.0854, "Reuters EOD"),
    ]
    for r in rates:
        if is_pg:
            cur.execute(
                "INSERT INTO market_rate (currency_pair, rate_date, closing_rate, source) "
                "VALUES (%s, %s, %s, %s) ON CONFLICT (currency_pair, rate_date) DO UPDATE SET closing_rate=EXCLUDED.closing_rate", r
            )
        else:
            cur.execute(
                "INSERT OR REPLACE INTO market_rate (currency_pair, rate_date, closing_rate, source) "
                "VALUES (?, ?, ?, ?)", r
            )
    conn.commit()

    # 3. Trades
    trades = [
        (book_map["USD_DESK"], "USD/MAD", "BUY", 1000000.0, 9.9200, datetime(2026, 9, 7, 9, 0), "confirmed", "T001"),
        (book_map["USD_DESK"], "USD/MAD", "SELL", 500000.0, 9.9600, datetime(2026, 9, 7, 10, 0), "confirmed", "T002"),
        (book_map["EUR_DESK"], "EUR/MAD", "BUY", 800000.0, 10.7700, datetime(2026, 9, 7, 11, 0), "confirmed", "T003"),
        (book_map["EUR_DESK"], "EUR/USD", "BUY", 600000.0, 1.0820, datetime(2026, 9, 7, 12, 0), "confirmed", "T004"),
    ]
    for t in trades:
        if is_pg:
            cur.execute(
                "INSERT INTO trade (book_id, currency_pair, direction, nominal, rate, trade_ts, confidence, source_ref) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (source_ref) DO NOTHING", t
            )
        else:
            cur.execute(
                "INSERT OR REPLACE INTO trade (book_id, currency_pair, direction, nominal, rate, trade_ts, confidence, source_ref) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", t
            )
    conn.commit()

    # 4. Back-Office Settlement Records for Reconciliation
    bo_settlements = [
        ("T001", "USD/MAD", "BUY", 1000000.0, 9.9200, ref_date, "Attijariwafa Bank", "SETTLED"),
        ("T002", "USD/MAD", "SELL", 500000.0, 9.9600, ref_date, "Banque Populaire (BCP)", "SETTLED"),
        ("T003", "EUR/MAD", "BUY", 800000.0, 10.7700, ref_date, "Bank of Africa (BMCE)", "SETTLED"),
        ("T004", "EUR/USD", "BUY", 600000.0, 1.0820, ref_date, "BNP Paribas FX", "SETTLED"),
    ]
    for bo in bo_settlements:
        if is_pg:
            cur.execute(
                "INSERT INTO backoffice_settlement (trade_ref, currency_pair, direction, settled_nominal, settled_rate, settlement_date, counterparty, status) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (trade_ref) DO NOTHING", bo
            )
        else:
            cur.execute(
                "INSERT OR REPLACE INTO backoffice_settlement (trade_ref, currency_pair, direction, settled_nominal, settled_rate, settlement_date, counterparty, status) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", bo
            )
    conn.commit()

    # 5. Populate Reference Daily P&L
    daily_pnl = [
        (book_map["USD_DESK"], ref_date, 20000.0, 15000.0, 35000.0, "FIFO"),
        (book_map["EUR_DESK"], ref_date, 0.0, 44460.0, 44460.0, "FIFO"),
    ]
    for p in daily_pnl:
        if is_pg:
            cur.execute(
                "INSERT INTO daily_pnl (book_id, pnl_date, realized_mad, unrealized_mad, total_mad, method_used) "
                "VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (book_id, pnl_date) DO UPDATE SET total_mad=EXCLUDED.total_mad", p
            )
        else:
            cur.execute(
                "INSERT OR REPLACE INTO daily_pnl (book_id, pnl_date, realized_mad, unrealized_mad, total_mad, method_used) "
                "VALUES (?, ?, ?, ?, ?, ?)", p
            )
    conn.commit()

    cur.close()
    conn.close()
    print("Loaded 4-Trade Reference Case Study.")


def load_production_kaggle_dataset():
    """
    Generates a realistic 30-day Trading Room dataset:
    - 4 Desks: USD_DESK, EUR_DESK, CROSS_DESK, CORP_SALES
    - 180+ authentic trades with varying lot sizes, directions, and prices
    - Historical daily Bank Al-Maghrib rates
    - Full multi-day equity curves and risk histories
    - Back-Office records with realistic settlement status and audit reconciliation items
    """
    init_database()
    conn = get_connection()
    cur = conn.cursor()
    is_pg = hasattr(conn, "get_dsn_parameters")

    # Clear current tables
    cur.execute("DELETE FROM daily_pnl")
    cur.execute("DELETE FROM backoffice_settlement")
    cur.execute("DELETE FROM trade")
    cur.execute("DELETE FROM market_rate")
    cur.execute("DELETE FROM book")
    conn.commit()

    # Seed for reproducibility
    random.seed(42)

    # 1. Books
    books = [
        ("USD_DESK", "trader_taha", "MAD", "FIFO", 75000.0),
        ("EUR_DESK", "trader_sarah", "MAD", "FIFO", 90000.0),
        ("CROSS_DESK", "trader_mehdi", "MAD", "FIFO", 65000.0),
        ("CORP_SALES", "trader_khalid", "MAD", "WAC", 120000.0),
    ]
    for b in books:
        if is_pg:
            cur.execute(
                "INSERT INTO book (name, trader_id, accounting_currency, default_method, stop_loss_threshold_mad) "
                "VALUES (%s, %s, %s, %s, %s) ON CONFLICT (name) DO NOTHING", b
            )
        else:
            cur.execute(
                "INSERT INTO book (name, trader_id, accounting_currency, default_method, stop_loss_threshold_mad) "
                "VALUES (?, ?, ?, ?, ?)", b
            )
    conn.commit()

    cur.execute("SELECT id, name FROM book")
    book_map = {name: b_id for b_id, name in cur.fetchall()}

    # 2. Historical Market Rates (30 business days)
    start_date = date.today() - timedelta(days=40)
    current_date = start_date
    business_days = []
    while len(business_days) < 30:
        if current_date.weekday() < 5:  # Mon-Fri
            business_days.append(current_date)
        current_date += timedelta(days=1)

    usd_mad = 9.8800
    eur_mad = 10.7200
    gbp_mad = 12.5500
    rates_history = []

    for d in business_days:
        # Realistic daily random walk
        usd_mad += random.uniform(-0.025, 0.026)
        eur_mad += random.uniform(-0.028, 0.029)
        gbp_mad += random.uniform(-0.035, 0.035)
        eur_usd = eur_mad / usd_mad

        rates_history.append((d, round(usd_mad, 4), round(eur_mad, 4), round(eur_usd, 4), round(gbp_mad, 4)))

        # Insert rates
        for pair, val in [("USD/MAD", usd_mad), ("EUR/MAD", eur_mad), ("EUR/USD", eur_usd), ("GBP/MAD", gbp_mad)]:
            source = "Bank Al-Maghrib (BAM Fixing)" if pair.endswith("/MAD") else "Reuters EOD"
            if is_pg:
                cur.execute(
                    "INSERT INTO market_rate (currency_pair, rate_date, closing_rate, source) "
                    "VALUES (%s, %s, %s, %s) ON CONFLICT (currency_pair, rate_date) DO UPDATE SET closing_rate=EXCLUDED.closing_rate",
                    (pair, d, round(val, 6), source)
                )
            else:
                cur.execute(
                    "INSERT OR REPLACE INTO market_rate (currency_pair, rate_date, closing_rate, source) "
                    "VALUES (?, ?, ?, ?)",
                    (pair, d, round(val, 6), source)
                )
    conn.commit()

    # 3. Generate Trades across the 30 days
    counterparties = [
        "Attijariwafa Bank", "Banque Populaire (BCP)", "Bank of Africa (BMCE)", 
        "Société Générale Maroc", "CIH Bank", "BNP Paribas FX", "Citigroup London"
    ]
    trade_counter = 1
    trades_list = []
    bo_settlements = []

    for day_idx, (d, u_rate, e_rate, eu_rate, g_rate) in enumerate(rates_history):
        # 4 to 8 trades per day
        num_trades = random.randint(4, 7)
        for _ in range(num_trades):
            desk = random.choices(["USD_DESK", "EUR_DESK", "CROSS_DESK", "CORP_SALES"], weights=[35, 30, 20, 15])[0]
            b_id = book_map[desk]
            
            if desk == "USD_DESK":
                pair = "USD/MAD"
                base_p = u_rate
            elif desk == "EUR_DESK":
                pair = "EUR/MAD"
                base_p = e_rate
            elif desk == "CROSS_DESK":
                pair = random.choice(["EUR/USD", "EUR/MAD"])
                base_p = eu_rate if pair == "EUR/USD" else e_rate
            else: # CORP_SALES
                pair = random.choice(["USD/MAD", "EUR/MAD", "GBP/MAD"])
                base_p = u_rate if pair == "USD/MAD" else (e_rate if pair == "EUR/MAD" else g_rate)

            direction = random.choice(["BUY", "SELL"])
            nominal = float(random.choice([100_000, 250_000, 500_000, 750_000, 1_000_000, 1_500_000]))
            spread = random.uniform(-0.0035, 0.0035)
            traded_rate = round(base_p * (1.0 + spread), 6)
            
            hour = random.randint(9, 16)
            minute = random.randint(0, 59)
            trade_ts = datetime(d.year, d.month, d.day, hour, minute)
            ref = f"TRD_{trade_counter:04d}"
            trade_counter += 1
            confidence = "confirmed"

            trades_list.append((b_id, pair, direction, nominal, traded_rate, trade_ts, confidence, ref))

            # Back-Office Settlement Record
            cp = random.choice(counterparties)
            # Inject realistic settlement conditions:
            # 94% exact matches, 4% tiny rate slippage (1 pip), 2% unconfirmed
            rand_flag = random.random()
            if rand_flag < 0.94:
                bo_rate = traded_rate
                bo_nom = nominal
                status = "SETTLED"
            elif rand_flag < 0.98:
                bo_rate = round(traded_rate + random.choice([-0.0003, 0.0003]), 6)
                bo_nom = nominal
                status = "SETTLED"
            else:
                # Omit to simulate unconfirmed trade
                continue

            bo_settlements.append((ref, pair, direction, bo_nom, bo_rate, d + timedelta(days=2), cp, status))

    # Insert trades
    for t in trades_list:
        if is_pg:
            cur.execute(
                "INSERT INTO trade (book_id, currency_pair, direction, nominal, rate, trade_ts, confidence, source_ref) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (source_ref) DO NOTHING", t
            )
        else:
            cur.execute(
                "INSERT INTO trade (book_id, currency_pair, direction, nominal, rate, trade_ts, confidence, source_ref) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", t
            )
    conn.commit()

    # Insert BO settlements
    for bo in bo_settlements:
        if is_pg:
            cur.execute(
                "INSERT INTO backoffice_settlement (trade_ref, currency_pair, direction, settled_nominal, settled_rate, settlement_date, counterparty, status) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (trade_ref) DO NOTHING", bo
            )
        else:
            cur.execute(
                "INSERT INTO backoffice_settlement (trade_ref, currency_pair, direction, settled_nominal, settled_rate, settlement_date, counterparty, status) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", bo
            )
    conn.commit()

    # 4. Compute Daily P&L for each day and store
    from engine.pnl_engine import compute_book_analytics, Trade as EngineTrade, Direction as EngineDir

    cur.execute("SELECT id, name, default_method FROM book")
    book_info = cur.fetchall()

    for d, u_rate, e_rate, eu_rate, g_rate in rates_history:
        rates_on_day = {
            "USD/MAD": u_rate,
            "EUR/MAD": e_rate,
            "EUR/USD": eu_rate,
            "GBP/MAD": g_rate,
        }
        for b_id, b_name, method in book_info:
            # Query trades up to date d
            cur.execute(
                "SELECT source_ref, trade_ts, currency_pair, direction, nominal, rate, confidence "
                "FROM trade WHERE book_id = ? AND date(trade_ts) <= ? ORDER BY trade_ts",
                (b_id, d.strftime("%Y-%m-%d"))
            )
            raw_t = cur.fetchall()
            if not raw_t:
                continue

            eng_trades = [
                EngineTrade(
                    trade_id=r[0],
                    timestamp=pd.to_datetime(r[1]),
                    currency_pair=r[2],
                    direction=EngineDir(r[3]),
                    nominal=float(r[4]),
                    rate=float(r[5]),
                    confidence=r[6]
                )
                for r in raw_t
            ]

            analytics = compute_book_analytics(eng_trades, rates_on_day, method=method)
            tot_real = analytics["total_realized_mad"]
            tot_unreal = analytics["total_unrealized_mad"]
            tot_mtm = analytics["total_mtm_mad"]

            if is_pg:
                cur.execute(
                    """
                    INSERT INTO daily_pnl (book_id, pnl_date, realized_mad, unrealized_mad, total_mad, method_used)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (book_id, pnl_date) DO UPDATE
                    SET realized_mad=EXCLUDED.realized_mad, unrealized_mad=EXCLUDED.unrealized_mad,
                        total_mad=EXCLUDED.total_mad, method_used=EXCLUDED.method_used
                    """,
                    (b_id, d, tot_real, tot_unreal, tot_mtm, method)
                )
            else:
                cur.execute(
                    """
                    INSERT OR REPLACE INTO daily_pnl (book_id, pnl_date, realized_mad, unrealized_mad, total_mad, method_used)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (b_id, d, tot_real, tot_unreal, tot_mtm, method)
                )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Loaded Production Kaggle-scale Dataset: {len(trades_list)} trades across 30 days.")


if __name__ == "__main__":
    load_reference_case_study()
