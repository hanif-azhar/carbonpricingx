from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import pandas as pd

from modules.utils import clamp


@dataclass
class InternalFeeConfig:
    internal_fee_rate: float
    response_factor: float


def simulate_internal_fee(department_emissions: pd.DataFrame, config: InternalFeeConfig) -> Dict[str, pd.DataFrame | float]:
    if department_emissions is None or department_emissions.empty:
        raise ValueError("Department emissions data is empty.")
    required = {"department", "emissions_tonnes"}
    missing = required - set(department_emissions.columns)
    if missing:
        raise ValueError(f"Department emissions missing columns: {', '.join(sorted(missing))}")

    table = department_emissions.copy()
    table["emissions_tonnes"] = pd.to_numeric(table["emissions_tonnes"], errors="coerce").fillna(0.0)

    response_multiplier = 1.0 - (config.response_factor * config.internal_fee_rate / 100.0)
    response_multiplier = clamp(response_multiplier, 0.0, 1.0)

    table["fee_cost"] = table["emissions_tonnes"] * config.internal_fee_rate
    table["adjusted_emissions"] = table["emissions_tonnes"] * response_multiplier
    table["emissions_reduction"] = table["emissions_tonnes"] - table["adjusted_emissions"]
    table["savings_from_reduction"] = table["emissions_reduction"] * config.internal_fee_rate
    table["net_cost_vs_savings"] = table["fee_cost"] - table["savings_from_reduction"]
    table = table.sort_values("fee_cost", ascending=False)

    return {
        "table": table,
        "total_fee_cost": float(table["fee_cost"].sum()),
        "total_adjusted_emissions": float(table["adjusted_emissions"].sum()),
        "total_reduction": float(table["emissions_reduction"].sum()),
    }
