.PHONY: lint format check

lint:
	poetry run ruff .
	poetry run pylint ons_alpha

format:
	poetry run black .

check: lint format
