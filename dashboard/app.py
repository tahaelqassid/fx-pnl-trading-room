"""
FX Trading Room — live dashboard.
Reads already-validated data; computes nothing new except display-layer
aggregation. Dark terminal styling; sections: live P&L, market structure,
backtest.
"""
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import psycopg2
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")
from engine.risk_model import assess_book
from engine.market_data import get_candles
from engine.strategy_signals import structure_signal
from engine.backtest import run_backtest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

st.set_page_config(page_title="FX Trading Room | Live P&L", layout="wide", page_icon="📈")
st_autorefresh(interval=6000, key="refresh")

st.markdown("""
<style>
    .stApp { background-color: #0a0e14; }
    * { font-family: 'Consolas', 'Courier New', monospace; }
    h1, h2, h3, .stMarkdown p { color: #d4d8de !important; }
    div[data-testid="stMetricValue"] { font-size: 1.6rem; }
    div[data-testid="stMetric"] {
        background-color: #10151f; border: 1px solid #1f2937;
        border-radius: 6px; padding: 10px 14px;
    }
    .rate-ticker {
        display: flex; gap: 24px; padding: 10px 16px; background-color: #10151f;
        border: 1px solid #1f2937; border-radius: 6px; margin-bottom: 16px;
        font-size: 1rem; color: #9ca3af;
    }
    .rate-ticker b { color: #e5e7eb; }
    .book-header {
        font-size: 1.15rem; font-weight: 700; color: #e5e7eb;
        border-left: 4px solid #3b82f6; padding-left: 10px; margin: 18px 0 8px 0;
    }
</style>
""", unsafe_allow_html=True)

conn = psycopg2.connect(
    host=os.getenv("DBT_HOST", "127.0.0.1"), port=int(os.getenv("DBT_PORT", "5432")),
    dbname=os.getenv("POSTGRES_DB"), user=os.getenv("POSTGRES_USER"), password=os.getenv("POSTGRES_PASSWORD"),
)

# ---------- Header ----------
col_title, col_time = st.columns([3, 1])
col_title.title("📈 FX Trading Room")
col_time.markdown(f"<div style='text-align:right; color:#6b7280; padding-top:22px;'>{datetime.now().strftime('%H:%M:%S')} · MAD accounting</div>", unsafe_allow_html=True)

# ---------- Rate ticker ----------
rates_today = pd.read_sql(
    "SELECT currency_pair, closing_rate, source FROM market_rate WHERE rate_date = CURRENT_DATE", conn
)
if not rates_today.empty:
    ticker_html = "<div class='rate-ticker'>"
    for _, r in rates_today.iterrows():
        ticker_html += f"{r['currency_pair']} <b>{r['closing_rate']:.4f}</b>&nbsp;&nbsp;&nbsp;"
    ticker_html += f"<span style='margin-left:auto; color:#4b5563;'>source: {rates_today.iloc[0]['source']}</span></div>"
    st.markdown(ticker_html, unsafe_allow_html=True)
else:
    st.warning("No market rate for today yet — run: python engine/fetch_real_rates.py")

# ---------- Recalculate control ----------
if st.button("🔄 Recalculate P&L now", type="primary"):
    with st.spinner("Running dbt transformation..."):
        r1 = subprocess.run(["dbt", "run"], cwd=PROJECT_ROOT / "fx_pnl_dbt", capture_output=True, text=True)
    if r1.returncode != 0:
        st.error("dbt run failed:"); st.code(r1.stdout + r1.stderr); st.stop()
    with st.spinner("Running FIFO/WAC calculation engine..."):
        r2 = subprocess.run(["python", "engine/run_daily_pnl.py"], cwd=PROJECT_ROOT, capture_output=True, text=True)
    if r2.returncode != 0:
        st.error("Calculation engine failed:"); st.code(r2.stdout + r2.stderr); st.stop()
    st.success("Recalculated."); st.rerun()

st.divider()

# ---------- Per-book P&L panels ----------
books = pd.read_sql("SELECT id, name, stop_loss_threshold_mad FROM book", conn)

