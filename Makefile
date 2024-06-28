.PHONY: lint lint-fix format format-check test build-docker

lint:
	poetry run ruff check .

lint-fix:
	poetry run ruff check . --fix

format:
	poetry run black .

format-check:
	poetry run black --check .

test:
	export DJANGO_SETTINGS_MODULE=ons_alpha.settings.test_settings && poetry run python manage.py collectstatic --noinput && poetry run pytest

build-docker:
	docker build -t ons_alpha .
