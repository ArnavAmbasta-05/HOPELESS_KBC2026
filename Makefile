# KoreX — Development Makefile
# All Docker commands use the Compose file in infra/

COMPOSE := docker compose -f infra/docker-compose.yml

.PHONY: up down restart logs ps db-shell redis-shell test lint fmt seed help

## ---- Docker Compose ----

up: ## Start all services in detached mode
	$(COMPOSE) up -d --build

down: ## Stop and remove all containers
	$(COMPOSE) down

restart: down up ## Restart all services

logs: ## Follow logs from all services
	$(COMPOSE) logs -f

ps: ## Show running service status
	$(COMPOSE) ps

## ---- Database / Redis shells ----

db-shell: ## Open psql shell in the postgres container
	$(COMPOSE) exec postgres psql -U korex -d korex

redis-shell: ## Open redis-cli in the redis container
	$(COMPOSE) exec redis redis-cli

## ---- Python tooling ----

test: ## Run pytest
	$(COMPOSE) exec api python -m pytest tests/ -ra --strict-markers

lint: ## Run ruff check + mypy
	$(COMPOSE) exec api python -m ruff check .
	$(COMPOSE) exec api python -m mypy services/ packages/

fmt: ## Run ruff format
	$(COMPOSE) exec api python -m ruff format .

## ---- Data ----

seed: ## Verify and load golden scenario seed data
	$(COMPOSE) exec api python -c "from packages.domain.seed import load_golden_seed; s = load_golden_seed(); print(f'Seeded {len(s.venues)} venues, {len(s.sessions)} sessions, {len(s.volunteers)} volunteers for {s.event_id}')"

## ---- Help ----

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'
