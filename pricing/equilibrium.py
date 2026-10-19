"""Dynamic pricing equilibrium engine.

For each spatial cell the engine finds the price multiplier ``m`` that clears
the market, i.e. the effective demand equals the available supply::

    D * m ** -e = S   =>   m = (D / S) ** (1 / e)

The raw multiplier is then smoothed across neighboring cells, rate-limited
against the previous round, and clamped to ``[m_min, m_max]``.

The module is pure Python and performs no I/O.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass

from pricing.config import PricingConfig

NeighborFn = Callable[[str], Iterable[str]]


@dataclass(frozen=True)
class PriceDecision:
    """Auditable result of pricing one cell."""

    cell: str
    demand: float
    supply: float
    raw_multiplier: float
    smoothed_multiplier: float
    multiplier: float
    capped: bool


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def solve_multiplier(demand: float, supply: float, cfg: PricingConfig) -> float:
    """Return the market-clearing multiplier for a single cell.

    Rules:
        * No demand pressure (``demand <= supply``) -> ``m_min``.
        * No supply but positive demand -> ``m_max``.
        * Otherwise ``(D / S) ** (1 / e)`` clamped to ``[m_min, m_max]``.
    """
    if demand < 0 or supply < 0 or math.isnan(demand) or math.isnan(supply):
        raise ValueError("demand and supply must be non-negative numbers")
    if demand <= supply:
        return cfg.m_min
    if supply == 0:
        return cfg.m_max
    raw = (demand / supply) ** (1.0 / cfg.elasticity)
    return clamp(raw, cfg.m_min, cfg.m_max)


def limit_step(previous: float | None, target: float, max_step: float) -> float:
    """Limit the change between two rounds to ``max_step``."""
    if previous is None:
        return target
    return clamp(target, previous - max_step, previous + max_step)


def smooth_spatially(
    multipliers: Mapping[str, float], neighbors: NeighborFn, weight: float
) -> dict[str, float]:
    """Blend each cell's multiplier with the mean of its known neighbors.

    ``result = (1 - w) * own + w * mean(neighbors)``. Cells without any known
    neighbor keep their own value. The result stays inside the min/max of the
    input values, so configured bounds are never violated.
    """
    smoothed: dict[str, float] = {}
    for cell, own in multipliers.items():
        values = [multipliers[n] for n in neighbors(cell) if n != cell and n in multipliers]
        if not values or weight == 0:
            smoothed[cell] = own
        else:
            smoothed[cell] = (1.0 - weight) * own + weight * (sum(values) / len(values))
    return smoothed


def price_cells(
    demand: Mapping[str, float],
    supply: Mapping[str, float],
    cfg: PricingConfig | None = None,
    previous: Mapping[str, float] | None = None,
    neighbors: NeighborFn | None = None,
) -> dict[str, PriceDecision]:
    """Compute price decisions for every cell present in ``demand``.

    Args:
        demand: Forecast demand per cell.
        supply: Available supply per cell (missing cells are treated as 0).
        cfg: Engine configuration.
        previous: Multipliers from the previous round, used for rate limiting.
        neighbors: Function returning neighboring cell ids (for spatial smoothing).
    """
    cfg = cfg or PricingConfig()
    previous = previous or {}

    raw = {c: solve_multiplier(d, supply.get(c, 0.0), cfg) for c, d in demand.items()}
    smoothed = (
        smooth_spatially(raw, neighbors, cfg.neighbor_weight)
        if neighbors is not None
        else dict(raw)
    )

    decisions: dict[str, PriceDecision] = {}
    for cell, demand_value in demand.items():
        limited = limit_step(previous.get(cell), smoothed[cell], cfg.max_step)
        final = clamp(limited, cfg.m_min, cfg.m_max)
        decisions[cell] = PriceDecision(
            cell=cell,
            demand=demand_value,
            supply=supply.get(cell, 0.0),
            raw_multiplier=raw[cell],
            smoothed_multiplier=smoothed[cell],
            multiplier=final,
            capped=final >= cfg.m_max,
        )
    return decisions


def final_price(base_price: float, multiplier: float) -> float:
    """Apply a multiplier to a base price, rounded to 2 decimals."""
    if base_price < 0:
        raise ValueError("base_price must be non-negative")
    return round(base_price * multiplier, 2)
