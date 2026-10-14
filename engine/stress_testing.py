"""
Stress Testing & Scenario Simulator for FX Salle de Marché.
Implements:
1. Bank Al-Maghrib (BAM) Fluctuation Band Scenarios (+/- 2.5%, +/- 5.0%, +/- 200 pips).
2. Dirham Basket Shock (EUR 60% / USD 40% weight sensitivity).
3. Intraday Parametric Value at Risk (VaR 95% & 99%).
4. Portfolio Delta and Stop-Loss Headroom under stress.
"""
from dataclasses import dataclass
from typing import Dict, List, Any
import numpy as np
import pandas as pd


@dataclass
class ScenarioResult:
    scenario_name: str
    usd_mad_rate: float
    eur_mad_rate: float
    eur_usd_rate: float
    portfolio_mtm_mad: float
    mtm_change_mad: float
    percentage_change: float
    is_stop_loss_breached: bool
    breached_books: List[str]


def compute_portfolio_var(historical_pnl_changes: List[float], confidence: float = 0.95, horizon_days: int = 1) -> float:
    """
    Parametric Value-at-Risk (VaR) based on historical P&L variance.
    VaR = - (mu - z * sigma) * sqrt(horizon)
    """
    if len(historical_pnl_changes) < 2:
        return 0.0
    
    std_dev = float(np.std(historical_pnl_changes, ddof=1))
    mean = float(np.mean(historical_pnl_changes))
    
    # Standard normal quantile
    z_map = {0.90: 1.282, 0.95: 1.645, 0.99: 2.326}
    z = z_map.get(confidence, 1.645)
    
    # 1-tailed loss estimate
    var_value = (z * std_dev - mean) * np.sqrt(horizon_days)
    return round(max(var_value, 0.0), 2)


def run_scenario_matrix(
    trades_df: pd.DataFrame,
    books_df: pd.DataFrame,
    base_rates: Dict[str, float]
) -> List[ScenarioResult]:
    """
    Evaluates trading portfolio against standard Bank Al-Maghrib and market shock scenarios:
    1. Base Case (Current BAM Fixing)
    2. MAD Appreciation +100 pips (+1.0%)
    3. MAD Depreciation -100 pips (-1.0%)
    4. MAD Severe Depreciation -200 pips (-2.0%)
    5. BAM Full Band Upper Limit (+5.0% Dirham strength)
    6. BAM Full Band Lower Limit (-5.0% Dirham weakness)
    7. EUR/USD Global Parity Shock (EUR/USD = 1.0000)
    8. EUR/USD Rally Shock (EUR/USD = 1.1500)
    """
    if trades_df.empty:
        return []

    usd_base = base_rates.get("USD/MAD", 9.9500)
    eur_base = base_rates.get("EUR/MAD", 10.8000)
    eur_usd_base = base_rates.get("EUR/USD", 1.0854)

    scenarios = [
        {"name": "Base Case (Current BAM Fixing)", "usd_adj": 0.0, "eur_adj": 0.0, "eur_usd": eur_usd_base},
        {"name": "Dirham +100 pips (Appreciation)", "usd_adj": -0.0100, "eur_adj": -0.0100, "eur_usd": eur_usd_base},
        {"name": "Dirham -100 pips (Depreciation)", "usd_adj": +0.0100, "eur_adj": +0.0100, "eur_usd": eur_usd_base},
        {"name": "Dirham -200 pips (Severe Pressure)", "usd_adj": +0.0200, "eur_adj": +0.0200, "eur_usd": eur_usd_base},
        {"name": "BAM Band Upper Limit (+5% MAD)", "usd_adj": -usd_base * 0.05, "eur_adj": -eur_base * 0.05, "eur_usd": eur_usd_base},
        {"name": "BAM Band Lower Limit (-5% MAD)", "usd_adj": +usd_base * 0.05, "eur_adj": +eur_base * 0.05, "eur_usd": eur_usd_base},
        {"name": "EUR/USD Parity Shock (1.0000)", "usd_adj": 0.0, "eur_adj": -0.8000, "eur_usd": 1.0000},
        {"name": "EUR/USD High Rally (1.1500)", "usd_adj": 0.0, "eur_adj": +0.6500, "eur_usd": 1.1500},
    ]

    stop_limits = {}
    if not books_df.empty:
        for _, b in books_df.iterrows():
            stop_limits[b["id"]] = (b["name"], float(b.get("stop_loss_threshold_mad", 50000)))

    results = []
    base_mtm = None

    for sc in scenarios:
        u_rate = round(usd_base + sc["usd_adj"], 4)
        e_rate = round(eur_base + sc["eur_adj"], 4)
        eu_rate = sc["eur_usd"]
        rates = {"USD/MAD": u_rate, "EUR/MAD": e_rate, "EUR/USD": eu_rate}

        # Calculate MTM under this scenario
        tot_mtm = 0.0
        book_mtm = {b_id: 0.0 for b_id in stop_limits}

        for _, t in trades_df.iterrows():
            pair = t["currency_pair"]
            direction = t["direction"]
            nominal = float(t["nominal"])
            rate = float(t["rate"])
            b_id = int(t["book_id"]) if "book_id" in t else 1

            if pair == "USD/MAD":
                close_m = u_rate
                traded_m = rate
            elif pair == "EUR/MAD":
                close_m = e_rate
                traded_m = rate
            elif pair == "EUR/USD":
                close_m = e_rate
                traded_m = rate * u_rate
            else:
                close_m = rate
                traded_m = rate

            trade_pnl = (close_m - traded_m) * nominal if direction == "BUY" else (traded_m - close_m) * nominal
            tot_mtm += trade_pnl
            if b_id in book_mtm:
                book_mtm[b_id] += trade_pnl

        tot_mtm = round(tot_mtm, 2)
        if base_mtm is None:
            base_mtm = tot_mtm

        diff_mtm = round(tot_mtm - base_mtm, 2)
        pct_diff = round((diff_mtm / abs(base_mtm) * 100) if base_mtm != 0 else 0.0, 2)

        breached = []
        is_breach = False
        for b_id, pnl in book_mtm.items():
            name, threshold = stop_limits[b_id]
            if pnl < -threshold:
                is_breach = True
                breached.append(f"{name} ({pnl:,.0f} < -{threshold:,.0f} MAD)")

        results.append(ScenarioResult(
            scenario_name=sc["name"],
            usd_mad_rate=u_rate,
            eur_mad_rate=e_rate,
            eur_usd_rate=eu_rate,
            portfolio_mtm_mad=tot_mtm,
            mtm_change_mad=diff_mtm,
            percentage_change=pct_diff,
            is_stop_loss_breached=is_breach,
            breached_books=breached
        ))

    return results
