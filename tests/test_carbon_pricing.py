import pytest

from modules.carbon_pricing import CarbonPricingConfig, run_price_scenarios


def test_price_scenarios_cost_growth_without_reduction():
    cfg = CarbonPricingConfig(elasticity=0.0, fuel_switching_factor=0.0, energy_efficiency_factor=0.0)
    df = run_price_scenarios(1000.0, [0, 50, 100], cfg)
    assert df.loc[df["carbon_price"] == 50, "carbon_cost"].iloc[0] == 50000
    assert df.loc[df["carbon_price"] == 100, "carbon_cost"].iloc[0] == 100000


def test_price_scenarios_elasticity_reduces_emissions():
    cfg = CarbonPricingConfig(elasticity=0.2)
    df = run_price_scenarios(1000.0, [100], cfg)
    adjusted = df.loc[0, "adjusted_emissions"]
    assert pytest.approx(adjusted) == 800.0
