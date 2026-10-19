"""CLI: generate synthetic rain/demand/supply data into ml/data/raw/."""

from __future__ import annotations

import argparse
from pathlib import Path

from ml.simulation import SimulationConfig, generate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=Path, default=Path("ml/data/raw/simulated.csv"))
    args = parser.parse_args()

    df = generate(SimulationConfig(days=args.days, seed=args.seed))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"Wrote {len(df):,} rows to {args.out}")


if __name__ == "__main__":
    main()
