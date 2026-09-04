#!/usr/bin/make
# === Alembic ===
new-migration:
	poetry run alembic revision --autogenerate -m $(name)

upgrade-head:
	poetry run alembic upgrade head

run-app:
	upgrade-head
	poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

lint:
	poetry run ruff check

up:
	docker compose up --build

