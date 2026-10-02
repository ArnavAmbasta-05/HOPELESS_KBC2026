# KoreX -- KIIT EventOps AI Command Center

An AI-powered event digital twin, operational command center, simulation and adaptive-response platform for KIIT university events.

KoreX detects disruptions (venue outages, weather hazards, transport delays, crowd surges), computes blast-radius impact across the dependency graph, simulates what-if branches, generates AI-explained proposals, routes them through human approval, and executes idempotent corrective actions with cohort-targeted notifications.

## Repository layout

```
apps/web/             React/Vite command-center frontend
services/api/         FastAPI backend
services/workers/     Celery background workers
packages/domain/      SQLAlchemy domain models (shared)
packages/contracts/   Pydantic schemas and contracts (shared)
ai/graphs/            LangGraph AI orchestration graphs
integrations/         External adapters (Notion, weather, transport, etc.)
infra/                Docker Compose, Dockerfiles, k8s stubs
tests/                Test suite (unit, integration, e2e, fixtures)
docs/                 Architecture and operational documentation
agents/               Agent jurisdiction contracts
```

## Prerequisites

- Python 3.12+
- Node.js 20+ and npm
- Docker and Docker Compose
- Git

## Getting started

### 1. Clone and configure environment

```bash
git clone <repo-url> && cd KBC_PROJECT
cp .env.example .env
# Edit .env with your credentials (never commit .env)
```

### 2. Python setup

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
pre-commit install
```

### 3. Frontend setup

```bash
cd apps/web
npm install
npm run dev
```

### 4. Run services with Docker Compose

```bash
docker compose up -d
```

### 5. Run tests

```bash
pytest                          # all tests
pytest -m unit                  # unit tests only
pytest -m integration           # integration tests only
pytest --cov                    # with coverage report
```

### 6. Linting and type checking

```bash
ruff check .                    # lint
ruff format --check .           # format check
mypy .                          # type check
```

## Architecture

See `docs/` for detailed architecture documentation. The system follows the core loop:

```
detect -> impact (blast radius) -> simulate (branch) -> explain (AI) ->
approve (human) -> execute (idempotent) -> notify (cohort) -> monitor (reconcile)
```

## License

MIT
