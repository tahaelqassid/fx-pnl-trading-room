"""
Unit tests for the FX P&L Calculation Engine.
Verifies all reference case studies, FIFO vs CMP matching, synthetic cross resolution,
and the fundamental business identity: Total P&L = Realized + Unrealized.
"""
from datetime import datetime
import pytest
from engine.pnl_engine import (
    Trade, Direction, mtm_pnl, realized_fifo, realized_wac, 
    compute_book_analytics, realized_fifo_with_audit
)

# Reference closing rates from PFE PDF Page 3 & Student Report Page 8
CLOSING_RATES = {
    "USD/MAD": 9.9500,
    "EUR/MAD": 10.8000,
    "EUR/USD": 1.0854,
}

# The 4 official trades from Section 2.2 of the PFE specification
T1 = Trade("T001", datetime(2026, 9, 7, 9, 0), "USD/MAD", Direction.BUY, 1_000_000, 9.9200)
T2 = Trade("T002", datetime(2026, 9, 7, 10, 0), "USD/MAD", Direction.SELL, 500_000, 9.9600)
T3 = Trade("T003", datetime(2026, 9, 7, 11, 0), "EUR/MAD", Direction.BUY, 800_000, 10.7700)
T4 = Trade("T004", datetime(2026, 9, 7, 12, 0), "EUR/USD", Direction.BUY, 600_000, 1.0820)


def test_individual_trade_mtm():
    """Verify each trade's MTM against Table 2.3 of the PFE specification."""
    # Trade 1: Long 1M USD/MAD @ 9.9200 -> (9.9500 - 9.9200) * 1,000,000 = +30,000 MAD
    assert mtm_pnl(T1, CLOSING_RATES) == 30_000.0

    # Trade 2: Short 500K USD/MAD @ 9.9600 -> (9.9600 - 9.9500) * 500,000 = +5,000 MAD
    assert mtm_pnl(T2, CLOSING_RATES) == 5_000.0

    # Trade 3: Long 800K EUR/MAD @ 10.7700 -> (10.8000 - 10.7700) * 800,000 = +24,000 MAD
    assert mtm_pnl(T3, CLOSING_RATES) == 24_000.0

    # Trade 4: Synthetic EUR/USD Long 600K EUR @ 1.0820
    # Implied traded rate: 1.0820 * 9.9500 = 10.7659 MAD
    # Closing rate: 10.8000 MAD -> (10.8000 - 10.7659) * 600,000 = +20,460 MAD
    assert mtm_pnl(T4, CLOSING_RATES) == 20_460.0

    # Total MTM = 30,000 + 5,000 + 24,000 + 20,460 = 79,460 MAD
    total = sum(mtm_pnl(t, CLOSING_RATES) for t in [T1, T2, T3, T4])
    assert total == 79_460.0


def test_realized_and_unrealized_decomposition():
    """Verify the Realized vs Latent split from Section 3.2 of the specification."""
    # Trade 2 partially unwinds Trade 1:
    # 500K sold @ 9.9600 against 500K bought @ 9.9200
    realized, residual = realized_fifo([T1], T2)
    assert realized == 20_000.0
    assert len(residual) == 1
    assert residual[0].nominal == 500_000.0

    # Total MTM is 79,460 MAD. With Realized = 20,000, Unrealized must equal 59,460 MAD.
    unrealized = 79_460.0 - realized
    assert unrealized == 59_460.0


def test_supporting_example_fifo_vs_cmp():
    """
    Verify the Section 4 comparison example:
    Buy 1: 500K @ 9.9100
    Buy 2: 500K @ 9.9300
    Sell:  600K @ 9.9500
    """
    b1 = Trade("B1", datetime(2026, 9, 7, 9, 15), "USD/MAD", Direction.BUY, 500_000, 9.9100)
    b2 = Trade("B2", datetime(2026, 9, 7, 10, 30), "USD/MAD", Direction.BUY, 500_000, 9.9300)
    s1 = Trade("S1", datetime(2026, 9, 7, 14, 0), "USD/MAD", Direction.SELL, 600_000, 9.9500)

    # FIFO Test:
    # Lot 1: 500K @ (9.95 - 9.91) = 20,000 MAD
    # Lot 2: 100K @ (9.95 - 9.93) = 2,000 MAD
    # Total FIFO = 22,000 MAD (validates the correction of the spec's 21,500 typo)
    fifo_realized, residual_lots = realized_fifo([b1, b2], s1)
    assert fifo_realized == 22_000.0
    assert len(residual_lots) == 1
    assert residual_lots[0].nominal == 400_000.0
    assert residual_lots[0].rate == 9.9300

    # CMP / WAC Test:
    # CMP = (500k*9.91 + 500k*9.93) / 1M = 9.9200
    # Realized = (9.9500 - 9.9200) * 600,000 = +18,000 MAD
    cmp_realized, wac_price, residual_nominal = realized_wac([b1, b2], s1)
    assert cmp_realized == 18_000.0
    assert wac_price == 9.9200
    assert residual_nominal == 400_000.0


def test_business_rule_br3_identity():
    """Verify that Total = Realized + Unrealized holds strictly across all methods."""
    analytics_fifo = compute_book_analytics([T1, T2, T3, T4], CLOSING_RATES, method="FIFO")
    assert analytics_fifo["identity_holds"] is True
    assert analytics_fifo["total_mtm_mad"] == 79_460.0
    assert analytics_fifo["total_realized_mad"] == 20_000.0
    assert analytics_fifo["total_unrealized_mad"] == 59_460.0
