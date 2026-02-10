from __future__ import annotations

from typing import Dict, Tuple

import pandas as pd

from modules.utils import coerce_numeric, ensure_required_columns, normalize_columns

REQUIRED_ACTIVITY_COLUMNS = {
    "department",
    "scope",
    "activity",
    "amount",
    "unit",
    "emission_factor",
    "source",
}

_SCOPE_MAP = {
    "scope_1": "scope1",
    "scope 1": "scope1",
    "scope1": "scope1",
    "s1": "scope1",
    "scope_2": "scope2",
    "scope 2": "scope2",
    "scope2": "scope2",
    "s2": "scope2",
    "scope_3": "scope3",
    "scope 3": "scope3",
    "scope3": "scope3",
    "s3": "scope3",
}


def _normalize_scope(scope: str) -> str:
    value = str(scope).strip().lower()
    return _SCOPE_MAP.get(value, value)


def validate_activities(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        raise ValueError("Activities data is empty.")

    cleaned = normalize_columns(df.copy())
    ensure_required_columns(cleaned, REQUIRED_ACTIVITY_COLUMNS, "Activities")
    cleaned = coerce_numeric(cleaned, ["amount", "emission_factor"])

    if cleaned["department"].isna().any() or (cleaned["department"].astype(str).str.strip() == "").any():
        raise ValueError("Activities contains missing department values.")

    if cleaned["amount"].isna().any() or (cleaned["amount"] < 0).any():
        raise ValueError("Activities contains invalid amount values. Amount must be numeric and non-negative.")

    if cleaned["emission_factor"].isna().any():
        raise ValueError("Activities contains invalid emission_factor values. emission_factor must be numeric.")

    cleaned["department"] = cleaned["department"].astype(str).str.strip()
    cleaned["scope"] = cleaned["scope"].apply(_normalize_scope)
    cleaned["activity"] = cleaned["activity"].astype(str).str.strip()
    cleaned["unit"] = cleaned["unit"].astype(str).str.strip()
    cleaned["source"] = cleaned["source"].astype(str).str.strip()
    return cleaned


def calculate_emissions(df: pd.DataFrame) -> Dict[str, pd.DataFrame | float | Dict[str, float]]:
    cleaned = validate_activities(df)
    detailed = cleaned.copy()
    detailed["emissions_tonnes"] = detailed["amount"] * detailed["emission_factor"]

    by_scope = (
        detailed.groupby("scope", as_index=False)["emissions_tonnes"].sum().sort_values("emissions_tonnes", ascending=False)
    )
    by_department = (
        detailed.groupby("department", as_index=False)["emissions_tonnes"]
        .sum()
        .sort_values("emissions_tonnes", ascending=False)
    )

    total = float(detailed["emissions_tonnes"].sum())

    scope_totals = {row["scope"]: float(row["emissions_tonnes"]) for _, row in by_scope.iterrows()}

    return {
        "detailed": detailed,
        "by_scope": by_scope,
        "by_department": by_department,
        "total_emissions": total,
        "scope_totals": scope_totals,
    }


def emissions_baseline_by_segment(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    detailed = calculate_emissions(df)["detailed"]
    by_scope = detailed.groupby("scope", as_index=False)["emissions_tonnes"].sum()
    by_dept_scope = detailed.groupby(["department", "scope"], as_index=False)["emissions_tonnes"].sum()
    return by_scope, by_dept_scope
