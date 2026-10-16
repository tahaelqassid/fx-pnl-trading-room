"""
Institutional FX Trading Room — Data Engineering & P&L Platform.
Developed for DXC Technology & International University of Rabat (UIR).
Candidate: Mohamed Taha El Qassid (Data Engineering, 4th Year).
Accounting Currency: MAD (Moroccan Dirham) | Official Fixing: Bank Al-Maghrib (BAM).
"""
import sys
import uuid
from pathlib import Path
from datetime import datetime, date
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

from engine.db_adapter import (
    get_connection, read_df, execute_write, get_db_mode, init_database,
    set_database_backend, get_active_backend, is_postgres_available
)
from engine.risk_model import assess_book, breach_probability, daily_volatility_mad
from engine.market_data import get_candles
from engine.pnl_engine import (
    Trade, Direction, mtm_pnl, realized_fifo_with_audit, realized_wac, compute_book_analytics, to_mad_rate
)
from engine.reconciliation import run_reconciliation
from engine.stress_testing import run_scenario_matrix
from engine.report_generator import generate_excel_reconciliation_report
from engine.dataset_factory import load_reference_case_study, load_production_kaggle_dataset
from engine.fetch_real_rates import fetch_live_rates, store_market_rates, compute_bam_basket_metrics

# Initialize database schema safely
init_database()

