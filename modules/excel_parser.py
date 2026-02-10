from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from modules.utils import ensure_required_columns, normalize_columns

ACTIVITY_COLUMNS = {
    "department",
    "scope",
    "activity",
    "amount",
    "unit",
    "emission_factor",
    "source",
}
EMISSION_FACTOR_COLUMNS = {"scope", "activity", "co2_factor", "ch4_factor", "n2o_factor", "region", "year"}
DEPARTMENT_COLUMNS = {"department", "scope", "activity", "amount", "unit", "emission_factor", "source"}
ABATEMENT_COLUMNS = {
    "initiative_name",
    "max_reduction_pct",
    "cost_per_tonne",
    "capex",
    "target_scope",
    "department",
}
ALLOWANCE_COLUMNS = {"year", "allocated_allowances", "initial_cap", "offset_limit_pct"}


@dataclass
class ParsedInput:
    activities: pd.DataFrame
    emission_factors: pd.DataFrame
    departments: pd.DataFrame
    abatement: pd.DataFrame
    allowances: pd.DataFrame


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    out = normalize_columns(df.copy())
    return out.dropna(how="all")


def _normalize_abatement(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "max_reduction_pct" not in out.columns and "reduction_pct" in out.columns:
        out = out.rename(columns={"reduction_pct": "max_reduction_pct"})
    return out


def _empty_df(columns: set[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=sorted(columns))


def _validate_if_not_empty(df: pd.DataFrame, required: set[str], name: str) -> None:
    if not df.empty:
        ensure_required_columns(df, required, name)


def _sheet_kind(sheet_name: str, cleaned: pd.DataFrame) -> str | None:
    key = str(sheet_name).strip().lower().replace(" ", "_")
    cols = set(cleaned.columns)

    if key in {"activities", "activity", "activity_data"}:
        return "activities"
    if key in {"emission_factors", "factors", "factor_library"}:
        return "emission_factors"
    if key in {"department_mapped_data", "departments", "department_data"}:
        return "departments"
    if key in {"abatement_initiative_list", "abatement", "initiatives"}:
        return "abatement"
    if key in {"allowances", "cap_and_trade_allowances", "market_allowances"}:
        return "allowances"

    if ACTIVITY_COLUMNS.issubset(cols):
        return "activities"
    if DEPARTMENT_COLUMNS.issubset(cols):
        return "departments"
    if ALLOWANCE_COLUMNS.issubset(cols):
        return "allowances"
    if EMISSION_FACTOR_COLUMNS.issubset(cols):
        return "emission_factors"

    abatement_like = {"initiative_name", "department", "target_scope", "cost_per_tonne", "capex"}
    if abatement_like.issubset(cols) and ({"max_reduction_pct", "reduction_pct"} & cols):
        return "abatement"

    return None


def _parse_sheets(sheets: Dict[str, pd.DataFrame]) -> ParsedInput:
    activities = _empty_df(ACTIVITY_COLUMNS)
    emission_factors = _empty_df(EMISSION_FACTOR_COLUMNS)
    departments = _empty_df(DEPARTMENT_COLUMNS)
    abatement = _empty_df(ABATEMENT_COLUMNS)
    allowances = _empty_df(ALLOWANCE_COLUMNS)

    for sheet_name, sheet in sheets.items():
        cleaned = _clean(sheet)
        kind = _sheet_kind(sheet_name, cleaned)
        if kind == "activities":
            activities = cleaned
        elif kind == "emission_factors":
            emission_factors = cleaned
        elif kind == "departments":
            departments = cleaned
        elif kind == "abatement":
            abatement = _normalize_abatement(cleaned)
        elif kind == "allowances":
            allowances = cleaned

    if departments.empty and not activities.empty:
        departments = activities.copy()

    _validate_if_not_empty(activities, ACTIVITY_COLUMNS, "Activities")
    _validate_if_not_empty(emission_factors, EMISSION_FACTOR_COLUMNS, "Emission factors")
    _validate_if_not_empty(departments, DEPARTMENT_COLUMNS, "Department-mapped data")
    _validate_if_not_empty(abatement, ABATEMENT_COLUMNS, "Abatement initiative list")
    _validate_if_not_empty(allowances, ALLOWANCE_COLUMNS, "Cap-and-trade allowances")

    return ParsedInput(
        activities=activities,
        emission_factors=emission_factors,
        departments=departments,
        abatement=abatement,
        allowances=allowances,
    )


def parse_uploaded_file(file_obj: Any) -> ParsedInput:
    if file_obj is None:
        raise ValueError("No file uploaded.")

    name = getattr(file_obj, "name", "")
    lower_name = str(name).lower()

    if lower_name.endswith(".csv"):
        activities = _clean(pd.read_csv(file_obj))
        _validate_if_not_empty(activities, ACTIVITY_COLUMNS, "Activities")
        return ParsedInput(
            activities=activities,
            emission_factors=_empty_df(EMISSION_FACTOR_COLUMNS),
            departments=activities.copy(),
            abatement=_empty_df(ABATEMENT_COLUMNS),
            allowances=_empty_df(ALLOWANCE_COLUMNS),
        )
    elif lower_name.endswith(".xlsx"):
        sheets = pd.read_excel(file_obj, sheet_name=None)
        return _parse_sheets(sheets)
    else:
        raise ValueError("Unsupported file type. Use CSV or XLSX.")


def parse_path(path: str | Path) -> ParsedInput:
    p = Path(path)
    if p.suffix.lower() == ".csv":
        activities = _clean(pd.read_csv(p))
        _validate_if_not_empty(activities, ACTIVITY_COLUMNS, "Activities")
        return ParsedInput(
            activities=activities,
            emission_factors=_empty_df(EMISSION_FACTOR_COLUMNS),
            departments=activities.copy(),
            abatement=_empty_df(ABATEMENT_COLUMNS),
            allowances=_empty_df(ALLOWANCE_COLUMNS),
        )

    if p.suffix.lower() == ".xlsx":
        sheets = pd.read_excel(p, sheet_name=None)
        return _parse_sheets(sheets)

    raise ValueError("Unsupported file type. Use CSV or XLSX.")
