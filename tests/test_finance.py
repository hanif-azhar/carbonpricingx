import pytest

from modules.finance import irr, npv


def test_npv_simple_case():
    # -100 upfront, +60 for 2 years at 10%
    value = npv([-100, 60, 60], 0.10)
    assert pytest.approx(value, rel=1e-6) == -100 + 60 / 1.1 + 60 / (1.1**2)


def test_irr_exists_for_mixed_flows():
    rate = irr([-100, 70, 70])
    assert rate is not None
    assert 0.0 < rate < 1.0


def test_irr_none_when_no_sign_change():
    assert irr([10, 5, 3]) is None