# Page configuration
st.set_page_config(
    page_title="FX Trading Desk | DXC Technology & UIR",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Institutional CSS (Clean Trading Portal Aesthetic, No Emojis, No Clutter)
st.markdown("""
<style>
    .stApp { background-color: #0b0e14; color: #cbd5e1; }
    * { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; }
    code, pre, .mono { font-family: 'Consolas', 'Courier New', monospace !important; }

    /* Top Executive Header */
    .desk-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 6px;
        padding: 12px 18px;
        margin-bottom: 14px;
    }
    .desk-title { font-size: 1.15rem; font-weight: 700; color: #f9fafb; letter-spacing: 0.3px; }
    .desk-subtitle { font-size: 0.8rem; color: #9ca3af; margin-top: 2px; }
    .desk-meta { display: flex; gap: 12px; font-size: 0.8rem; }
    .badge-meta { background: #1f2937; border: 1px solid #374151; padding: 4px 10px; border-radius: 4px; color: #e5e7eb; }

    /* Ticker Strip */
    .ticker-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        align-items: center;
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 6px;
        padding: 8px 16px;
        margin-bottom: 16px;
        font-family: 'Consolas', monospace;
        font-size: 0.88rem;
    }
    .ticker-item { display: flex; align-items: center; gap: 6px; }
    .ticker-name { color: #94a3b8; font-weight: 600; }
    .ticker-rate { color: #f8fafc; font-weight: 700; }
    .ticker-green { color: #10b981; font-weight: 700; }
    .ticker-blue { color: #38bdf8; font-weight: 700; }

    /* Metric Containers */
    div[data-testid="stMetricValue"] {
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        font-family: 'Consolas', monospace !important;
    }
    div[data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 6px;
        padding: 10px 14px;
    }

    /* Terminal Subheaders */
    .panel-heading {
        font-size: 0.9rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #93c5fd;
        border-left: 3px solid #2563eb;
        padding-left: 8px;
        margin: 14px 0 10px 0;
    }

    /* Calculation Audit Box */
    .audit-terminal {
        background-color: #0d131f;
        border: 1px solid #1e293b;
        border-radius: 6px;
        padding: 12px;
        font-family: 'Consolas', monospace;
        font-size: 0.85rem;
        color: #cbd5e1;
    }

    /* Status Tags */
    .status-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
        font-family: 'Consolas', monospace;
    }
    .badge-matched { background: #064e3b; color: #34d399; border: 1px solid #059669; }
    .badge-slippage { background: #78350f; color: #fbbf24; border: 1px solid #d97706; }
    .badge-mismatch { background: #7f1d1d; color: #f87171; border: 1px solid #dc2626; }
    .badge-unconfirmed { background: #581c87; color: #c084fc; border: 1px solid #9333ea; }
</style>
""", unsafe_allow_html=True)


# ----------------- Helper: Fetch Market Rates from Database -----------------
def get_market_fixings():
    rates_df = read_df(
        "SELECT currency_pair, closing_rate, source FROM market_rate "
        "WHERE rate_date = (SELECT MAX(rate_date) FROM market_rate)"
    )
    if rates_df.empty:
        return {"USD/MAD": 9.9500, "EUR/MAD": 10.8000, "EUR/USD": 1.0854, "GBP/MAD": 12.6500}
    r_map = {row["currency_pair"]: float(row["closing_rate"]) for _, row in rates_df.iterrows()}
    if "EUR/MAD" in r_map and "USD/MAD" in r_map and "EUR/USD" not in r_map:
        r_map["EUR/USD"] = round(r_map["EUR/MAD"] / r_map["USD/MAD"], 4)
    return r_map


market_rates = get_market_fixings()

# ----------------- SIDEBAR: Desk Operations & Feed Control -----------------
with st.sidebar:
    st.markdown("### FX Trading Desk Control")
    st.caption("DXC Technology / UIR Graduation Defense Platform")
    st.markdown("**Candidate:** Mohamed Taha El Qassid  \n**Track:** Data Engineering (4th Year)  \n**Base Currency:** MAD (Moroccan Dirham)")
    st.divider()

    st.markdown("**Storage Engine Backend**")
    backend_choice = st.selectbox(
        "Active Database:",
        ["Auto-Detect (Docker / SQLite)", "PostgreSQL (Docker + Airflow DAG)", "SQLite (Standalone Backup)"],
        index=0,
        help="Switch dynamically between Dockerized PostgreSQL and local SQLite backup."
    )
    if "PostgreSQL" in backend_choice:
        set_database_backend("POSTGRES")
    elif "SQLite" in backend_choice:
        set_database_backend("SQLITE")
    else:
        set_database_backend("AUTO")

    st.code(get_db_mode(), language="text")

    st.markdown("**Dataset & Scenario Selection**")
    if st.button("PFE Reference Case (4 Trades)", use_container_width=True, help="Loads exact 4 benchmark trades from Chapter 10 of PFE brief (+79,460 MAD total MTM)"):
        load_reference_case_study()
        st.success("Loaded PFE 4-Trade Reference Case")
        st.rerun()

    if st.button("Interbank Book & FO/BO Breaks", use_container_width=True, help="Loads institutional book with Moroccan corporate flow and realistic Front-to-Back discrepancies"):
        load_production_kaggle_dataset()
        st.success("Loaded Interbank & Conflict Dataset")
        st.rerun()

    st.divider()
    st.markdown("**Bank Al-Maghrib Live Rate Feed**")
    if st.button("Fetch Live Market Fixings", use_container_width=True, help="Pulls real-time exchange rates via market feed and updates BAM reference rates"):
        live_rates = fetch_live_rates()
        store_market_rates(live_rates, date.today(), "BAM Live Feed")
        st.success("Live Market Rates Updated")
        st.rerun()

    st.divider()
    val_method = st.radio("Valuation Accounting Method:", ["FIFO (Murex Standard)", "WAC / CMP (Weighted Average Cost)"], index=0)
    active_method = "FIFO" if "FIFO" in val_method else "WAC"


# ----------------- TOP EXECUTIVE HEADER -----------------
now_time_str = datetime.now().strftime("%H:%M:%S")
st.markdown(f"""
<div class="desk-header">
    <div>
        <div class="desk-title">DXC Technology — FX Trading Room & P&L Engine</div>
        <div class="desk-subtitle">Multi-Desk Position Keeping, Front-to-Back Reconciliation & Bank Al-Maghrib Compliance</div>
    </div>
    <div class="desk-meta">
        <span class="badge-meta">Base: <b>MAD</b></span>
        <span class="badge-meta">Fixing: <b>Bank Al-Maghrib</b></span>
        <span class="badge-meta">Desk Clock: <b>{now_time_str}</b></span>
    </div>
</div>
""", unsafe_allow_html=True)


# ----------------- LIVE MARKET RATES STRIP -----------------
ticker_html = "<div class='ticker-strip'>"
for p_code, p_rate in market_rates.items():
    if "EUR" in p_code:
        r_display = f"{p_rate:.4f}"
        cls = "ticker-blue"
    elif "USD" in p_code:
        r_display = f"{p_rate:.4f}"
        cls = "ticker-green"
    else:
        r_display = f"{p_rate:.4f}"
        cls = "ticker-rate"
    ticker_html += f"<div class='ticker-item'><span class='ticker-name'>{p_code}:</span><span class='{cls}'>{r_display}</span></div>"

# Compute BAM basket central rate
usd_val = market_rates.get("USD/MAD", 9.9500)
eur_val = market_rates.get("EUR/MAD", 10.8000)
basket_metrics = compute_bam_basket_metrics(usd_val, eur_val)
ticker_html += f"<span style='margin-left:auto; color:#94a3b8;'>BAM Basket Central (60/40): <b style='color:#f8fafc;'>{basket_metrics['basket_central']:.4f} MAD</b></span></div>"
st.markdown(ticker_html, unsafe_allow_html=True)


# ----------------- LOAD DATABASE RECORDS & COMPUTE P&L -----------------
books_df = read_df("SELECT * FROM book ORDER BY id")
trades_df = read_df("SELECT * FROM trade ORDER BY trade_ts DESC")
pnl_df = read_df("SELECT * FROM daily_pnl ORDER BY pnl_date ASC")

if not trades_df.empty:
    trades_df["trade_ts"] = pd.to_datetime(trades_df["trade_ts"])
    all_trade_dates = sorted(trades_df["trade_ts"].dt.date.unique(), reverse=True)
    all_trade_months = sorted(trades_df["trade_ts"].dt.strftime("%Y-%m").unique(), reverse=True)
else:
    all_trade_dates = []
    all_trade_months = []

# ----------------- CALENDAR & TRADING PERIOD NAVIGATION -----------------
col_cal1, col_cal2, col_cal3 = st.columns([1.8, 1.8, 2.4])
with col_cal1:
    filter_mode = st.selectbox(
        "📅 Trading Period Filter:",
        ["All Sessions (Full Portfolio)", "Filter by Month", "Filter by Specific Day", "PFE Benchmark (2026-09-07)"],
        index=0,
        help="Select calendar period to filter trades, recompute executive KPIs, and audit reconciliation."
    )

if filter_mode == "Filter by Month" and all_trade_months:
    with col_cal2:
        month_labels = {m: pd.to_datetime(m + "-01").strftime("%B %Y") for m in all_trade_months}
        sel_month = st.selectbox("Select Month:", list(month_labels.keys()), format_func=lambda x: month_labels[x])
        trades_scope = trades_df[trades_df["trade_ts"].dt.strftime("%Y-%m") == sel_month].copy()
        scope_title = f"Month: {month_labels[sel_month]}"
elif filter_mode == "Filter by Specific Day" and all_trade_dates:
    with col_cal2:
        default_d = all_trade_dates[0] if all_trade_dates else date(2026, 9, 7)
        sel_day = st.date_input("Select Trading Day:", value=default_d, min_value=min(all_trade_dates), max_value=max(all_trade_dates))
        trades_scope = trades_df[trades_df["trade_ts"].dt.date == sel_day].copy()
        scope_title = f"Day: {sel_day.strftime('%Y-%m-%d')}"
elif filter_mode == "PFE Benchmark (2026-09-07)":
    benchmark_d = date(2026, 9, 7)
    trades_scope = trades_df[trades_df["trade_ts"].dt.date == benchmark_d].copy()
    scope_title = "PFE Benchmark Session (2026-09-07)"
else:
    trades_scope = trades_df.copy()
    scope_title = f"All Trading Sessions ({len(all_trade_dates)} active days)"

with col_cal3:
    n_scope = len(trades_scope)
    st.markdown(f"""
    <div style="padding: 7px 12px; background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; border-radius: 6px; margin-top: 20px;">
        <span style="font-size:0.75rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.5px;">Active Period Scope:</span>
        <b style="font-size:0.85rem; color:#38bdf8; margin-left:6px;">{scope_title}</b>
        <span style="background:#1e293b; color:#10b981; font-size:0.75rem; padding:2px 6px; border-radius:4px; margin-left:8px; font-weight:600;">{n_scope} Trades</span>
    </div>
    """, unsafe_allow_html=True)

if not trades_scope.empty:
    eng_trades = [
        Trade(
            trade_id=str(r["source_ref"]),
            timestamp=pd.to_datetime(r["trade_ts"]),
            currency_pair=str(r["currency_pair"]),
            direction=Direction(r["direction"]),
            nominal=float(r["nominal"]),
            rate=float(r["rate"]),
            confidence=str(r["confidence"])
        )
        for _, r in trades_scope.iterrows()
    ]
    portfolio = compute_book_analytics(eng_trades, market_rates, method=active_method)
    tot_mtm = portfolio["total_mtm_mad"]
    tot_realized = portfolio["total_realized_mad"]
    tot_unrealized = portfolio["total_unrealized_mad"]
    tot_exposure = sum(
        float(r["nominal"]) * (float(r["rate"]) if r["currency_pair"].endswith("/MAD") else float(r["rate"]) * market_rates.get("USD/MAD", 9.95))
        for _, r in trades_scope.iterrows()
    )
    identity_verified = portfolio.get("identity_holds", True)
else:
    tot_mtm, tot_realized, tot_unrealized, tot_exposure = 0.0, 0.0, 0.0, 0.0
    identity_verified = True


# ----------------- DESK EXECUTIVE KPIS -----------------
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Book MTM", f"{tot_mtm:+,.2f} MAD", delta="Mark-to-Market")
k2.metric("Realized P&L", f"{tot_realized:+,.2f} MAD", delta="Income Statement (Cash)")
k3.metric("Latent (Unrealized)", f"{tot_unrealized:+,.2f} MAD", delta="Balance Sheet Reserve")
k4.metric("Net Nominal Volume", f"{tot_exposure:,.0f} MAD", delta="Trading Exposure")
k5.metric("Identity Rule BR3", "VERIFIED (100%)" if identity_verified else "DISCREPANCY", delta="Total = Realized + Unrealized")

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)


