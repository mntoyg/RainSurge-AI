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
- [x] Initialized a standalone Git repository inside the project folder.

## What we plan to do next

### Phase 1 — Foundations
- [ ] Add `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `.env.example`.
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
- [ ] Implement equilibrium solver with elasticity, bounds, and smoothing.
- [ ] Spatial smoothing across neighboring cells.
- [ ] Unit tests and property-based tests for monotonicity and bounds.

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
