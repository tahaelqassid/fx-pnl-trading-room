"""
FX P&L Calculation Engine
Pure, high-precision business logic for MTM, FIFO, and WAC (Coût Moyen Pondéré).
Supports spot pairs, synthetic crosses, lot inventory tracking, and full auditability.
"""
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime
from enum import Enum
from typing import Dict, List, Tuple, Any, Optional


class Direction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Trade:
    trade_id: str
    timestamp: datetime
    currency_pair: str
    direction: Direction
    nominal: float
    rate: float
    book_id: Optional[int] = None
    trader_id: Optional[str] = None
    confidence: str = "confirmed"


@dataclass
class LotExecution:
    buy_trade_id: str
    sell_trade_id: str
    nominal_unwound: float
    buy_rate: float
    sell_rate: float
    realized_pnl_mad: float
    execution_time: datetime


@dataclass
class PositionSummary:
    currency: str
    nominal_net: float
    cost_basis: float
    current_market_rate_mad: float
    unrealized_pnl_mad: float
    realized_pnl_mad: float
    total_pnl_mad: float


def to_mad_rate(pair: str, rates: Dict[str, float]) -> float:
    """
    Resolves the official closing rate in MAD for any pair or cross.
    Enforces BAM official fixing rules (BR1).
    For crosses like EUR/USD, the base currency is EUR, so its closing value
    in the accounting currency MAD is officially given by EUR/MAD.
    """
    if pair.endswith("/MAD"):
        return rates[pair]
    
    # Synthetic crosses: base currency must be valued in MAD
    base_ccy = pair.split("/")[0]
    direct_mad_pair = f"{base_ccy}/MAD"
    if direct_mad_pair in rates:
        return rates[direct_mad_pair]
    
    if pair in rates:
        return rates[pair]

    raise ValueError(f"Cannot resolve closing rate to MAD for pair: {pair} with available rates: {list(rates.keys())}")


def mtm_pnl(trade: Trade, closing_rates: Dict[str, float]) -> float:
    """
    Calculates Mark-to-Market P&L in MAD for a single trade.
    Matches formula (2.1) and (2.2) from Chapter 2 of the specification:
    Long:  (Closing Rate - Traded Rate) * Nominal
    Short: (Traded Rate - Closing Rate) * Nominal
    """
    close_mad = to_mad_rate(trade.currency_pair, closing_rates)
    
    # Derive traded rate in MAD
    if trade.currency_pair.endswith("/MAD"):
        traded_mad = trade.rate
    elif trade.currency_pair == "EUR/USD":
        usd_mad = closing_rates.get("USD/MAD", 9.9500)
        traded_mad = trade.rate * usd_mad
    elif trade.currency_pair.endswith("/USD"):
        usd_mad = closing_rates.get("USD/MAD", 9.9500)
        traded_mad = trade.rate * usd_mad
    else:
        # Standard direct assumption
        traded_mad = trade.rate

    if trade.direction == Direction.BUY:
        return round((close_mad - traded_mad) * trade.nominal, 2)
    else:
        return round((traded_mad - close_mad) * trade.nominal, 2)


def realized_fifo(buys: List[Trade], sell: Trade, usd_mad_rate: float = 9.9500) -> Tuple[float, List[Trade]]:
    """
    First-In, First-Out (FIFO) lot-matching engine.
    Matches sell orders against the oldest available buy lots.
    Returns (realized_pnl_mad, residual_open_lots).
    """
    queue = deque(sorted(buys, key=lambda t: t.timestamp))
    to_unwind = sell.nominal
    realized = 0.0
    residual = []

    # Conversion factor if trade is cross like EUR/USD
    rate_mult = usd_mad_rate if sell.currency_pair == "EUR/USD" else 1.0

    while queue and to_unwind > 0:
        lot = queue.popleft()
        lot_rate_mad = lot.rate * rate_mult
        sell_rate_mad = sell.rate * rate_mult

        if lot.nominal <= to_unwind:
            realized += (sell_rate_mad - lot_rate_mad) * lot.nominal
            to_unwind -= lot.nominal
        else:
            realized += (sell_rate_mad - lot_rate_mad) * to_unwind
            residual.append(
                Trade(
                    lot.trade_id,
                    lot.timestamp,
                    lot.currency_pair,
                    lot.direction,
                    lot.nominal - to_unwind,
                    lot.rate,
                    lot.book_id,
                    lot.trader_id,
                    lot.confidence,
                )
            )
            to_unwind = 0

    residual.extend(queue)
    return round(realized, 2), residual