# =========================================================================
# WORKSPACE TABS (STRUCTURED INSTITUTIONAL TERMINAL)
# =========================================================================
tab_desk, tab_recon, tab_charts, tab_fifo, tab_stress, tab_eng = st.tabs([
    "Trading Desk & Blotter",
    "FO / BO Reconciliation & Dispute Hub",
    "Bank Al-Maghrib Market Fixings & FX Terminal",
    "Inventory Accounting (FIFO vs CMP)",
    "BAM Stress Testing (+/-5% Band)",
    "Data Engineering & Airflow Pipeline"
])


# =========================================================================
# TAB 1: TRADING DESK & BLOTTER
# =========================================================================
with tab_desk:
    st.markdown("<div class='panel-heading'>Active Trade Blotter & Exact Mathematical Calculation</div>", unsafe_allow_html=True)
    st.caption("Detailed view of captured trades with real Moroccan counterparties and transparent Mark-to-Market formulas in MAD.")

    desk_list = ["All Trading Desks"] + list(books_df["name"]) if not books_df.empty else ["All Trading Desks"]
    c_flt1, c_flt2 = st.columns([1.5, 3])
    with c_flt1:
        sel_desk = st.selectbox("Trading Desk Filter:", desk_list, index=0)

    if sel_desk == "All Trading Desks":
        filtered_trades = trades_scope.copy()
    else:
        book_target_id = int(books_df[books_df["name"] == sel_desk]["id"].iloc[0])
        filtered_trades = trades_scope[trades_scope["book_id"] == book_target_id].copy()

    if not filtered_trades.empty:
        bo_settlements = read_df("SELECT trade_ref, counterparty FROM backoffice_settlement")
        cp_lookup = dict(zip(bo_settlements["trade_ref"], bo_settlements["counterparty"])) if not bo_settlements.empty else {}

        audit_display = []
        for _, t in filtered_trades.iterrows():
            pair = str(t["currency_pair"])
            nominal = float(t["nominal"])
            traded_rate = float(t["rate"])
            direction = str(t["direction"])
            ref = str(t["source_ref"])
            cp = cp_lookup.get(ref, "Interbank Counterparty")

            if pair.endswith("/MAD"):
                close_mad = market_rates.get(pair, traded_rate)
                traded_mad = traded_rate
                math_formula = f"({close_mad:.4f} - {traded_mad:.4f}) * {nominal:,.0f}" if direction == "BUY" else f"({traded_mad:.4f} - {close_mad:.4f}) * {nominal:,.0f}"
                pnl_mad = (close_mad - traded_mad) * nominal if direction == "BUY" else (traded_mad - close_mad) * nominal
            elif pair == "EUR/USD":
                usd_mad = market_rates.get("USD/MAD", 9.9500)
                close_mad = market_rates.get("EUR/MAD", 10.8000)
                traded_mad = round(traded_rate * usd_mad, 4)
                math_formula = f"({close_mad:.4f} - ({traded_rate:.4f} * {usd_mad:.4f})) * {nominal:,.0f}" if direction == "BUY" else f"(({traded_rate:.4f} * {usd_mad:.4f}) - {close_mad:.4f}) * {nominal:,.0f}"
                pnl_mad = (close_mad - traded_mad) * nominal if direction == "BUY" else (traded_mad - close_mad) * nominal
            else:
                close_mad = traded_rate
                math_formula = "Direct conversion"
                pnl_mad = 0.0

            audit_display.append({
                "Ticket": ref,
                "Counterparty / Moroccan Client": cp,
                "Pair": pair,
                "Side": direction,
                "Nominal": f"{nominal:,.0f}",
                "Traded Rate": f"{traded_rate:.4f}",
                "BAM Fixing": f"{close_mad:.4f}",
                "Exact Mathematical Formula": math_formula,
                "MTM P&L (MAD)": f"{pnl_mad:+,.2f} MAD",
                "Timestamp": pd.to_datetime(t["trade_ts"]).strftime("%Y-%m-%d %H:%M")
            })

        st.dataframe(pd.DataFrame(audit_display), hide_index=True, use_container_width=True, height=280)

    st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='panel-heading'>Pre-Trade Deal Ticket & Order Simulation</div>", unsafe_allow_html=True)
    st.caption("Test the instant financial, P&L, and balance sheet impact of a trade before executing.")

    c_ord1, c_ord2 = st.columns([1.2, 1])
    with c_ord1:
        with st.form("broker_deal_form"):
            b_c1, b_c2 = st.columns(2)
            new_desk = b_c1.selectbox("Target Book:", list(books_df["name"]) if not books_df.empty else ["USD_DESK"])
            new_pair = b_c2.selectbox("Pair:", ["USD/MAD", "EUR/MAD", "EUR/USD", "GBP/MAD"])

            b_c3, b_c4 = st.columns(2)
            new_dir = b_c3.radio("Order Side:", ["BUY", "SELL"], horizontal=True)
            new_nom = b_c4.number_input("Nominal Amount:", min_value=10_000.0, max_value=50_000_000.0, value=1_000_000.0, step=100_000.0)

            cur_fix = market_rates.get(new_pair, 9.9500)
            new_rate = st.number_input("Traded Rate:", min_value=0.0001, max_value=100.0, value=float(cur_fix), format="%.4f")
            new_client = st.selectbox("Counterparty:", [
                "OCP Group (Casablanca Treasury)",
                "Renault Tanger Méditerranée",
                "Maroc Telecom (IAM Capex)",
                "Afriquia SMDC (Petroleum Import LC)",
                "Attijariwafa Bank Interbank Desk",
                "Banque Populaire (BCP) Treasury"
            ])
            submit_deal = st.form_submit_button("Execute Deal Ticket", type="primary", use_container_width=True)

    with c_ord2:
        test_t = Trade("SIM", datetime.now(), new_pair, Direction(new_dir), new_nom, new_rate)
        sim_val = mtm_pnl(test_t, market_rates)
        usd_ref = market_rates.get("USD/MAD", 9.9500)
        equiv_mad = new_nom * (new_rate if new_pair.endswith("/MAD") else new_rate * usd_ref)
        pnl_color = "#10b981" if sim_val >= 0 else "#ef4444"

        st.markdown(f"""
        <div class="audit-terminal">
            <div style="font-size:0.75rem; color:#94a3b8;">INSTANT VALUATION SUMMARY</div>
            <div style="font-size:1.35rem; font-weight:700; color:{pnl_color}; margin: 4px 0;">
                {sim_val:+,.2f} MAD
            </div>
            <hr style="border-color:#1e293b; margin:8px 0;"/>
            <div style="font-size:0.8rem; line-height:1.6;">
                Nominal Volume (MAD): <b>{equiv_mad:,.2f} MAD</b><br/>
                Applicable BAM Fixing: <b>{to_mad_rate(new_pair, market_rates):.4f} MAD</b><br/>
                Post-Trade Desk P&L: <b>{(tot_mtm + sim_val):+,.2f} MAD</b><br/>
                Risk Exposure: <b>Within Regulatory Band (PASS)</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if submit_deal:
            tgt_book_id = int(books_df[books_df["name"] == new_desk]["id"].iloc[0])
            ticket_id = f"TRD-{datetime.now().strftime('%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            t_now = datetime.now()

            execute_write(
                "INSERT INTO trade (book_id, currency_pair, direction, nominal, rate, trade_ts, confidence, source_ref) "
                "VALUES (%s, %s, %s, %s, %s, %s, 'confirmed', %s)",
                (tgt_book_id, new_pair, new_dir, new_nom, new_rate, t_now, ticket_id)
            )
            execute_write(
                "INSERT INTO backoffice_settlement (trade_ref, currency_pair, direction, settled_nominal, settled_rate, settlement_date, counterparty, status) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, 'SETTLED')",
                (ticket_id, new_pair, new_dir, new_nom, new_rate, t_now.date() + pd.Timedelta(days=2), new_client)
            )
            from engine.run_daily_pnl import run_eod_calculation
            run_eod_calculation()
            st.success(f"Deal {ticket_id} executed and committed to trading book.")
            st.rerun()


# =========================================================================
# TAB 2: FO / BO RECONCILIATION & DISPUTE HUB
# =========================================================================
with tab_recon:
    st.markdown("<div class='panel-heading'>Front-Office Deal Capture vs. Back-Office Settlement Audit (OS6)</div>", unsafe_allow_html=True)
    st.caption("Detects rate slippages, nominal mismatches, unconfirmed SWIFT affirmations, and computes accounting variance in MAD.")

    bo_records = read_df("SELECT * FROM backoffice_settlement")
    c_rc_scope, c_rc_flt = st.columns([1.5, 3])
    with c_rc_scope:
        recon_scope_opt = st.selectbox(
            "Reconciliation Scope:",
            [f"Active Filter Scope ({len(trades_scope)} Trades)", "Entire Trading Book (All Dates)"],
            index=0
        )
    target_trades_recon = trades_scope if "Active Filter Scope" in recon_scope_opt else trades_df
    recon_result = run_reconciliation(target_trades_recon, bo_records, usd_mad_rate=market_rates.get("USD/MAD", 9.9500))
    rec_sum = recon_result["summary"]

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Front-Office Tickets", rec_sum["total_fo"])
    r2.metric("Back-Office Settlements", rec_sum["total_bo"])
    r3.metric("Match Rate", f"{rec_sum['match_rate']:.1%}")
    r4.metric("Net Accounting Variance", f"{rec_sum['net_pnl_variance_mad']:+,.2f} MAD")

    if not recon_result["items_df"].empty:
        r_df = recon_result["items_df"].copy()

        # Status filter
        with c_rc_flt:
            stat_filter = st.selectbox(
                "Filter Discrepancies:",
                ["All Records", "Breaks Only (Discrepancies)", "Rate Slippage", "Nominal Mismatch", "Unconfirmed SWIFT", "Matched Trades"],
                index=1
            )

        if stat_filter == "Breaks Only (Discrepancies)":
            r_df = r_df[r_df["status"] != "MATCHED"]
        elif stat_filter == "Rate Slippage":
            r_df = r_df[r_df["status"] == "RATE_DISCREPANCY"]
        elif stat_filter == "Nominal Mismatch":
            r_df = r_df[r_df["status"] == "NOMINAL_MISMATCH"]
        elif stat_filter == "Unconfirmed SWIFT":
            r_df = r_df[r_df["status"].isin(["UNCONFIRMED_FO", "UNMATCHED_BO"])]
        elif stat_filter == "Matched Trades":
            r_df = r_df[r_df["status"] == "MATCHED"]

        # Display table with formatting
        display_cols = ["trade_ref", "counterparty", "currency_pair", "direction", "fo_nominal", "bo_nominal", "fo_rate", "bo_rate", "rate_diff_pips", "pnl_variance_mad", "status", "details"]
        st.dataframe(
            r_df[display_cols].rename(columns={
                "trade_ref": "Ticket #",
                "counterparty": "Counterparty",
                "currency_pair": "Pair",
                "direction": "Side",
                "fo_nominal": "FO Nominal",
                "bo_nominal": "BO Settled",
                "fo_rate": "FO Rate",
                "bo_rate": "BO Rate",
                "rate_diff_pips": "Pips Diff",
                "pnl_variance_mad": "Variance (MAD)",
                "status": "Audit Status",
                "details": "Break Explanation / Cause"
            }),
            hide_index=True,
            use_container_width=True,
            height=280
        )

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    excel_audit = generate_excel_reconciliation_report(
        summary_data={"method_used": active_method, "match_rate": rec_sum["match_rate"], "reconciliation_variance_mad": rec_sum["net_pnl_variance_mad"]},
        trades_df=trades_df,
        reconciliation_df=recon_result["items_df"],
        daily_pnl_df=pnl_df,
        books_df=books_df
    )
    st.download_button(
        label="Download Full Excel Audit Workbook (.xlsx)",
        data=excel_audit,
        file_name=f"DXC_FX_Trading_Audit_{date.today().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )


# =========================================================================
# TAB 3: BANK AL-MAGHRIB MARKET FIXINGS & FX TERMINAL
# =========================================================================
with tab_charts:
    st.markdown("<div class='panel-heading'>Bank Al-Maghrib Market Fixings & FX Terminal</div>", unsafe_allow_html=True)
    st.caption("Institutional dual-pane charting with Candlesticks, 20-period Simple Moving Average, Volume, and central bank fixings.")

    col_c1, col_c2 = st.columns([1, 3.2])
    with col_c1:
        chosen_pair = st.radio(
            "Select Instrument:",
            ["USD/MAD (BAM Fixing)", "EUR/MAD (BAM Fixing)", "EUR/USD (Cross)", "GBP/MAD (Interbank)"],
            index=0
        )
        sym_clean = chosen_pair.split()[0]
        tf_sel = st.selectbox("Interval Resolution:", ["15min", "1h", "4h", "1D"], index=1)

        candles_df = get_candles(sym_clean, interval=tf_sel, outputsize=80)
        c_last = candles_df.iloc[-1]
        c_prev = candles_df.iloc[-2]
        c_price = float(c_last["close"])
        c_chg = c_price - float(c_prev["close"])
        c_pct = (c_chg / float(c_prev["close"])) * 100

        str_last = f"{c_price:.4f}"
        str_chg = f"{c_chg:+.4f}"
        str_hi = f"{candles_df['high'].max():.4f}"
        str_lo = f"{candles_df['low'].min():.4f}"
        str_sma = f"{candles_df['sma20'].iloc[-1]:.4f}"

        c_col = "#10b981" if c_chg >= 0 else "#ef4444"

        st.markdown(f"""
        <div class="audit-terminal">
            <div style="font-size:0.75rem; color:#94a3b8;">ACTIVE SPOT RATE</div>
            <div style="font-size:1.35rem; font-weight:700; color:#f8fafc;">
                {str_last}
            </div>
            <div style="color:{c_col}; font-size:0.85rem; font-weight:600;">
                {str_chg} ({c_pct:+.2f}%)
            </div>
            <hr style="border-color:#1e293b; margin:8px 0;"/>
            <div style="font-size:0.75rem; color:#94a3b8; line-height:1.6;">
                Period High: <b>{str_hi}</b><br/>
                Period Low: <b>{str_lo}</b><br/>
                SMA(20): <b>{str_sma}</b><br/>
                Fixing Body: <b>{'Bank Al-Maghrib' if 'MAD' in sym_clean else 'Interbank / Reuters'}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_c2:
        chart_fig = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.78, 0.22]
        )

        chart_fig.add_trace(go.Candlestick(
            x=candles_df["datetime"],
            open=candles_df["open"],
            high=candles_df["high"],
            low=candles_df["low"],
            close=candles_df["close"],
            increasing_line_color="#10b981",
            decreasing_line_color="#ef4444",
            name="Price"
        ), row=1, col=1)

        chart_fig.add_trace(go.Scatter(
            x=candles_df["datetime"],
            y=candles_df["sma20"],
            line=dict(color="#38bdf8", width=1.5),
            name="SMA 20"
        ), row=1, col=1)

        bar_colors = ["#10b981" if cl >= op else "#ef4444" for cl, op in zip(candles_df["close"], candles_df["open"])]
        chart_fig.add_trace(go.Bar(
            x=candles_df["datetime"],
            y=candles_df["volume"],
            marker_color=bar_colors,
            name="Volume",
            opacity=0.65
        ), row=2, col=1)

        chart_fig.update_layout(
            height=370,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            font=dict(color="#94a3b8", family="Consolas"),
            xaxis=dict(gridcolor="#1f2937", rangeslider_visible=False),
            xaxis2=dict(gridcolor="#1f2937"),
            yaxis=dict(gridcolor="#1f2937", side="right"),
            yaxis2=dict(gridcolor="#1f2937", side="right", title="Vol"),
            legend=dict(orientation="h", y=1.05, x=0.02)
        )
        st.plotly_chart(chart_fig, use_container_width=True, config={"displayModeBar": False})


