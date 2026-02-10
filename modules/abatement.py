from __future__ import annotations

from typing import Dict

import pandas as pd

from modules.finance import irr, npv
from modules.utils import coerce_numeric, ensure_required_columns, normalize_columns

REQUIRED_ABATEMENT_COLUMNS = {
    "initiative_name",
    "max_reduction_pct",
    "cost_per_tonne",
    "capex",
    "target_scope",
    "department",
}


def _build_cash_flows(
    *,
    capex: float,
    annual_carbon_savings: float,
    annual_variable_cost: float,
    years: int,
    annual_savings_growth: float,
) -> list[float]:
    cash_flows = [-capex]
    for year in range(1, years + 1):
        growth = (1.0 + annual_savings_growth) ** (year - 1)
        net_benefit = (annual_carbon_savings - annual_variable_cost) * growth
        cash_flows.append(net_benefit)
    return cash_flows


def evaluate_abatement(
    initiatives: pd.DataFrame,
    baseline_detailed: pd.DataFrame,
    carbon_price: float,
    *,
    discount_rate: float = 0.08,
    analysis_years: int = 10,
    annual_savings_growth: float = 0.0,
) -> Dict[str, pd.DataFrame | float | None]:
    if initiatives is None or initiatives.empty:
        empty = pd.DataFrame(
            columns=[
                "initiative_name",
                "target_scope",
                "department",
                "cost_per_tonne",
                "adopted",
                "reduction_tonnes",
                "abatement_cost",
                "carbon_savings",
                "net_value",
                "cumulative_reduction",
                "npv",
                "irr",
            ]
        )
        return {
            "macc": empty,
            "total_reduction": 0.0,
            "total_cost": 0.0,
            "total_net_value": 0.0,
            "total_npv": 0.0,
            "portfolio_irr": None,
        }

    work = normalize_columns(initiatives.copy())
    ensure_required_columns(work, REQUIRED_ABATEMENT_COLUMNS, "Abatement initiatives")
    work = coerce_numeric(work, ["max_reduction_pct", "cost_per_tonne", "capex"])

    detailed = baseline_detailed.copy()
    detailed["emissions_tonnes"] = pd.to_numeric(detailed["emissions_tonnes"], errors="coerce").fillna(0.0)

    rows = []
    portfolio_cash_flows = [0.0] * (analysis_years + 1)

    for _, row in work.iterrows():
        target_scope = str(row["target_scope"]).strip().lower()
        target_department = str(row["department"]).strip().lower()

        segment = detailed
        if target_scope and target_scope != "all":
            segment = segment[segment["scope"].astype(str).str.lower() == target_scope]
        if target_department and target_department != "all":
            segment = segment[segment["department"].astype(str).str.lower() == target_department]

        baseline_segment_emissions = float(segment["emissions_tonnes"].sum())
        reduction_tonnes = baseline_segment_emissions * (float(row["max_reduction_pct"]) / 100.0)
        adopted = bool(float(carbon_price) >= float(row["cost_per_tonne"]))

        if not adopted:
            reduction_tonnes = 0.0

        variable_cost = reduction_tonnes * float(row["cost_per_tonne"])
        annual_carbon_savings = reduction_tonnes * float(carbon_price)
        abatement_cost = variable_cost + float(row["capex"])
        net_value = annual_carbon_savings - abatement_cost

        cash_flows = _build_cash_flows(
            capex=float(row["capex"]),
            annual_carbon_savings=annual_carbon_savings,
            annual_variable_cost=variable_cost,
            years=analysis_years,
            annual_savings_growth=annual_savings_growth,
        )
        initiative_npv = npv(cash_flows, discount_rate)
        initiative_irr = irr(cash_flows)

        for idx, cf in enumerate(cash_flows):
            portfolio_cash_flows[idx] += cf

        rows.append(
            {
                "initiative_name": row["initiative_name"],
                "target_scope": row["target_scope"],
                "department": row["department"],
                "cost_per_tonne": float(row["cost_per_tonne"]),
                "capex": float(row["capex"]),
                "adopted": adopted,
                "baseline_segment_emissions": baseline_segment_emissions,
                "reduction_tonnes": reduction_tonnes,
                "abatement_cost": abatement_cost,
                "carbon_savings": annual_carbon_savings,
                "net_value": net_value,
                "roi_years": (float(row["capex"]) / annual_carbon_savings) if annual_carbon_savings > 0 else None,
                "npv": initiative_npv,
                "irr": initiative_irr,
                "cash_flows": cash_flows,
            }
        )

    macc = pd.DataFrame(rows).sort_values("cost_per_tonne").reset_index(drop=True)
    macc["cumulative_reduction"] = macc["reduction_tonnes"].cumsum()
    macc["cumulative_cost"] = macc["abatement_cost"].cumsum()

    return {
        "macc": macc,
        "total_reduction": float(macc["reduction_tonnes"].sum()),
        "total_cost": float(macc["abatement_cost"].sum()),
        "total_net_value": float(macc["net_value"].sum()),
        "total_npv": float(macc["npv"].sum()),
        "portfolio_irr": irr(portfolio_cash_flows),
        "portfolio_cash_flows": portfolio_cash_flows,
    }
