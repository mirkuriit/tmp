#!/usr/bin/make

run-app:
	poetry run alembic upgrade head
	poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

lint:
	poetry run ruff check
	
new-migration:
	poetry run alembic revision --autogenerate -m $(name)

up:
	poetry run docker compose up --build

