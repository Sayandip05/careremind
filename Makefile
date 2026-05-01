.PHONY: dev dev-api dev-worker test migrate logs build clean

# ── Development ───────────────────────────────────────────────
dev:
	docker-compose up api worker

dev-api:
	docker-compose up api

dev-worker:
	docker-compose up worker

# ── Database ──────────────────────────────────────────────────
migrate:
	docker-compose exec api alembic upgrade head

migrate-local:
	cd services/fastapi && venv/Scripts/alembic upgrade head

# ── Testing ───────────────────────────────────────────────────
test:
	docker-compose exec api pytest

test-local:
	cd services/fastapi && venv/Scripts/pytest

# ── Operations ────────────────────────────────────────────────
logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f api

logs-worker:
	docker-compose logs -f worker

build:
	docker-compose build

clean:
	docker-compose down -v
