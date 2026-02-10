from __future__ import annotations

from typing import Dict

from modules.utils import clamp


def simulate_offsets(
    total_emissions: float,
    offset_price: float,
    integrity_score: float,
    offset_limit_pct: float,
    quality_discount_factor: float,
) -> Dict[str, float]:
    integrity = clamp(integrity_score / 100.0, 0.0, 1.0)
    limit = clamp(offset_limit_pct, 0.0, 1.0)
    qdf = clamp(quality_discount_factor, 0.0, 1.5)

    eligible_offsets = total_emissions * limit
    effective_offset_cost = offset_price * qdf
    total_offset_cost = eligible_offsets * effective_offset_cost

    effective_reduction = eligible_offsets * integrity
    residual_emissions = max(total_emissions - effective_reduction, 0.0)

    return {
        "eligible_offsets": eligible_offsets,
        "effective_offset_cost": effective_offset_cost,
        "total_offset_cost": total_offset_cost,
        "effective_reduction": effective_reduction,
        "residual_emissions": residual_emissions,
    }
