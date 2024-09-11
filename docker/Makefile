ECR_AWS_ACCOUNT_ID := $(shell aws sts get-caller-identity --query "Account" --output text)

.DEFAULT_GOAL := help
.PHONY: help docker-ecr-login build-container push-container container-build-push

help:  ## ⁉️   - Display help comments for each make command
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_\-\.]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

docker-ecr-login:
	aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin $(ECR_AWS_ACCOUNT_ID).dkr.ecr.eu-west-2.amazonaws.com

build-container:
	docker build -t ${REPO}:$(TAG) -t $(ECR_AWS_ACCOUNT_ID).dkr.ecr.eu-west-2.amazonaws.com/${REPO}:$(TAG) --target production ../

push-container: docker-ecr-login
	docker push $(ECR_AWS_ACCOUNT_ID).dkr.ecr.eu-west-2.amazonaws.com/${REPO}:$(TAG)

container-build-push: build-container push-container
