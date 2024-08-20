DESIGN_SYSTEM_VERSION=`cat .design-system-version`

.DEFAULT_GOAL := help

.PHONY: help load-design-system-templates lint format format-check test build-docker messages

help:  ## ⁉️   - Display help comments for each make command
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_\-\.]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

load-design-system-templates:  ## 🎨️   - Load the design system templates
	./scripts/load_release.sh onsdigital/design-system $(DESIGN_SYSTEM_VERSION)
	./scripts/finalize_design_system_setup.sh $(DESIGN_SYSTEM_VERSION)

lint: lint-py lint-html  ## 🧹️   - Run Linters

lint-py:  ## 🧹️   - Run Python Linters
	poetry run black --check .
	poetry run ruff check .
	find . -type f -name "*.py" | xargs poetry run pylint --reports=n --output-format=colorized --rcfile=.pylintrc -j 0

lint-html:  ## 🧹️   - Run HTML Linters
	find ons_alpha/ -name '*.html' | xargs poetry run djhtml --check

format: format-py format-html ## 🎨️   - Format the code

format-py:  ## 🎨️   - Format the Python code
	poetry run black .
	poetry run ruff check . --fix

format-html:  ## 🎨️   - Format the HTML code
	find ons_alpha/ -name '*.html' | xargs poetry run djhtml

build-docker:
	docker build -t ons_alpha .

messages:
    python -m manage makemessages --all

compile-messages:
    python -m manage compilemessages --use-fuzzy
