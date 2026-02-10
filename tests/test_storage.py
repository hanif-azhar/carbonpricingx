from pathlib import Path

from modules.storage import compare_runs, save_run


def test_storage_save_and_compare(tmp_path: Path):
    run_a = save_run({"summary": {"total_emissions": 100, "total_carbon_cost": 1000}}, tmp_path)
    run_b = save_run({"summary": {"total_emissions": 80, "total_carbon_cost": 900}}, tmp_path)

    diff = compare_runs(run_a, run_b)
    assert diff["delta_emissions"] is not None
    assert diff["delta_total_carbon_cost"] is not None
