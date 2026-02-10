from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from modules.utils import clamp


@dataclass
class CapTradeConfig:
    annual_cap: float
    free_allocations: float
    trading_limit_pct: float
    offset_limit_pct: float
    base_price: float
    scarcity_factor: float
    bank_balance: float = 0.0


def clearing_price(demand: float, supply: float, base_price: float, scarcity_factor: float) -> float:
    if supply <= 0:
        return base_price * scarcity_factor * 10.0
    ratio = demand / supply
    return base_price * ratio * max(scarcity_factor, 0.0)


def simulate_cap_and_trade(
    emissions_tonnes: float,
    config: CapTradeConfig,
    offsets_used: float = 0.0,
) -> Dict[str, float]:
    eligible_offset_cap = emissions_tonnes * clamp(config.offset_limit_pct, 0.0, 1.0)
    applied_offsets = min(max(offsets_used, 0.0), eligible_offset_cap)

    compliance_demand = max(emissions_tonnes - applied_offsets, 0.0)
    market_supply = max(config.annual_cap, 1e-9)
    price = clearing_price(
        demand=compliance_demand,
        supply=market_supply,
        base_price=config.base_price,
        scarcity_factor=config.scarcity_factor,
    )

    owned_allowances = max(config.free_allocations, 0.0) + max(config.bank_balance, 0.0)

    deficit = max(compliance_demand - owned_allowances, 0.0)
    surplus = max(owned_allowances - compliance_demand, 0.0)

    max_trade_volume = max(config.trading_limit_pct, 0.0) * max(config.annual_cap, 0.0)
    allowances_to_buy = min(deficit, max_trade_volume)
    unmet_after_trade = max(deficit - allowances_to_buy, 0.0)
    allowances_to_sell = min(surplus, max_trade_volume)

    compliance_cost = allowances_to_buy * price
    trading_revenue = allowances_to_sell * price
    net_compliance_cost = compliance_cost - trading_revenue

    bank_balance = max(owned_allowances + allowances_to_buy - allowances_to_sell - compliance_demand, 0.0)

    return {
        "clearing_price": price,
        "allowances_to_buy": allowances_to_buy,
        "allowances_to_sell": allowances_to_sell,
        "unmet_after_trade": unmet_after_trade,
        "compliance_cost": compliance_cost,
        "trading_revenue": trading_revenue,
        "net_compliance_cost": net_compliance_cost,
        "net_position": owned_allowances - compliance_demand,
        "bank_balance": bank_balance,
        "compliance_demand": compliance_demand,
        "applied_offsets": applied_offsets,
    }
