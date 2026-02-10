from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from modules.utils import clamp


@dataclass
class CarbonPricingConfig:
    elasticity: float = 0.0
    fuel_switching_factor: float = 0.0
    energy_efficiency_factor: float = 0.0


def _adjustment_multiplier(price: float, config: CarbonPricingConfig) -> float:
    # Guideline formula: adjusted_activity = activity * (1 - elasticity * (P / 100))
    elastic_component = 1.0 - (config.elasticity * (price / 100.0))
    # Additional controls from UI modeled as percentage reductions.
    extra_reduction = config.fuel_switching_factor + config.energy_efficiency_factor
    multiplier = elastic_component * (1.0 - extra_reduction)
    return clamp(multiplier, 0.0, 1.0)


def run_price_scenarios(
    total_emissions_tonnes: float,
    prices: Iterable[float],
    config: CarbonPricingConfig,
) -> pd.DataFrame:
    rows = []
    for price in prices:
        multiplier = _adjustment_multiplier(float(price), config)
        adjusted_emissions = total_emissions_tonnes * multiplier
        carbon_cost = adjusted_emissions * float(price)
        reduction_pct = 0.0
        if total_emissions_tonnes > 0:
            reduction_pct = (1.0 - adjusted_emissions / total_emissions_tonnes) * 100.0

        rows.append(
            {
                "carbon_price": float(price),
                "adjusted_emissions": adjusted_emissions,
                "carbon_cost": carbon_cost,
                "reduction_pct": reduction_pct,
                "multiplier": multiplier,
            }
        )

    return pd.DataFrame(rows).sort_values("carbon_price").reset_index(drop=True)


def recommend_carbon_price(macc_df: pd.DataFrame) -> float:
    if macc_df is None or macc_df.empty or "cost_per_tonne" not in macc_df.columns:
        return 50.0
    return float(macc_df["cost_per_tonne"].median())
