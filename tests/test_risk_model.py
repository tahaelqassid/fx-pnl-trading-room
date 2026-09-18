# tests/test_risk_model.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine.risk_model import breach_probability

def test_low_volatility_far_from_threshold_is_low_risk():
    # +50,000 unrealized, stop-loss at -20,000 -> 70,000 MAD of room, low vol
    prob = breach_probability(current_unrealized_mad=50000, stop_loss_threshold_mad=20000, volatility_mad=5000)
    assert prob < 0.05

def test_already_past_threshold_is_high_risk():
    # already at -25,000, past the -20,000 stop-loss -> high risk
    prob = breach_probability(current_unrealized_mad=-25000, stop_loss_threshold_mad=20000, volatility_mad=5000)
    assert prob > 0.5

if __name__ == "__main__":
    test_low_volatility_far_from_threshold_is_low_risk()
    test_already_past_threshold_is_high_risk()
    print("ALL RISK MODEL TESTS PASSED")