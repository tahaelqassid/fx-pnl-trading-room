"""
FX P&L Calculation Engine
Pure, dependency-free business logic for MTM, FIFO, and WAC.
"""
from dataclasses import dataclass
from collections import deque
from datetime import datetime
from enum import Enum


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


def to_mad_rate(pair: str, rates: dict) -> float:
    if pair.endswith("/MAD"):
        return rates[pair]
    if pair == "EUR/USD":
        return rates["EUR/MAD"]
    raise ValueError(f"Unsupported pair for MAD conversion: {pair}")


def mtm_pnl(trade: Trade, closing_rates: dict) -> float:
    close = to_mad_rate(trade.currency_pair, closing_rates)
    traded_mad = trade.rate if trade.currency_pair.endswith("/MAD") else trade.rate * closing_rates["USD/MAD"]
    if trade.direction == Direction.BUY:
        return round((close - traded_mad) * trade.nominal, 2)
    return round((traded_mad - close) * trade.nominal, 2)


def realized_fifo(buys: list[Trade], sell: Trade) -> tuple[float, list[Trade]]:
    queue = deque(sorted(buys, key=lambda t: t.timestamp))
    to_unwind = sell.nominal
    realized = 0.0
    residual = []

    while queue and to_unwind > 0:
        lot = queue.popleft()
        if lot.nominal <= to_unwind:
            realized += (sell.rate - lot.rate) * lot.nominal
            to_unwind -= lot.nominal
        else:
            realized += (sell.rate - lot.rate) * to_unwind
            residual.append(Trade(lot.trade_id, lot.timestamp, lot.currency_pair,
                                   lot.direction, lot.nominal - to_unwind, lot.rate))
            to_unwind = 0

    residual.extend(queue)
    return round(realized, 2), residual


def realized_wac(buys: list[Trade], sell: Trade) -> tuple[float, float, float]:
    total_nominal = sum(t.nominal for t in buys)
    wac = sum(t.nominal * t.rate for t in buys) / total_nominal
    realized = (sell.rate - wac) * sell.nominal
    residual_nominal = total_nominal - sell.nominal
    return round(realized, 2), round(wac, 4), residual_nominal