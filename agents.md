# agents.md — AI Agent Guidelines for RainSurge AI

This document defines how AI coding agents (Claude, Codex, and any other assistant) must operate in this repository.

## 1. Project Context

RainSurge AI is a **Hyper-Local Dynamic Pricing & Demand Forecasting Engine**. It forecasts hyper-local demand shocks (for example, rainfall-driven spikes in ride, delivery, and umbrella/food demand) and computes a market-clearing dynamic price per H3 hexagonal cell.

## 2. Usage Quota Policy (Mandatory)

| Agent  | Limit for this project                    |
|--------|-------------------------------------------|
| Claude | **14% of weekly usage quota per day**     |
| Codex  | **14% of weekly usage quota per day**     |

Rules:

1. Each agent must not consume more than **14% of its weekly usage allowance in any single calendar day** while working on this project (14% x 7 days = 98%, leaving a 2% safety margin).
2. Track consumption at the start and end of every session. Record a one-line entry in `progress.md` under "Quota Log" when a session consumes more than 5%.
3. When the daily budget is reached, **stop**, write the current state to `handoff.md`, and wait for the next day.
4. Prefer cheap operations: read only the files you need, avoid repeated full-repo scans, batch independent tool calls, and do not spawn sub-agents for trivial work.
5. Never start long-running generation or large refactors in the last 20% of the daily budget.

## 3. Hard Constraints

1. **No external AI APIs.** Do not call or add OpenAI, Anthropic, Gemini, Cohere, Mistral-hosted, or any other third-party hosted AI/LLM API. Do not add their SDKs to dependencies.
2. **Self-hosted models only.** All forecasting is done by models we train and serve ourselves (XGBoost, LightGBM, LSTM/GRU/TCN in PyTorch, or custom time-series models).
3. **No secrets in Git.** Never commit API keys, tokens, credentials, or `.env` files. Use `.env.example` with placeholder values.
4. **Public-repo ready.** Every change must be safe to push to a public GitHub repository: no private data, no personal paths, no proprietary datasets, no large binaries (use `.gitignore` and DVC/object storage for data and model artifacts).
5. **English only in code and docs.** Code, comments, commit messages, and Markdown files are written in professional English.

## 4. Boundaries

### Allowed
- Edit files under `api/`, `ml/`, `pricing/`, `workers/`, `infra/`, `docs/`, `scripts/`, `.github/`.
- Add tests and documentation for any change.
- Add dependencies that are open source and necessary (update the relevant `requirements*.txt` / `pyproject.toml`).

### Ask first
- Changing the public API contract (`api/app/schemas/`).
- Changing the pricing equilibrium formula or its constraints.
- Adding a new infrastructure component (new database, queue, or cloud service).
- Deleting or rewriting files in bulk.

### Never
- Force-push, rewrite published Git history, or push directly to `main`.
- Commit datasets, trained model binaries (`*.pkl`, `*.pt`, `*.onnx`, `*.joblib`), or `.env` files.
- Disable tests, linters, or CI checks to make a build pass.
- Call external paid or hosted AI services.

## 5. Workflow Expectations

1. Read `architecture.md`, `progress.md`, and `handoff.md` before starting work.
2. Work on a feature branch (`feat/...`, `fix/...`, `docs/...`, `chore/...`).
3. Write or update tests first for new behavior (test-driven where practical).
4. Run the checks in Section 6 before every commit.
5. Use Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:`).
6. After each meaningful change, update `progress.md`; log bugs and blockers in `handoff.md`.
7. Open a Pull Request for every merge into `main`.

## 6. Commands

```bash
# Environment
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

# Infrastructure (Redis, Kafka, Zookeeper, API, worker)
docker compose -f infra/docker/docker-compose.yml up -d
docker compose -f infra/docker/docker-compose.yml down

# Run API locally
uvicorn api.app.main:app --reload --port 8000

# Run Celery worker
celery -A workers.celery_app worker --loglevel=info

# Tests
pytest                       # entire suite
pytest api/tests             # API only
pytest ml/tests              # ML only
pytest pricing/tests         # pricing engine only

# Lint, format, type-check
ruff check .
ruff format --check .
mypy api ml pricing workers

# Train a model locally
python -m ml.training.train --config ml/training/config.yaml
```

## 7. Definition of Done

- Tests pass locally and in CI.
- Lint, format, and type checks pass.
- Docs (`architecture.md`, `progress.md`, `handoff.md`) are updated where relevant.
- No secrets, data files, or model binaries in the diff.
- The change is committed with a Conventional Commit message and is ready to push.
