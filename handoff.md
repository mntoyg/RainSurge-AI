# handoff.md — Knowledge Transfer & Issue Log

_Last updated: 2026-10-19_

## Things we fixed

| Date | Area | Issue | Resolution |
|------|------|-------|------------|
| 2026-10-19 | Git | The parent directory (`~`) is itself a Git repository, so project files would be tracked by the wrong repo. | Initialized a standalone Git repository inside the project folder. |

_Add new rows as bugs and tasks are resolved. Include the commit hash or PR link when available._

## Problems that we face

| # | Category | Problem / Constraint | Impact | Proposed direction |
|---|----------|----------------------|--------|--------------------|
| 1 | Process | Agents are limited to 14% of weekly usage per day (see `agents.md`). | Large tasks must be split across days. | Keep tasks small; log state here before stopping. |
| 2 | Data | No training data selected yet; hyper-local rainfall plus demand data is scarce publicly. | Blocks model training. | Start with public weather data and a synthetic demand simulator in `scripts/`. |
| 3 | ML | Self-hosted training needs enough local compute for LSTM models. | Slow iteration. | Start with XGBoost/LightGBM baselines; use small sequence models. |
| 4 | Architecture | Kafka plus Zookeeper is heavy for local development. | Slow startup on laptops. | Evaluate Kafka in KRaft mode or Redpanda for dev only. |
| 5 | Pricing | Surge pricing during bad weather carries fairness and regulatory risk. | Reputation and legal exposure. | Enforce hard caps, cooldowns, and audit logs. |
| 6 | Latency | Meeting p95 < 50 ms depends on keeping inference off the request path. | Design constraint. | Precompute prices in workers; API only reads Redis. |

## Environment Notes for the Next Engineer

- Working directory: `/Users/thanapatmanasom/code-project/RainSurge AI`
- Use the standalone repo in this folder, not the parent home-directory repo.
- Read `agents.md` first; it contains hard constraints (no external AI APIs, quota rules).
- No application code exists yet; start from Phase 1 in `progress.md`.
