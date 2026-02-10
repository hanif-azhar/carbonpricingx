from __future__ import annotations

from typing import Iterable


def npv(cash_flows: Iterable[float], discount_rate: float) -> float:
    rate = float(discount_rate)
    total = 0.0
    for idx, flow in enumerate(cash_flows):
        total += float(flow) / ((1.0 + rate) ** idx)
    return total


def irr(
    cash_flows: Iterable[float],
    *,
    lower_bound: float = -0.99,
    upper_bound: float = 10.0,
    max_iter: int = 200,
    tolerance: float = 1e-7,
) -> float | None:
    flows = [float(x) for x in cash_flows]
    if len(flows) < 2:
        return None

    if not any(x < 0 for x in flows) or not any(x > 0 for x in flows):
        return None

    def f(rate: float) -> float:
        return npv(flows, rate)

    low = lower_bound
    high = upper_bound
    f_low = f(low)
    f_high = f(high)

    if f_low == 0:
        return low
    if f_high == 0:
        return high

    if f_low * f_high > 0:
        return None

    for _ in range(max_iter):
        mid = (low + high) / 2.0
        f_mid = f(mid)
        if abs(f_mid) <= tolerance:
            return mid

        if f_low * f_mid < 0:
            high = mid
            f_high = f_mid
        else:
            low = mid
            f_low = f_mid

    return (low + high) / 2.0
