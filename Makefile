ECR_AWS_ACCOUNT_ID := $(shell aws sts get-caller-identity --query "Account" --output text)
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

build-docker-dev:
	docker build -t ons_alpha .

messages:  ## 🌍   - Make strings available for translation
	poetry run python -m manage makemessages --all

compile-messages:  ## 🌏   - Compile translated messages
	poetry run python -m manage compilemessages --use-fuzzy

docker-ecr-login:
	aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin $(ECR_AWS_ACCOUNT_ID).dkr.ecr.eu-west-2.amazonaws.com

build-container:
	docker build -t ${REPO}:$(TAG) -t $(ECR_AWS_ACCOUNT_ID).dkr.ecr.eu-west-2.amazonaws.com/${REPO}:$(TAG) --target production .

push-container: docker-ecr-login
	docker push $(ECR_AWS_ACCOUNT_ID).dkr.ecr.eu-west-2.amazonaws.com/${REPO}:$(TAG)

container-build-push: build-container push-container
