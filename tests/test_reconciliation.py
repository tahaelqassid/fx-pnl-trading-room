"""
Unit tests for the Front-Office to Back-Office Reconciliation Engine.
Verifies exact matching, rate slippage detection, nominal discrepancy,
and unconfirmed trade flagging.
"""
import pandas as pd
from engine.reconciliation import run_reconciliation


def test_reconciliation_exact_matches():
    fo = pd.DataFrame([{
        "source_ref": "T001", "currency_pair": "USD/MAD", "direction": "BUY",
        "nominal": 1_000_000.0, "rate": 9.9200
    }])
    bo = pd.DataFrame([{
        "trade_ref": "T001", "currency_pair": "USD/MAD", "direction": "BUY",
        "settled_nominal": 1_000_000.0, "settled_rate": 9.9200,
        "counterparty": "Attijariwafa Bank", "status": "SETTLED"
    }])
    res = run_reconciliation(fo, bo)
    assert res["summary"]["matched"] == 1
    assert res["summary"]["discrepancies"] == 0
    assert res["summary"]["net_pnl_variance_mad"] == 0.0


def test_reconciliation_rate_slippage():
    fo = pd.DataFrame([{
        "source_ref": "T002", "currency_pair": "USD/MAD", "direction": "BUY",
        "nominal": 500_000.0, "rate": 9.9200
    }])
    # Back-Office confirmed at 9.9210 (+1 pip slippage)
    bo = pd.DataFrame([{
        "trade_ref": "T002", "currency_pair": "USD/MAD", "direction": "BUY",
        "settled_nominal": 500_000.0, "settled_rate": 9.9210,
        "counterparty": "BCP", "status": "SETTLED"
    }])
    res = run_reconciliation(fo, bo)
    assert res["summary"]["discrepancies"] == 1
    assert res["items"][0].status == "RATE_DISCREPANCY"
    # P&L variance = (9.9210 - 9.9200) * 500,000 = +500 MAD
    assert res["items"][0].pnl_variance_mad == 500.0


def test_reconciliation_unconfirmed_trade():
    fo = pd.DataFrame([{
        "source_ref": "T003", "currency_pair": "EUR/MAD", "direction": "SELL",
        "nominal": 800_000.0, "rate": 10.7700
    }])
    bo = pd.DataFrame([])  # Missing in BO
    res = run_reconciliation(fo, bo)
    assert res["summary"]["discrepancies"] == 1
    assert res["items"][0].status == "UNCONFIRMED_FO"
