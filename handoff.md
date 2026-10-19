# handoff.md — Knowledge Transfer & Issue Log

_Last updated: 2026-10-19_

## Things we fixed

| Date | Area | Issue | Resolution |
|------|------|-------|------------|
| 2026-10-19 | Git | The parent directory (`~`) is itself a Git repository, so project files would be tracked by the wrong repo. | Initialized a standalone Git repository inside the project folder. |
| 2026-10-19 | Data | No training data available. | Added a reproducible synthetic simulator (`ml/simulation.py`). |

_Add new rows as bugs and tasks are resolved. Include the commit hash or PR link when available._

## Problems that we face

| # | Category | Problem / Constraint | Impact | Proposed direction |
|---|----------|----------------------|--------|--------------------|
| 1 | Process | Agents are limited to 14% of weekly usage per day (see `agents.md`). | Large tasks must be split across days. | Keep tasks small; log state here before stopping. |
| 2 | Data | No training data selected yet; hyper-local rainfall plus demand data is scarce publicly. | Blocks model training. | Start with public weather data and a synthetic demand simulator in `scripts/`. |
| 3 | ML | Self-hosted training needs enough local compute for LSTM models. | Slow iteration. | Start with XGBoost/LightGBM baselines; use small sequence models. |
| 4 | Architecture | Kafka plus Zookeeper is heavy for local development. | Slow startup on laptops. | Evaluate Kafka in KRaft mode or Redpanda for dev only. |
| 5 | Pricing | Surge pricing during bad weather carries fairness and regulatory risk. | Reputation and legal exposure. | Enforce hard caps, cooldowns, and audit logs. |
| 7 | Calibration | With default parameters (elasticity 1.2, cap 3.0) many cells hit the cap during heavy simulated rain; the simulator's demand/supply ratio is likely too aggressive. | Unrealistic price levels. | Tune simulator and elasticity against real data. |
| 8 | Environment | Local Python is 3.10; docs target 3.11+. | None so far; code is 3.10-compatible. | Keep `requires-python >= 3.10` until upgrade. |
| 6 | Latency | Meeting p95 < 50 ms depends on keeping inference off the request path. | Design constraint. | Precompute prices in workers; API only reads Redis. |

## Environment Notes for the Next Engineer

- Working directory: `/Users/thanapatmanasom/code-project/RainSurge AI`
- Use the standalone repo in this folder, not the parent home-directory repo.
- Read `agents.md` first; it contains hard constraints (no external AI APIs, quota rules).
- Setup: `python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt`, then `.venv/bin/pytest`.
- Try it: `PYTHONPATH=. .venv/bin/python scripts/demo_pricing.py`.
- Implemented: `pricing/` and `ml/simulation.py`. The API, workers, and model training are not started.
