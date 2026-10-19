# progress.md — Task Tracking

_Last updated: 2026-10-19_

## What we have done

- [x] Defined project vision: RainSurge AI, a hyper-local dynamic pricing and demand forecasting engine.
- [x] Set project constraints: self-hosted ML only, no external AI APIs, public-GitHub-ready.
- [x] Created repository folder structure (`api/`, `ml/`, `pricing/`, `workers/`, `infra/`, `docs/`, `scripts/`, `.github/`).
- [x] Wrote `agents.md` (agent rules, 14% weekly usage per day quota, boundaries, commands).
- [x] Wrote `architecture.md` (data flow, tech stack, folder structure, CI/CD, run instructions).
- [x] Wrote `progress.md` and `handoff.md`.
- [x] Added `README.md` and `.gitignore`.
- [x] Initialized a standalone Git repository inside the project folder and pushed to public GitHub.
- [x] Pricing engine (`pricing/`): equilibrium solver, spatial smoothing, rate limiting, caps, 16 unit tests.
- [x] Synthetic data simulator (`ml/simulation.py`, `scripts/simulate_data.py`): rain-driven demand/supply per H3 cell.
- [x] Demo script (`scripts/demo_pricing.py`), `pyproject.toml`, `requirements*.txt`, ruff config.

## What we plan to do next

### Phase 1 — Foundations
- [ ] Add `.env.example` (`pyproject.toml` and requirements files are done).
- [ ] Add `infra/docker/docker-compose.yml` (Redis, Kafka, Zookeeper, API, worker).
- [ ] Add GitHub Actions workflow `.github/workflows/ci.yml` (ruff, mypy, pytest).
- [ ] Add pre-commit configuration.

### Phase 2 — API & Spatial Layer
- [ ] FastAPI app skeleton with `/health` and `/v1/price` endpoints.
- [ ] H3 service: lat/lng to cell, k-ring neighbors.
- [ ] Redis store for per-cell demand, supply, and price with TTL.

### Phase 3 — Data & Forecasting
- [ ] Select public weather and mobility datasets; write ingestion scripts.
- [ ] Feature engineering (time, rainfall, H3 lag features).
- [ ] Baseline model (XGBoost) with evaluation (MAE, MAPE, pinball loss).
- [ ] Sequence model (LSTM/GRU) and comparison.
- [ ] MLflow tracking and model versioning.

### Phase 4 — Pricing Engine
- [x] Equilibrium solver, spatial smoothing, unit tests (done).
- [ ] Calibrate default elasticity and supply model against real data.
- [ ] Property-based tests (hypothesis) for monotonicity and bounds.

### Phase 5 — Streaming & Workers
- [ ] Kafka topics and producers/consumers.
- [ ] Celery tasks for scheduled forecast and price refresh.

### Phase 6 — Production Readiness
- [ ] Prometheus metrics and Grafana dashboards.
- [ ] Load testing against the p95 < 50 ms target.
- [ ] Kubernetes manifests and release workflow.
- [ ] Fairness and price-cap audit log.

## Quota Log

| Date | Agent | Session usage (% of weekly) | Notes |
|------|-------|-----------------------------|-------|
| 2026-10-19 | Claude | — | Project initialization |

## Security TODO (main machine)

Deferred until the project moves to the main, hardened machine:

- [ ] API authentication and authorization.
- [ ] Rate limiting and HTTPS termination.
- [ ] Secret management (no secrets are stored in this repository).
- [ ] Dependency and container vulnerability scanning in CI.
