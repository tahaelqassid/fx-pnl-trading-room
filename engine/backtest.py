"""
Backtests structure_signal() against real historical candles.
Long-only for clarity; short logic is a direct symmetric extension.
Produces a trade log + equity curve from real market data, not simulated.
"""
import pandas as pd
from engine.market_data import get_candles
from engine.strategy_signals import structure_signal


def run_backtest(symbol: str, interval: str = "1h", outputsize: int = 300,
                  nominal: float = 100_000, window: int = 30):
    candles = get_candles(symbol, interval=interval, outputsize=outputsize)
    trades, equity_curve = [], []
    position = None
    equity = 0.0

    for i in range(window, len(candles)):
        window_df = candles.iloc[i - window:i + 1].reset_index(drop=True)
        signal = structure_signal(window_df)
        bias = signal["bias"]
        price = candles["close"].iloc[i]
        time = candles["datetime"].iloc[i]

        if position is None and bias == "bullish BOS":
            position = {"entry_time": time, "entry_price": price}
        elif position is not None and bias == "bearish BOS":
            pnl = (price - position["entry_price"]) * nominal
            equity += pnl
            trades.append({
                "entry_time": position["entry_time"], "exit_time": time,
                "entry_price": round(position["entry_price"], 5),
                "exit_price": round(price, 5), "pnl": round(pnl, 2),
            })
            position = None

        equity_curve.append({"datetime": time, "equity": round(equity, 2)})

    trades_df = pd.DataFrame(trades)
    equity_df = pd.DataFrame(equity_curve)
    stats = {
        "symbol": symbol,
        "total_trades": len(trades_df),
        "win_rate": round((trades_df["pnl"] > 0).mean(), 3) if len(trades_df) else 0.0,
        "total_pnl": round(trades_df["pnl"].sum(), 2) if len(trades_df) else 0.0,
    }
    return trades_df, equity_df, stats