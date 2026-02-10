from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


def normalize_column_name(name: str) -> str:
    return str(name).strip().lower().replace(" ", "_").replace("-", "_")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = {col: normalize_column_name(col) for col in df.columns}
    return df.rename(columns=renamed)


def ensure_required_columns(df: pd.DataFrame, required: Iterable[str], frame_name: str) -> None:
    missing = set(required) - set(df.columns)
    if missing:
        missing_cols = ", ".join(sorted(missing))
        raise ValueError(f"{frame_name} missing required columns: {missing_cols}")


def coerce_numeric(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    out = df.copy()
    for col in columns:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def load_csv(path: str | Path) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")
    return pd.read_csv(p)
