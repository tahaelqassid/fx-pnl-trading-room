"""
Exposure risk model — statistical, not ML.

Estimates the probability that a book's unrealized P&L breaches its
stop-loss threshold before end of day, using recent rate volatility
to build a confidence band around today's position.

Deliberately not ML: with a handful of trading days of history, a
trained model would be fit to noise, not signal. A volatility-based
band is the honest, defensible choice at this data volume — and it's
the same logic real risk desks use for intraday VaR-style estimates.
"""
import math
from dataclasses import dataclass


@dataclass
class RiskAssessment:
    book_id: int
    current_unrealized_mad: float
    stop_loss_threshold_mad: float
    estimated_daily_volatility_mad: float
    breach_probability: float
    z_score: float


def daily_volatility_mad(historical_rate_changes_mad: list[float]) -> float:
    """
    Standard deviation of day-over-day P&L swings, in MAD.
    Needs at least 2 historical points to mean anything.
    """
    n = len(historical_rate_changes_mad)
    if n < 2:
        raise ValueError("Need at least 2 historical points to estimate volatility")
    mean = sum(historical_rate_changes_mad) / n
    variance = sum((x - mean) ** 2 for x in historical_rate_changes_mad) / (n - 1)
    return math.sqrt(variance)


def breach_probability(current_unrealized_mad: float, stop_loss_threshold_mad: float,
                        volatility_mad: float) -> float:
    """
    Probability that unrealized P&L moves from its current value past
    the stop-loss threshold, assuming normally-distributed daily moves
    (the standard, explicitly-stated simplifying assumption real desks
    use for quick intraday risk checks -- not a claim of precision).
    """
    distance_to_breach = current_unrealized_mad - (-stop_loss_threshold_mad)
    z = distance_to_breach / volatility_mad
    # P(a standard normal variable exceeds z) via the complementary error function
    prob_no_breach = 0.5 * (1 + math.erf(z / math.sqrt(2)))
    return round(1 - prob_no_breach, 4)


def assess_book(book_id: int, current_unrealized_mad: float, stop_loss_threshold_mad: float,
                 historical_daily_pnl_swings_mad: list[float]) -> RiskAssessment:
    vol = daily_volatility_mad(historical_daily_pnl_swings_mad)
    prob = breach_probability(current_unrealized_mad, stop_loss_threshold_mad, vol)
    z = (current_unrealized_mad + stop_loss_threshold_mad) / vol
    return RiskAssessment(book_id, current_unrealized_mad, stop_loss_threshold_mad, vol, prob, z)