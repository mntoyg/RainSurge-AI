"""Configuration for the dynamic pricing equilibrium engine."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PricingConfig:
    """Tunable parameters of the pricing engine.

    Attributes:
        elasticity: Price elasticity of demand ``e`` (> 0). Effective demand at
            multiplier ``m`` is ``D * m ** -e``.
        m_min: Lowest allowed multiplier (1.0 means no discount below base price).
        m_max: Hard cap on the multiplier (fairness guardrail).
        max_step: Largest allowed change of a cell's multiplier between two
            consecutive pricing rounds.
        neighbor_weight: Share ``w`` in [0, 1] of the spatially smoothed
            multiplier that comes from neighboring cells.
    """

    elasticity: float = 1.2
    m_min: float = 1.0
    m_max: float = 3.0
    max_step: float = 0.25
    neighbor_weight: float = 0.3

    def __post_init__(self) -> None:
        if self.elasticity <= 0:
            raise ValueError("elasticity must be > 0")
        if self.m_min <= 0 or self.m_max < self.m_min:
            raise ValueError("require 0 < m_min <= m_max")
        if self.max_step <= 0:
            raise ValueError("max_step must be > 0")
        if not 0.0 <= self.neighbor_weight <= 1.0:
            raise ValueError("neighbor_weight must be within [0, 1]")
