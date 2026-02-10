import pandas as pd

from modules.abatement import evaluate_abatement


def test_abatement_adoption_logic():
    initiatives = pd.DataFrame(
        [
            {
                "initiative_name": "cheap",
                "max_reduction_pct": 10,
                "cost_per_tonne": 20,
                "capex": 0,
                "target_scope": "scope1",
                "department": "all",
            },
            {
                "initiative_name": "expensive",
                "max_reduction_pct": 10,
                "cost_per_tonne": 100,
                "capex": 0,
                "target_scope": "scope1",
                "department": "all",
            },
        ]
    )
    baseline = pd.DataFrame(
        [
            {
                "department": "x",
                "scope": "scope1",
                "activity": "a",
                "amount": 1,
                "unit": "kwh",
                "emission_factor": 10,
                "source": "s",
                "emissions_tonnes": 100,
            }
        ]
    )

    result = evaluate_abatement(initiatives, baseline, carbon_price=50)
    macc = result["macc"]
    assert macc.loc[macc["initiative_name"] == "cheap", "adopted"].iloc[0]
    assert not macc.loc[macc["initiative_name"] == "expensive", "adopted"].iloc[0]
    assert "npv" in macc.columns
    assert "irr" in macc.columns
    assert result["total_npv"] is not None