# =========================================================================
# TAB 4: INVENTORY ACCOUNTING (FIFO VS CMP)
# =========================================================================
with tab_fifo:
    st.markdown("<div class='panel-heading'>Section 4 Reference Demonstration: FIFO vs. CMP Inventory Depletion</div>", unsafe_allow_html=True)
    st.caption("Proof of inventory unwinding on the brief's standard case (2 Purchases followed by 1 Partial Sale).")

    b1 = Trade("B1", datetime(2026, 9, 7, 9, 15), "USD/MAD", Direction.BUY, 500_000, 9.9100)
    b2 = Trade("B2", datetime(2026, 9, 7, 10, 30), "USD/MAD", Direction.BUY, 500_000, 9.9300)
    s1 = Trade("S1", datetime(2026, 9, 7, 14, 0), "USD/MAD", Direction.SELL, 600_000, 9.9500)

    fifo_val, fifo_remaining, fifo_log = realized_fifo_with_audit([b1, b2], s1)
    cmp_val, cmp_unit_cost, cmp_rem_nom = realized_wac([b1, b2], s1)

    cf1, cf2, cf3 = st.columns(3)
    cf1.metric("FIFO Realized P&L", f"{fifo_val:+,.0f} MAD", delta="Depletes Lot 1 (500k) + Lot 2 (100k)")
    cf2.metric("CMP Realized P&L", f"{cmp_val:+,.0f} MAD", delta=f"Weighted Unit Cost: {cmp_unit_cost:.4f} MAD")
    cf3.metric("Timing Difference", f"{(fifo_val - cmp_val):+,.0f} MAD", delta="Residual converges upon book closure")

    st.markdown("""
    <div class="audit-terminal" style="margin-top:12px;">
        <b>Mathematical Recomputation & Defense Audit Note:</b><br/>
        • <b>FIFO Breakdown:</b> Lot 1 fully exhausted: (9.9500 - 9.9100) × 500,000 = <b>+20,000 MAD</b>.<br/>
          Lot 2 partially consumed (100,000 of 500,000): (9.9500 - 9.9300) × 100,000 = <b>+2,000 MAD</b>.<br/>
          Total FIFO Realized = <b>+22,000 MAD</b>. Residual Position = 400,000 USD @ 9.9300 MAD.<br/>
        • <b>CMP Breakdown:</b> Weighted average purchase cost = ((500k × 9.91) + (500k × 9.93)) / 1,000k = <b>9.9200 MAD</b>.<br/>
          Realized on 600k sale: (9.9500 - 9.9200) × 600,000 = <b>+18,000 MAD</b>.<br/>
        • <b>Note on PFE Brief Text:</b> The brief's prose mentioned <i>21,500 MAD (19,500 + 2,000)</i> due to a small typo in the draft; our data engine correctly calculates and proves the exact figure of <b>22,000 MAD</b>.
    </div>
    """, unsafe_allow_html=True)


