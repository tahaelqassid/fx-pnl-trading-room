"""
Front-Office to Back-Office Reconciliation Engine (OS6).
Compares Front-Office trade tickets against Back-Office settlement records,
detects rate slippages, unconfirmed trades, nominal mismatches,
and computes accounting P&L variance in MAD.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd


@dataclass
class ReconciliationItem:
    trade_ref: str
    currency_pair: str
    direction: str
    fo_nominal: float
    bo_nominal: float
    fo_rate: float
    bo_rate: float
    status: str  # MATCHED, RATE_DISCREPANCY, NOMINAL_MISMATCH, UNCONFIRMED_FO, UNMATCHED_BO
    rate_diff_pips: float
    pnl_variance_mad: float
    counterparty: str
    details: str


def run_reconciliation(fo_trades_df: pd.DataFrame, bo_records_df: pd.DataFrame, usd_mad_rate: float = 9.9500) -> Dict[str, Any]:
    """
    Reconciles Front-Office trade records with Back-Office settlement confirmations.
    """
    items: List[ReconciliationItem] = []
    
    if fo_trades_df.empty and bo_records_df.empty:
        return {
            "summary": {
                "total_fo": 0, "total_bo": 0, "matched": 0,
                "discrepancies": 0, "match_rate": 1.0,
                "net_pnl_variance_mad": 0.0
            },
            "items": []
        }

    fo_dict = {str(row["source_ref"]): row for _, row in fo_trades_df.iterrows()} if "source_ref" in fo_trades_df else {}
    bo_dict = {str(row["trade_ref"]): row for _, row in bo_records_df.iterrows()} if "trade_ref" in bo_records_df else {}

    all_refs = set(fo_dict.keys()).union(set(bo_dict.keys()))

    matched_count = 0
    discrepancy_count = 0
    total_variance_mad = 0.0

    for ref in sorted(all_refs):
        in_fo = ref in fo_dict
        in_bo = ref in bo_dict

        if in_fo and in_bo:
            fo = fo_dict[ref]
            bo = bo_dict[ref]
            fo_nominal = float(fo["nominal"])
            bo_nominal = float(bo["settled_nominal"])
            fo_rate = float(fo["rate"])
            bo_rate = float(bo["settled_rate"])
            pair = str(fo["currency_pair"])
            direction = str(fo["direction"])
            counterparty = str(bo.get("counterparty", "Interbank Desk"))

            rate_diff = bo_rate - fo_rate
            pip_mult = 10000.0 if not pair.endswith("JPY") else 100.0
            diff_pips = round(rate_diff * pip_mult, 1)

            rate_mult = usd_mad_rate if pair == "EUR/USD" else 1.0
            
            # Rate tolerance: 0.0002 (2 pips)
            is_nominal_match = abs(fo_nominal - bo_nominal) < 1.0
            is_rate_match = abs(rate_diff) <= 0.0002

            if is_nominal_match and is_rate_match:
                status = "MATCHED"
                details = "Exact match across Front-Office and Back-Office."
                pnl_var = 0.0
                matched_count += 1
            elif not is_nominal_match:
                status = "NOMINAL_MISMATCH"
                details = f"Nominal mismatch: FO={fo_nominal:,.0f} vs BO={bo_nominal:,.0f}"
                pnl_var = round((bo_nominal - fo_nominal) * fo_rate * rate_mult, 2)
                discrepancy_count += 1
            else:
                status = "RATE_DISCREPANCY"
                details = f"Rate slippage of {diff_pips:+.1f} pips between booking and settlement"
                sign = 1 if direction == "BUY" else -1
                pnl_var = round(sign * (bo_rate - fo_rate) * fo_nominal * rate_mult, 2)
                discrepancy_count += 1

            total_variance_mad += pnl_var
            items.append(ReconciliationItem(
                trade_ref=ref,
                currency_pair=pair,
                direction=direction,
                fo_nominal=fo_nominal,
                bo_nominal=bo_nominal,
                fo_rate=fo_rate,
                bo_rate=bo_rate,
                status=status,
                rate_diff_pips=diff_pips,
                pnl_variance_mad=pnl_var,
                counterparty=counterparty,
                details=details
            ))

        elif in_fo and not in_bo:
            fo = fo_dict[ref]
            items.append(ReconciliationItem(
                trade_ref=ref,
                currency_pair=str(fo["currency_pair"]),
                direction=str(fo["direction"]),
                fo_nominal=float(fo["nominal"]),
                bo_nominal=0.0,
                fo_rate=float(fo["rate"]),
                bo_rate=0.0,
                status="UNCONFIRMED_FO",
                rate_diff_pips=0.0,
                pnl_variance_mad=0.0,
                counterparty="Pending Confirmation",
                details="Trade booked in Front-Office but pending Back-Office affirmation"
            ))
            discrepancy_count += 1

        else: # in_bo and not in_fo
            bo = bo_dict[ref]
            items.append(ReconciliationItem(
                trade_ref=ref,
                currency_pair=str(bo["currency_pair"]),
                direction=str(bo["direction"]),
                fo_nominal=0.0,
                bo_nominal=float(bo["settled_nominal"]),
                fo_rate=0.0,
                bo_rate=float(bo["settled_rate"]),
                status="UNMATCHED_BO",
                rate_diff_pips=0.0,
                pnl_variance_mad=0.0,
                counterparty=str(bo.get("counterparty", "Unknown")),
                details="Back-Office settlement record with no corresponding Front-Office ticket"
            ))
            discrepancy_count += 1

    total_fo = len(fo_dict)
    total_bo = len(bo_dict)
    match_rate = matched_count / max(len(all_refs), 1)

    items_df = pd.DataFrame([vars(i) for i in items])

    return {
        "summary": {
            "total_fo": total_fo,
            "total_bo": total_bo,
            "matched": matched_count,
            "discrepancies": discrepancy_count,
            "match_rate": round(match_rate, 4),
            "net_pnl_variance_mad": round(total_variance_mad, 2)
        },
        "items": items,
        "items_df": items_df
    }
