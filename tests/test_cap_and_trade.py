from modules.cap_and_trade import CapTradeConfig, simulate_cap_and_trade


def test_cap_and_trade_buy_required_when_deficit():
    result = simulate_cap_and_trade(
        emissions_tonnes=1000,
        config=CapTradeConfig(
            annual_cap=800,
            free_allocations=700,
            trading_limit_pct=1.0,
            offset_limit_pct=0.1,
            base_price=50,
            scarcity_factor=1.0,
        ),
    )
    assert result["allowances_to_buy"] > 0
    assert result["compliance_cost"] > 0
