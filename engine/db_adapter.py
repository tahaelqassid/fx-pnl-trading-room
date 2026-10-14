"""
Resilient Database Adapter for FX P&L Trading Room.
Supports PostgreSQL (production / Docker) with seamless fallback to SQLite
(presentation / standalone / zero-dependency mode).
Enforces exact schema equivalence, NUMERIC precision, and business constraints.
"""
import os
import sqlite3
from pathlib import Path
from typing import Optional, Tuple, Any
import pandas as pd
from dotenv import load_dotenv

# Load .env if present
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=ROOT_DIR / ".env")

SQLITE_DB_PATH = ROOT_DIR / "db" / "fx_trading_room.db"


def is_postgres_available() -> bool:
    """Check if PostgreSQL container or host is actively reachable."""
    try:
        import psycopg2
        host = os.getenv("DBT_HOST", "127.0.0.1")
        port = int(os.getenv("DBT_PORT", "5432"))
        db = os.getenv("POSTGRES_DB", "fx_pnl")
        user = os.getenv("POSTGRES_USER", "postgres")
        pwd = os.getenv("POSTGRES_PASSWORD", "postgres")
        conn = psycopg2.connect(
            host=host, port=port, dbname=db, user=user, password=pwd, connect_timeout=2
        )
        conn.close()
        return True
    except Exception:
        return False


def get_connection():
    """
    Returns an open database connection:
    - PostgreSQL connection if available
    - SQLite connection as resilient fallback
    """
    if is_postgres_available():
        import psycopg2
        return psycopg2.connect(
            host=os.getenv("DBT_HOST", "127.0.0.1"),
            port=int(os.getenv("DBT_PORT", "5432")),
            dbname=os.getenv("POSTGRES_DB", "fx_pnl"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        )
    else:
        SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(SQLITE_DB_PATH), check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn


def get_db_mode() -> str:
    """Returns 'PostgreSQL (Active)' or 'SQLite (Standalone Fallback)'."""
    return "PostgreSQL (Live Container)" if is_postgres_available() else "SQLite (High-Availability Standalone)"


def init_database(force_reinit: bool = False):
    """
    Initializes tables in the active database engine.
    Ensures identical schema across both PostgreSQL and SQLite.
    """
    conn = get_connection()
    cur = conn.cursor()

    is_pg = hasattr(conn, "get_dsn_parameters")

    if is_pg:
        # PostgreSQL schema is handled by schema.sql
        with open(ROOT_DIR / "db" / "schema.sql", "r") as f:
            sql_content = f.read()
        for stmt in sql_content.split(";"):
            clean_stmt = stmt.strip()
            if clean_stmt:
                try:
                    cur.execute(clean_stmt)
                    conn.commit()
                except Exception:
                    conn.rollback()
    else:
        # SQLite equivalent schema
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS book (
            id                    INTEGER PRIMARY KEY AUTOINCREMENT,
            name                  VARCHAR(50) NOT NULL UNIQUE,
            trader_id             VARCHAR(50) NOT NULL,
            accounting_currency   VARCHAR(3)  NOT NULL DEFAULT 'MAD',
            default_method        VARCHAR(4)  NOT NULL CHECK (default_method IN ('FIFO','WAC')),
            stop_loss_threshold_mad NUMERIC(18,2) NOT NULL DEFAULT 50000
        );

        CREATE TABLE IF NOT EXISTS trade (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id        INTEGER NOT NULL REFERENCES book(id),
            currency_pair  VARCHAR(7) NOT NULL,
            direction      VARCHAR(4) NOT NULL CHECK (direction IN ('BUY','SELL')),
            nominal        NUMERIC(18,2) NOT NULL CHECK (nominal > 0),
            rate           NUMERIC(18,6) NOT NULL CHECK (rate > 0),
            trade_ts       TIMESTAMP NOT NULL,
            confidence     VARCHAR(10) NOT NULL DEFAULT 'confirmed'
                           CHECK (confidence IN ('manual','confirmed','simulated')),
            source_ref     VARCHAR(150) NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS market_rate (
            currency_pair  VARCHAR(7) NOT NULL,
            rate_date      DATE NOT NULL,
            closing_rate   NUMERIC(18,6) NOT NULL CHECK (closing_rate > 0),
            source         VARCHAR(50) NOT NULL,
            PRIMARY KEY (currency_pair, rate_date)
        );

        CREATE TABLE IF NOT EXISTS daily_pnl (
            book_id         INTEGER NOT NULL REFERENCES book(id),
            pnl_date        DATE NOT NULL,
            realized_mad    NUMERIC(18,2) NOT NULL,
            unrealized_mad  NUMERIC(18,2) NOT NULL,
            total_mad       NUMERIC(18,2) NOT NULL,
            method_used     VARCHAR(4) NOT NULL CHECK (method_used IN ('FIFO','WAC')),
            PRIMARY KEY (book_id, pnl_date),
            CHECK (ROUND(total_mad, 2) = ROUND(realized_mad + unrealized_mad, 2))
        );

        CREATE TABLE IF NOT EXISTS backoffice_settlement (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_ref      VARCHAR(150) NOT NULL UNIQUE,
            currency_pair  VARCHAR(7) NOT NULL,
            direction      VARCHAR(4) NOT NULL,
            settled_nominal NUMERIC(18,2) NOT NULL,
            settled_rate   NUMERIC(18,6) NOT NULL,
            settlement_date DATE NOT NULL,
            counterparty   VARCHAR(100) NOT NULL,
            status         VARCHAR(20) NOT NULL DEFAULT 'SETTLED'
        );
        """)
        conn.commit()

    cur.close()
    conn.close()


def read_df(sql: str, params: Optional[Tuple[Any, ...]] = None) -> pd.DataFrame:
    """Helper to query database into pandas DataFrame safely with query translation."""
    conn = get_connection()
    is_pg = hasattr(conn, "get_dsn_parameters")

    # Adapt query placeholder if SQLite
    formatted_sql = sql
    if not is_pg:
        formatted_sql = formatted_sql.replace("%s", "?")
        formatted_sql = formatted_sql.replace("CURRENT_DATE", "date('now')")
        formatted_sql = formatted_sql.replace("trade_ts::date", "date(trade_ts)")

    try:
        if params:
            df = pd.read_sql_query(formatted_sql, conn, params=params)
        else:
            df = pd.read_sql_query(formatted_sql, conn)
        return df
    finally:
        conn.close()


def execute_write(sql: str, params: Optional[Tuple[Any, ...]] = None):
    """Executes a single write query with parameter placeholder adaptation."""
    conn = get_connection()
    is_pg = hasattr(conn, "get_dsn_parameters")
    formatted_sql = sql
    if not is_pg:
        formatted_sql = formatted_sql.replace("%s", "?")
        formatted_sql = formatted_sql.replace("CURRENT_DATE", "date('now')")

    cur = conn.cursor()
    try:
        if params:
            cur.execute(formatted_sql, params)
        else:
            cur.execute(formatted_sql)
        conn.commit()
    finally:
        cur.close()
        conn.close()
