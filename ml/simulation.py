"""Synthetic rain-driven demand/supply data generator.

Produces a reproducible panel dataset (one row per H3 cell and time step) in
which demand rises with rainfall while supply (couriers/drivers) drops. It is
meant for developing and testing the forecasting and pricing pipeline until real
data is available.
"""

from __future__ import annotations

from dataclasses import dataclass

import h3
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SimulationConfig:
    center_lat: float = 13.7563  # Bangkok
    center_lng: float = 100.5018
    h3_resolution: int = 8
    ring_size: int = 3  # 37 cells for k=3
    days: int = 14
    step_minutes: int = 15
    start: str = "2026-01-05"  # a Monday
    seed: int = 42
    storms_per_day: float = 0.8
    rain_demand_boost: float = 0.9  # +90% demand at saturation
    rain_supply_drop: float = 0.45  # -45% supply at saturation
    rain_saturation_mm_h: float = 10.0


# Hourly demand profile: lunch and dinner peaks.
_HOURLY = np.array(
    [0.2, 0.1, 0.1, 0.1, 0.1, 0.2, 0.4, 0.7, 0.8, 0.7, 0.8, 1.2,
     1.5, 1.2, 0.9, 0.8, 0.9, 1.2, 1.6, 1.5, 1.1, 0.8, 0.5, 0.3]
)  # fmt: skip


def _cells(cfg: SimulationConfig) -> list[str]:
    center = h3.latlng_to_cell(cfg.center_lat, cfg.center_lng, cfg.h3_resolution)
    return sorted(h3.grid_disk(center, cfg.ring_size))


def _rain_field(
    cfg: SimulationConfig, cells: list[str], n_steps: int, rng: np.random.Generator
) -> np.ndarray:
    """Return rain intensity (mm/h) with shape ``(n_steps, n_cells)``."""
    steps_per_day = 24 * 60 // cfg.step_minutes
    index = {c: i for i, c in enumerate(cells)}
    rain = np.zeros((n_steps, len(cells)))
    for day in range(cfg.days):
        for _ in range(rng.poisson(cfg.storms_per_day)):
            start = day * steps_per_day + int(rng.integers(0, steps_per_day))
            duration = int(rng.integers(4, 17))  # 1-4 hours
            peak = float(rng.uniform(5, 40))
            radius = int(rng.integers(1, cfg.ring_size + 1))
            origin = cells[int(rng.integers(0, len(cells)))]
            footprint = h3.grid_disk(origin, radius)
            for t in range(duration):
                step = start + t
                if step >= n_steps:
                    break
                envelope = np.sin(np.pi * (t + 0.5) / duration)
                for cell in footprint:
                    if cell in index:
                        dist = h3.grid_distance(origin, cell)
                        falloff = 1.0 - dist / (radius + 1)
                        rain[step, index[cell]] += peak * envelope * falloff
    return rain


def generate(cfg: SimulationConfig | None = None) -> pd.DataFrame:
    """Generate the synthetic dataset.

    Columns: timestamp, cell, lat, lng, hour, day_of_week, rain_mm_h, temp_c,
    demand, supply.
    """
    cfg = cfg or SimulationConfig()
    rng = np.random.default_rng(cfg.seed)
    cells = _cells(cfg)
    n_cells = len(cells)
    steps_per_day = 24 * 60 // cfg.step_minutes
    n_steps = cfg.days * steps_per_day

    times = pd.date_range(cfg.start, periods=n_steps, freq=f"{cfg.step_minutes}min")
    hours = times.hour.to_numpy()
    dow = times.dayofweek.to_numpy()
    hour_frac = hours + times.minute.to_numpy() / 60.0

    rain = _rain_field(cfg, cells, n_steps, rng)
    rain_effect = np.tanh(rain / cfg.rain_saturation_mm_h)  # 0..~1

    popularity = rng.lognormal(mean=0.0, sigma=0.35, size=n_cells)
    fleet = rng.lognormal(mean=0.0, sigma=0.20, size=n_cells)
    weekend = np.where(dow >= 5, 1.15, 1.0)[:, None]
    profile = np.interp(hour_frac, np.arange(24), _HOURLY)[:, None]

    base_demand = 12.0 * profile * weekend * popularity[None, :]
    demand_mean = base_demand * (1.0 + cfg.rain_demand_boost * rain_effect)
    demand = rng.poisson(demand_mean)

    # Supply follows a smoother profile than demand and drops in the rain.
    supply_profile = 0.6 + 0.4 * np.interp(hour_frac, np.arange(24), _HOURLY) / _HOURLY.max()
    base_supply = 16.0 * supply_profile[:, None] * fleet[None, :]
    supply_mean = base_supply * (1.0 - cfg.rain_supply_drop * rain_effect)
    supply = rng.poisson(supply_mean)

    temp = 31.0 - 4.0 * rain_effect + 2.0 * np.sin(2 * np.pi * (hour_frac[:, None] - 9) / 24)
    temp = temp + rng.normal(0, 0.3, size=temp.shape)

    centers = np.array([h3.cell_to_latlng(c) for c in cells])
    df = pd.DataFrame(
        {
            "timestamp": np.repeat(times.to_numpy(), n_cells),
            "cell": np.tile(cells, n_steps),
            "lat": np.tile(centers[:, 0], n_steps),
            "lng": np.tile(centers[:, 1], n_steps),
            "hour": np.repeat(hours, n_cells),
            "day_of_week": np.repeat(dow, n_cells),
            "rain_mm_h": rain.reshape(-1).round(2),
            "temp_c": temp.reshape(-1).round(2),
            "demand": demand.reshape(-1),
            "supply": supply.reshape(-1),
        }
    )
    return df
