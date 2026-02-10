import pandas as pd

from modules.internal_market import InternalFeeConfig, simulate_internal_fee


def test_internal_fee_simulation_outputs():
    dept = pd.DataFrame(
        [
            {"department": "A", "emissions_tonnes": 100.0},
            {"department": "B", "emissions_tonnes": 50.0},
        ]
    )
    result = simulate_internal_fee(dept, InternalFeeConfig(internal_fee_rate=20, response_factor=0.1))
    assert result["total_fee_cost"] == 3000
    assert "adjusted_emissions" in result["table"].columns
