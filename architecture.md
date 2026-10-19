# architecture.md — System & Tech Architecture

## 1. Overview

RainSurge AI forecasts hyper-local demand (driven by weather, especially rainfall) and converts forecasts into dynamic prices per spatial cell. All AI components are **self-trained and self-hosted**; no external AI API is used.

## 2. High-Level Data Flow

```
Client Apps (mobile / web / partner systems)
        |
        v
FastAPI Gateway  ---------------------------+
        |                                    |
        v                                    | (read price)
Redis  (Uber H3 spatial index, hot cache)    |
        |                                    |
        v                                    |
Kafka (event stream)  -->  Celery Workers    |
        |                                    |
        v                                    |
Local AI Forecasting Model (XGBoost / LSTM)  |
        |                                    |
        v                                    |
Dynamic Pricing Equilibrium Engine ----------+
        |
        v
Redis (updated price per H3 cell)
```

### Component responsibilities

| Stage | Component | Responsibility |
|-------|-----------|----------------|
| 1 | Client Apps | Request prices, submit demand/supply events, receive surge updates |
| 2 | FastAPI Gateway | AuthN/Z, validation, rate limiting, price lookup, event ingestion |
| 3 | Redis + Uber H3 | Convert lat/lng to H3 cell (resolution 8 by default); store per-cell demand, supply, weather features, and current price with TTL |
| 4 | Kafka / Celery | Kafka carries raw events (orders, weather ticks); Celery workers run batch feature building, scheduled forecasts, and price refresh |
| 5 | Local AI Forecasting Model | Predicts demand per H3 cell for horizons of 15/30/60 minutes using self-trained models |
| 6 | Dynamic Pricing Equilibrium | Finds the multiplier that clears forecast demand against available supply within configured bounds |

## 3. Dynamic Pricing Equilibrium

For each H3 cell `c` and horizon `t`:

- `D(c,t)` = forecast demand from the local model
- `S(c,t)` = current/expected supply
- Price multiplier `m` is solved so that `D(c,t) * f(m) ≈ S(c,t)`, where `f(m)` is a demand-elasticity response (default: constant elasticity `m^-e`).
- Constraints: `m_min <= m <= m_max`, smoothing against the previous multiplier (`|m_t - m_{t-1}| <= delta`) and spatial smoothing across neighboring H3 cells (k-ring averaging) to avoid price cliffs at cell borders.
- Fairness guardrails: hard cap, cooldown, and an audit log of every price decision.

## 4. Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ (3.11+ preferred) |
| API | FastAPI, Uvicorn, Pydantic v2 |
| Spatial indexing | Uber H3 (`h3` Python library) |
| Cache / state | Redis 7 |
| Streaming | Apache Kafka (with `aiokafka` / `confluent-kafka`) |
| Async jobs | Celery (Redis as broker/result backend) |
| ML (self-hosted) | XGBoost, LightGBM, PyTorch (LSTM/GRU/TCN), scikit-learn, pandas, NumPy |
| Experiment tracking | MLflow (self-hosted, local file or Docker) |
| Model serving | In-process loading via ONNX Runtime / native format behind the worker and a `ml/serving` module |
| Persistence | PostgreSQL (price audit log, model registry metadata) — planned |
| Containers | Docker, Docker Compose; Kubernetes manifests in `infra/k8s` |
| Observability | Prometheus metrics, structured JSON logging, Grafana dashboards — planned |
| Quality | pytest, ruff, mypy, pre-commit |
| CI/CD | GitHub Actions |

### AI / ML policy
- Models are trained on data we own or public datasets (e.g., public weather and mobility data).
- Models are stored as versioned artifacts outside Git (MLflow artifact store / object storage).
- **No call to OpenAI, Anthropic, Gemini, or any hosted AI API.**

## 5. Folder Structure

```
RainSurge AI/
├── agents.md                  # AI agent rules and quota policy
├── architecture.md            # This document
├── progress.md                # Task tracking
├── handoff.md                 # Knowledge transfer and issue log
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── .github/
│   └── workflows/
│       └── ci.yml             # Lint, type-check, test, Docker build
├── api/                       # FastAPI gateway
│   ├── app/
│   │   ├── main.py
│   │   ├── core/              # config, logging, security
│   │   ├── routers/           # prices, events, health
│   │   ├── schemas/           # Pydantic request/response models
│   │   └── services/          # H3 + Redis access, pricing facade
│   └── tests/
├── ml/                        # Self-hosted forecasting
│   ├── data/{raw,processed}/  # Git-ignored (kept via .gitkeep)
│   ├── features/              # Feature engineering (weather, time, H3 lags)
│   ├── models/                # Model definitions (XGBoost, LSTM)
│   ├── training/              # Training scripts and configs
│   ├── serving/               # Inference wrapper used by workers
│   ├── notebooks/             # Exploration only
│   └── tests/
├── pricing/                   # Equilibrium engine (pure Python, no I/O)
│   └── tests/
├── workers/                   # Celery app and tasks; Kafka consumers
│   └── tasks/
├── infra/
│   ├── docker/                # Dockerfiles, docker-compose.yml
│   ├── k8s/                   # Kubernetes manifests
│   └── kafka/                 # Topic definitions
├── docs/                      # Extra documentation, ADRs
└── scripts/                   # Dev helper scripts (seed data, simulators)
```

## 6. Kafka Topics (planned)

| Topic | Producer | Consumer | Payload |
|-------|----------|----------|---------|
| `events.orders` | API | Celery/feature builder | order requests per H3 cell |
| `events.weather` | weather ingestor | feature builder | rainfall, temperature, wind per cell |
| `forecasts.demand` | forecast worker | pricing worker | demand forecast per cell/horizon |
| `prices.updates` | pricing worker | cache updater / clients | new multiplier per cell |

## 7. CI/CD Pipeline

```
Push / Pull Request
      |
      v
GitHub Actions (.github/workflows/ci.yml)
  1. Checkout + set up Python 3.11 (pip cache)
  2. Install requirements-dev.txt
  3. ruff check + ruff format --check
  4. mypy
  5. pytest with coverage (Redis service container)
  6. Docker build (no push) for API and worker images
      |
      v
Merge to main (requires green checks + review)
      |
      v
Tag vX.Y.Z  ->  Release workflow (planned)
  - Build and push images to GitHub Container Registry
  - Publish release notes
  - Deploy to staging via Kubernetes manifests (planned)
```

Model training runs **outside** CI (local or self-hosted runner); CI only validates code and runs small deterministic model smoke tests.

## 8. How to Run

```bash
# 1. Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env

# 2. Start infrastructure
docker compose -f infra/docker/docker-compose.yml up -d

# 3. Run API and worker
uvicorn api.app.main:app --reload --port 8000
celery -A workers.celery_app worker --loglevel=info

# 4. Train the local model
python -m ml.training.train --config ml/training/config.yaml

# 5. Test
pytest
```

> Note: only `pricing/` and `ml/simulation.py` are implemented so far (see `progress.md`); the API and worker commands above describe the target workflow. Currently working: `pytest`, `python scripts/simulate_data.py`, `python scripts/demo_pricing.py` (run with `PYTHONPATH=.`).

## 9. Non-Functional Targets

- Price lookup p95 latency < 50 ms (Redis hit).
- Forecast refresh every 5 minutes per active H3 cell.
- Horizontal scaling: stateless API pods; workers scale by Kafka partition count.
- Graceful degradation: if the forecast is stale, serve the last price within TTL and fall back to multiplier 1.0 after expiry.