for _, book in books.iterrows():
    history = pd.read_sql(
        "SELECT pnl_date, realized_mad, unrealized_mad, total_mad FROM daily_pnl "
        "WHERE book_id = %s ORDER BY pnl_date", conn, params=(book["id"],),
    )
    live_trades = pd.read_sql(
        "SELECT trade_ts, currency_pair, direction, nominal, rate FROM trade "
        "WHERE book_id = %s ORDER BY trade_ts DESC LIMIT 6", conn, params=(book["id"],),
    )

    st.markdown(f"<div class='book-header'>{book['name']}</div>", unsafe_allow_html=True)
    left, right = st.columns([2, 1])

    with left:
        if not history.empty:
            latest = history.iloc[-1]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Realized", f"{latest['realized_mad']:,.0f} MAD")
            c2.metric("Unrealized", f"{latest['unrealized_mad']:,.0f} MAD")
            c3.metric("Total P&L", f"{latest['total_mad']:,.0f} MAD")

            if len(history) >= 2:
                result = assess_book(
                    book["id"], float(latest["unrealized_mad"]), float(book["stop_loss_threshold_mad"]),
                    history["unrealized_mad"].astype(float).tolist(),
                )
                c4.metric("Breach Risk", f"{result.breach_probability:.2%}")
            else:
                c4.metric("Breach Risk", "—")

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=history["pnl_date"], y=history["total_mad"], name="Total P&L",
                                      line=dict(color="#3b82f6", width=2)))
            fig.add_trace(go.Scatter(x=history["pnl_date"], y=history["realized_mad"], name="Realized",
                                      line=dict(color="#22c55e", width=1.5, dash="dot")))
            fig.add_hline(y=-float(book["stop_loss_threshold_mad"]), line_dash="dash", line_color="#ef4444",
                          annotation_text="stop-loss", annotation_font_color="#ef4444")
            fig.update_layout(
                height=260, margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="#0a0e14", plot_bgcolor="#0a0e14",
                font=dict(color="#9ca3af", family="Consolas"),
                xaxis=dict(gridcolor="#1f2937"), yaxis=dict(gridcolor="#1f2937"),
                legend=dict(orientation="h", y=1.15),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No P&L history yet.")

    with right:
        st.caption("RECENT TRADES")
        if not live_trades.empty:
            styled = live_trades.copy()
            styled["trade_ts"] = pd.to_datetime(styled["trade_ts"]).dt.strftime("%H:%M:%S")
            st.dataframe(styled, hide_index=True, use_container_width=True, height=230)
        else:
            st.caption("No trades yet.")

# ---------- Market structure — real live candles ----------
st.divider()
st.markdown("<div class='book-header'>Market Structure — EUR/USD & XAU/USD</div>", unsafe_allow_html=True)

for symbol, label in [("EUR/USD", "EUR/USD"), ("XAU/USD", "Gold (XAU/USD)")]:
    try:
        candles = get_candles(symbol, interval="15min", outputsize=80)
        signal = structure_signal(candles)
        c1, c2 = st.columns([3, 1])
        with c1:
            fig = go.Figure(data=[go.Candlestick(
                x=candles["datetime"], open=candles["open"], high=candles["high"],
                low=candles["low"], close=candles["close"],
                increasing_line_color="#22c55e", decreasing_line_color="#ef4444",
            )])
            fig.update_layout(
                title=label, height=280, margin=dict(l=10, r=10, t=30, b=10),
                paper_bgcolor="#0a0e14", plot_bgcolor="#0a0e14",
                font=dict(color="#9ca3af", family="Consolas"),
                xaxis=dict(gridcolor="#1f2937", rangeslider_visible=False),
                yaxis=dict(gridcolor="#1f2937"),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        with c2:
            st.metric("Last price", signal.get("last_close", "—"))
            color = "🟢" if "bullish" in signal["bias"] else "🔴" if "bearish" in signal["bias"] else "⚪"
            st.markdown(f"**{color} {signal['bias']}**")
            st.caption(signal["detail"])
    except Exception as e:
        st.warning(f"{label}: could not fetch live data ({e})")

# ---------- Backtest ----------
st.divider()
st.markdown("<div class='book-header'>Strategy Backtest — real historical data</div>", unsafe_allow_html=True)

bt_symbol = st.selectbox("Symbol", ["EUR/USD", "XAU/USD"])
if st.button("▶ Run backtest"):
    with st.spinner("Fetching historical candles and replaying signal..."):
        trades_df, equity_df, stats = run_backtest(bt_symbol, interval="1h", outputsize=300)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total trades", stats["total_trades"])
    c2.metric("Win rate", f"{stats['win_rate']:.1%}")
    c3.metric("Total P&L (quote ccy)", f"{stats['total_pnl']:,.0f}")

    if not equity_df.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=equity_df["datetime"], y=equity_df["equity"],
                                  line=dict(color="#3b82f6", width=2), fill="tozeroy",
                                  fillcolor="rgba(59,130,246,0.1)"))
        fig.update_layout(
            height=260, margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="#0a0e14", plot_bgcolor="#0a0e14",
            font=dict(color="#9ca3af", family="Consolas"),
            xaxis=dict(gridcolor="#1f2937"), yaxis=dict(gridcolor="#1f2937", title="Equity"),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    if not trades_df.empty:
        st.dataframe(trades_df, hide_index=True, use_container_width=True)
    else:
        st.info("No trades generated in this window — try a larger outputsize.")

    st.caption("Long-only market-structure signal, backtested on real historical candles. "
               "Technical-analysis based, not a trading recommendation.")

conn.close()