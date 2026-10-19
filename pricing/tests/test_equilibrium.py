import pytest

from pricing.config import PricingConfig
from pricing.equilibrium import (
    final_price,
    limit_step,
    price_cells,
    smooth_spatially,
    solve_multiplier,
)

CFG = PricingConfig(elasticity=1.0, m_min=1.0, m_max=3.0, max_step=0.5, neighbor_weight=0.5)


def test_no_pressure_gives_min_multiplier():
    assert solve_multiplier(50, 100, CFG) == 1.0
    assert solve_multiplier(100, 100, CFG) == 1.0


def test_zero_supply_hits_cap():
    assert solve_multiplier(10, 0, CFG) == CFG.m_max


def test_zero_demand_zero_supply_is_min():
    assert solve_multiplier(0, 0, CFG) == CFG.m_min


def test_equilibrium_clears_market():
    cfg = PricingConfig(elasticity=1.5, m_max=10.0)
    demand, supply = 180.0, 100.0
    m = solve_multiplier(demand, supply, cfg)
    assert demand * m**-cfg.elasticity == pytest.approx(supply)


def test_multiplier_is_monotonic_in_demand_and_bounded():
    cfg = PricingConfig()
    values = [solve_multiplier(d, 100, cfg) for d in range(0, 1000, 25)]
    assert values == sorted(values)
    assert all(cfg.m_min <= v <= cfg.m_max for v in values)


def test_higher_elasticity_gives_lower_multiplier():
    low = solve_multiplier(200, 100, PricingConfig(elasticity=0.8))
    high = solve_multiplier(200, 100, PricingConfig(elasticity=2.0))
    assert high < low


@pytest.mark.parametrize("d,s", [(-1, 1), (1, -1), (float("nan"), 1)])
def test_invalid_inputs_raise(d, s):
    with pytest.raises(ValueError):
        solve_multiplier(d, s, CFG)


def test_limit_step():
    assert limit_step(None, 2.5, 0.5) == 2.5
    assert limit_step(1.0, 2.5, 0.5) == 1.5
    assert limit_step(2.0, 1.0, 0.5) == 1.5


def test_spatial_smoothing_reduces_cliff_and_keeps_bounds():
    mult = {"a": 3.0, "b": 1.0, "c": 1.0}
    nbrs = {"a": ["b"], "b": ["a", "c"], "c": ["b"]}
    out = smooth_spatially(mult, lambda c: nbrs[c], 0.5)
    assert out["a"] == pytest.approx(2.0)
    assert out["b"] == pytest.approx(0.5 * 1.0 + 0.5 * 2.0)
    assert all(1.0 <= v <= 3.0 for v in out.values())


def test_isolated_cell_unchanged_by_smoothing():
    assert smooth_spatially({"a": 2.0}, lambda c: [], 0.5) == {"a": 2.0}


def test_price_cells_applies_rate_limit_and_cap_flag():
    demand = {"a": 1000.0, "b": 100.0}
    supply = {"a": 100.0, "b": 100.0}
    out = price_cells(demand, supply, CFG, previous={"a": 1.0, "b": 1.0})
    assert out["a"].raw_multiplier == CFG.m_max
    assert out["a"].multiplier == pytest.approx(1.5)  # 1.0 + max_step
    assert out["a"].capped is False
    assert out["b"].multiplier == 1.0

    out = price_cells(demand, supply, CFG, previous={"a": 2.8})
    assert out["a"].multiplier == CFG.m_max
    assert out["a"].capped is True


def test_missing_supply_treated_as_zero():
    out = price_cells({"x": 5.0}, {}, CFG)
    assert out["x"].multiplier == CFG.m_max


def test_final_price():
    assert final_price(10.0, 1.236) == 12.36
    with pytest.raises(ValueError):
        final_price(-1.0, 1.0)


def test_config_validation():
    with pytest.raises(ValueError):
        PricingConfig(elasticity=0)
    with pytest.raises(ValueError):
        PricingConfig(m_min=2.0, m_max=1.0)
    with pytest.raises(ValueError):
        PricingConfig(neighbor_weight=1.5)
