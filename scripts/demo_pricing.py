"""Demo: price the most rain-affected time step of the simulated data."""

from __future__ import annotations

import h3

from ml.simulation import SimulationConfig, generate
from pricing.equilibrium import price_cells


def main() -> None:
    df = generate(SimulationConfig(days=14, seed=42))
    peak_ts = df.groupby("timestamp")["rain_mm_h"].sum().idxmax()
    snap = df[df["timestamp"] == peak_ts]
    demand = dict(zip(snap["cell"], snap["demand"].astype(float)))
    supply = dict(zip(snap["cell"], snap["supply"].astype(float)))

    decisions = price_cells(demand, supply, neighbors=lambda c: h3.grid_ring(c, 1))
    print(f"Snapshot: {peak_ts}  (heaviest rain)")
    print(f"{'cell':<17}{'rain':>7}{'demand':>8}{'supply':>8}{'raw m':>8}{'final m':>9}")
    rain = dict(zip(snap["cell"], snap["rain_mm_h"]))
    top = sorted(decisions.values(), key=lambda d: d.multiplier, reverse=True)[:8]
    for d in top:
        print(
            f"{d.cell:<17}{rain[d.cell]:>7.1f}{d.demand:>8.0f}{d.supply:>8.0f}"
            f"{d.raw_multiplier:>8.2f}{d.multiplier:>9.2f}"
        )


if __name__ == "__main__":
    main()
