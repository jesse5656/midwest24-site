.PHONY: up down restart build logs ps shell db psql test migrate revision health

up:
	docker compose up --build -d

down:
	docker compose down

restart:
	docker compose down
	docker compose up --build -d

build:
	docker compose build

logs:
	docker compose logs -f archive-api

ps:
	docker compose ps

shell:
	docker compose exec archive-api bash

db:
	docker compose exec archive-db bash

psql:
	docker compose exec archive-db psql -U archive -d archive

test:
	docker compose exec archive-api pytest -q

migrate:
	docker compose exec archive-api alembic -c alembic.ini upgrade head

revision:
	@read -p "Migration name: " name; \
	docker compose exec archive-api alembic -c alembic.ini revision --autogenerate -m "$$name"

health:
	curl http://localhost:8080/health

worker:
	docker compose exec -e PYTHONPATH=/app archive-api python scripts/run_worker.py
