from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def _runs_dir(base_dir: str | Path) -> Path:
    path = Path(base_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_run(payload: Dict[str, Any], base_dir: str | Path) -> Path:
    runs = _runs_dir(base_dir)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    run_path = runs / f"run_{timestamp}.json"
    with run_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return run_path


def list_runs(base_dir: str | Path) -> List[Path]:
    runs = _runs_dir(base_dir)
    return sorted(runs.glob("run_*.json"), reverse=True)


def load_run(path: str | Path) -> Dict[str, Any]:
    run_path = Path(path)
    with run_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def compare_runs(path_a: str | Path, path_b: str | Path) -> Dict[str, float | None]:
    a = load_run(path_a)
    b = load_run(path_b)

    a_total = a.get("summary", {}).get("total_emissions")
    b_total = b.get("summary", {}).get("total_emissions")
    a_cost = a.get("summary", {}).get("total_carbon_cost")
    b_cost = b.get("summary", {}).get("total_carbon_cost")

    delta_emissions = None
    if a_total is not None and b_total is not None:
        delta_emissions = float(b_total) - float(a_total)

    delta_cost = None
    if a_cost is not None and b_cost is not None:
        delta_cost = float(b_cost) - float(a_cost)

    return {
        "run_a": str(path_a),
        "run_b": str(path_b),
        "delta_emissions": delta_emissions,
        "delta_total_carbon_cost": delta_cost,
    }
