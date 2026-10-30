# RainSurge AI

Hyper-local dynamic pricing and demand forecasting engine. RainSurge AI predicts demand shocks (such as rainfall-driven surges) per Uber H3 cell using **self-hosted machine learning models** and computes a market-clearing price multiplier.

- No external AI APIs: all models are trained and served locally.
- Stack: FastAPI, Redis (H3), Kafka, Celery, XGBoost/PyTorch.

## Documentation

| File | Purpose |
|------|---------|
| [agents.md](agents.md) | Rules for AI coding agents, quota policy, commands |
| [architecture.md](architecture.md) | System design, tech stack, folder structure, CI/CD |
| [progress.md](progress.md) | Done and planned work |
| [handoff.md](handoff.md) | Fixed issues and open problems |

## References

Background material and inspiration for this project.

| Source | Notes |
|--------|-------|
| [Why is Grab more expensive when it rains? (YouTube, Thai)](https://www.youtube.com/watch?v=rq3fqnYF6F0) | Original title: "ทำไมเรียก Grab ตอนฝนตกถึงแพงกว่าปกติ?" — explains the rain-driven surge pricing behaviour that this engine models: rainfall raises demand, lowers driver supply, and the market-clearing price rises. Starting point for the problem statement and the synthetic demand/supply simulator in `ml/simulation.py`. |

## Status

Project scaffolding only. See [progress.md](progress.md) for the roadmap.

## License

To be decided before the first public release.