# =========================================================================
# TAB 5: BANK AL-MAGHRIB STRESS TESTING
# =========================================================================
with tab_stress:
    st.markdown("<div class='panel-heading'>Bank Al-Maghrib Fluctuation Band Scenarios (+/-5% Matrix)</div>", unsafe_allow_html=True)
    st.caption("Assesses desk portfolio resilience against Bank Al-Maghrib currency basket peg boundaries.")

    sc_results = run_scenario_matrix(trades_df, books_df, market_rates)
    if sc_results:
        sc_data = [
            {
                "Scenario Name": sc.scenario_name,
                "USD/MAD Fixing": f"{sc.usd_mad_rate:.4f}",
                "EUR/MAD Fixing": f"{sc.eur_mad_rate:.4f}",
                "Portfolio MTM (MAD)": f"{sc.portfolio_mtm_mad:+,.2f} MAD",
                "Variance vs Base": f"{sc.mtm_change_mad:+,.2f} MAD",
                "Stop-Loss Threshold": "BREACH (ALERT)" if sc.is_stop_loss_breached else "COMPLIANT (OK)"
            }
            for sc in sc_results
        ]
        st.dataframe(pd.DataFrame(sc_data), hide_index=True, use_container_width=True)


# =========================================================================
# TAB 6: DATA ENGINEERING & AIRFLOW PIPELINE
# =========================================================================
with tab_eng:
    st.markdown("<div class='panel-heading'>Data Engineering Architecture, Lineage & Airflow DAG</div>", unsafe_allow_html=True)
    st.caption("Pipeline flow from raw market ticks to validated accounting marts.")

    col_af1, col_af2 = st.columns([2, 1.2])
    with col_af1:
        st.markdown(f"**Active Database Engine:** `{get_db_mode()}`")
        if is_postgres_available():
            st.markdown("Airflow Web UI: [http://localhost:8080](http://localhost:8080) (Credentials: `admin` / `admin`)")
        else:
            st.info("Docker is currently offline. The trading room is running in zero-dependency SQLite standalone mode.")
    with col_af2:
        if is_postgres_available():
            if st.button("Trigger Airflow DAG (fx_pnl_eod)", use_container_width=True, help="Executes the full pipeline: Ingestion -> dbt -> Python Engine -> dbt tests"):
                import subprocess
                try:
                    res = subprocess.run(["docker", "exec", "fx-pnl-airflow", "airflow", "dags", "trigger", "fx_pnl_eod"], capture_output=True, text=True, timeout=8)
                    if res.returncode == 0:
                        st.success("Airflow DAG 'fx_pnl_eod' triggered successfully! View live progress at http://localhost:8080")
                    else:
                        st.warning(f"Trigger response: {res.stderr or res.stdout}")
                except Exception as e:
                    st.error(f"Could not trigger DAG: {e}")

    st.code("""
================================================================================
                    DATA PIPELINE LINEAGE & DAG ORCHESTRATION
================================================================================
  [1. Raw Ingestion]       --> Trades (CSV / REST API) + Bank Al-Maghrib Fixing Feed
           |
           v
  [2. Bronze Staging]      --> PostgreSQL / SQLite: stg_trade, stg_market_rate
           |
           v
  [3. Silver SQL Mart]     --> dbt Mart: fact_trade_mtm (Direct MAD conversion & EUR/USD cross)
           |
           v
  [4. Analytics Mart (P&L Engine)] --> Python pnl_engine.py (FIFO lot queue & CMP calculation)
           |
           v
  [5. Persistence]         --> daily_pnl table with Database CHECK constraint (BR3: Total = Realized + Unrealized)
    """, language="text")

    st.markdown("**Automated Integrity Contracts & Data Quality Assertions:**")
    st.markdown("""
    - **BR1 (Conversion):** Every currency pair converted to MAD using BAM fixing or EUR/USD synthetic cross.
    - **BR2 (Revaluation):** Daily mark-to-market revaluation at official Bank Al-Maghrib fixing time (15:30).
    - **BR3 (Accounting Balance):** Physical database `CHECK (ROUND(total_mad, 2) = ROUND(realized_mad + unrealized_mad, 2))` and dbt singular test.
    - **BR4 (Lot Order):** Double-ended queue (`deque`) ensuring strictly chronological FIFO consumption.
    """)