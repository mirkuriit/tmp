#!/usr/bin/make

run:
	poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

lint:
	poetry run ruff check
	
