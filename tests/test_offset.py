from modules.offset_engine import simulate_offsets


def test_offset_model_limits_and_residuals():
    result = simulate_offsets(
        total_emissions=1000,
        offset_price=10,
        integrity_score=80,
        offset_limit_pct=0.2,
        quality_discount_factor=0.9,
    )
    assert result["eligible_offsets"] == 200
    assert result["residual_emissions"] < 1000