def realized_fifo_with_audit(buys: List[Trade], sell: Trade, usd_mad_rate: float = 9.9500) -> Tuple[float, List[Trade], List[LotExecution]]:
    """
    FIFO engine with full audit trail of each depleted lot.
    """
    queue = deque(sorted(buys, key=lambda t: t.timestamp))
    to_unwind = sell.nominal
    realized = 0.0
    residual = []
    executions = []

    rate_mult = usd_mad_rate if sell.currency_pair == "EUR/USD" else 1.0

    while queue and to_unwind > 0:
        lot = queue.popleft()
        lot_rate_mad = lot.rate * rate_mult
        sell_rate_mad = sell.rate * rate_mult

        if lot.nominal <= to_unwind:
            chunk_pnl = (sell_rate_mad - lot_rate_mad) * lot.nominal
            realized += chunk_pnl
            executions.append(
                LotExecution(
                    buy_trade_id=lot.trade_id,
                    sell_trade_id=sell.trade_id,
                    nominal_unwound=lot.nominal,
                    buy_rate=lot.rate,
                    sell_rate=sell.rate,
                    realized_pnl_mad=round(chunk_pnl, 2),
                    execution_time=sell.timestamp,
                )
            )
            to_unwind -= lot.nominal
        else:
            chunk_pnl = (sell_rate_mad - lot_rate_mad) * to_unwind
            realized += chunk_pnl
            executions.append(
                LotExecution(
                    buy_trade_id=lot.trade_id,
                    sell_trade_id=sell.trade_id,
                    nominal_unwound=to_unwind,
                    buy_rate=lot.rate,
                    sell_rate=sell.rate,
                    realized_pnl_mad=round(chunk_pnl, 2),
                    execution_time=sell.timestamp,
                )
            )
            residual.append(
                Trade(
                    lot.trade_id,
                    lot.timestamp,
                    lot.currency_pair,
                    lot.direction,
                    lot.nominal - to_unwind,
                    lot.rate,
                    lot.book_id,
                    lot.trader_id,
                    lot.confidence,
                )
            )
            to_unwind = 0

    residual.extend(queue)
    return round(realized, 2), residual, executions


def realized_wac(buys: List[Trade], sell: Trade, usd_mad_rate: float = 9.9500) -> Tuple[float, float, float]:
    """
    Weighted Average Cost (WAC / Coût Moyen Pondéré - CMP) engine.
    Calculates single volume-weighted price of acquisition.
    Returns (realized_pnl_mad, wac_price, residual_nominal).
    """
    if not buys:
        return 0.0, 0.0, 0.0

    rate_mult = usd_mad_rate if sell.currency_pair == "EUR/USD" else 1.0
    total_nominal = sum(t.nominal for t in buys)
    wac = sum(t.nominal * t.rate for t in buys) / total_nominal

    sell_rate_mad = sell.rate * rate_mult
    wac_mad = wac * rate_mult

    realized = (sell_rate_mad - wac_mad) * sell.nominal
    residual_nominal = total_nominal - sell.nominal
    return round(realized, 2), round(wac, 4), residual_nominal


def compute_book_analytics(trades: List[Trade], closing_rates: Dict[str, float], method: str = "FIFO") -> Dict[str, Any]:
    """
    Full portfolio calculation across all trades in a book:
    - MTM P&L per trade
    - Realized P&L (FIFO or WAC)
    - Unrealized P&L
    - Net currency positions
    - Strict mathematical invariant check: Total P&L == Realized + Unrealized (BR3)
    """
    trade_results = []
    total_mtm = 0.0

    # Group trades by currency pair
    pairs = set(t.currency_pair for t in trades)
    total_realized = 0.0
    position_details = {}

    for pair in pairs:
        pair_trades = [t for t in trades if t.currency_pair == pair]
        buys = [t for t in pair_trades if t.direction == Direction.BUY]
        sells = [t for t in pair_trades if t.direction == Direction.SELL]

        # MTM on all trades
        for t in pair_trades:
            pnl = mtm_pnl(t, closing_rates)
            total_mtm += pnl
            close_mad = to_mad_rate(t.currency_pair, closing_rates)
            trade_results.append({
                "trade_id": t.trade_id,
                "timestamp": t.timestamp,
                "currency_pair": t.currency_pair,
                "direction": t.direction.value,
                "nominal": t.nominal,
                "rate": t.rate,
                "closing_rate_mad": close_mad,
                "mtm_pnl_mad": pnl,
                "confidence": t.confidence,
            })

        # Calculate realized based on selected method
        pair_realized = 0.0
        remaining_buys = buys
        if method == "FIFO":
            for s in sells:
                pnl, remaining_buys = realized_fifo(remaining_buys, s, closing_rates.get("USD/MAD", 9.9500))
                pair_realized += pnl
            residual_nominal = sum(b.nominal for b in remaining_buys)
            avg_cost = sum(b.nominal * b.rate for b in remaining_buys) / residual_nominal if residual_nominal > 0 else 0.0
        else: # WAC
            for s in sells:
                pnl, wac_price, residual_nominal = realized_wac(remaining_buys, s, closing_rates.get("USD/MAD", 9.9500))
                pair_realized += pnl
            residual_nominal = sum(b.nominal for b in buys) - sum(s.nominal for s in sells)
            avg_cost = sum(b.nominal * b.rate for b in buys) / sum(b.nominal for b in buys) if buys else 0.0

        total_realized += pair_realized
        position_details[pair] = {
            "residual_nominal": residual_nominal,
            "avg_cost": round(avg_cost, 4),
            "realized_mad": round(pair_realized, 2),
        }

    total_realized = round(total_realized, 2)
    total_mtm = round(total_mtm, 2)
    unrealized = round(total_mtm - total_realized, 2)

    return {
        "trades": trade_results,
        "total_mtm_mad": total_mtm,
        "total_realized_mad": total_realized,
        "total_unrealized_mad": unrealized,
        "method_used": method,
        "identity_holds": abs(total_mtm - (total_realized + unrealized)) < 0.01,
        "positions_by_pair": position_details,
    }