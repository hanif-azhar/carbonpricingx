from pathlib import Path

import pandas as pd

from modules.excel_parser import parse_path


def test_parse_sample_xlsx():
    sample = Path(__file__).resolve().parents[1] / "data" / "sample_activities.xlsx"
    parsed = parse_path(sample)
    assert not parsed.activities.empty
    assert "department" in parsed.activities.columns


def test_parse_abatement_only_sheet_with_reduction_pct_alias(tmp_path: Path):
    workbook = tmp_path / "abatement_only.xlsx"
    sheet = pd.DataFrame(
        [
            {
                "initiative_name": "initiative_a",
                "department": "manufacturing",
                "target_scope": "scope1",
                "reduction_pct": 12.0,
                "cost_per_tonne": 45.0,
                "capex": 10000.0,
            }
        ]
    )
    with pd.ExcelWriter(workbook, engine="openpyxl") as writer:
        sheet.to_excel(writer, sheet_name="Sheet1", index=False)

    parsed = parse_path(workbook)
    assert parsed.activities.empty
    assert not parsed.abatement.empty
    assert "max_reduction_pct" in parsed.abatement.columns
