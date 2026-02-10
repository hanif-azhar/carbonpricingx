import pandas as pd
import pytest

from modules.emissions_engine import calculate_emissions


def test_calculate_emissions_totals():
    df = pd.DataFrame(
        [
            {
                "department": "manufacturing",
                "scope": "scope1",
                "activity": "gas",
                "amount": 100,
                "unit": "kwh",
                "emission_factor": 0.2,
                "source": "test",
            },
            {
                "department": "office",
                "scope": "scope2",
                "activity": "power",
                "amount": 50,
                "unit": "kwh",
                "emission_factor": 0.3,
                "source": "test",
            },
        ]
    )
    result = calculate_emissions(df)
    assert pytest.approx(result["total_emissions"]) == 35.0
    assert set(result["by_scope"]["scope"]) == {"scope1", "scope2"}


def test_calculate_emissions_invalid_negative_amount():
    df = pd.DataFrame(
        [
            {
                "department": "manufacturing",
                "scope": "scope1",
                "activity": "gas",
                "amount": -1,
                "unit": "kwh",
                "emission_factor": 0.2,
                "source": "test",
            }
        ]
    )
    with pytest.raises(ValueError):
        calculate_emissions(df)
