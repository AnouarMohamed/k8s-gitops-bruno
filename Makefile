SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help

ENV ?= local-kind
REPORT_DIR ?= reports

.PHONY: help validate lint run-k8s run-argocd run-flux run-harbor run-obs port-forward clean

help: ## Show available targets
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

validate: ## Validate Bruno collections, metadata, sequences, and secret hygiene
	python3 scripts/validate-collections.py

lint: validate ## Run repository linters (collections + markdown if available)
	@if command -v markdownlint-cli2 >/dev/null 2>&1; then \
		markdownlint-cli2 "**/*.md" "#node_modules"; \
	fi

run-k8s: ## Run Kubernetes API Bruno collection (ENV=local-kind)
	./scripts/run-smoke.sh kubernetes-api $(ENV)

run-argocd: ## Run Argo CD GitOps Bruno collection (ENV=local-kind)
	./scripts/run-smoke.sh argocd-gitops $(ENV)

run-flux: ## Run Flux v2 GitOps Bruno collection (ENV=local-kind)
	./scripts/run-smoke.sh fluxcd-gitops $(ENV)

run-harbor: ## Run Harbor OCI Registry Bruno collection (ENV=local-kind)
	./scripts/run-smoke.sh harbor-oci-registry $(ENV)

run-obs: ## Run Observability Platform Bruno collection (ENV=local-kind)
	./scripts/run-smoke.sh observability-platform $(ENV)

port-forward: ## Start local port-forwards for kind/homelab services
	./scripts/port-forward-all.sh

clean: ## Remove generated test reports and temp files
	rm -rf $(REPORT_DIR)/*.json $(REPORT_DIR)/*.xml $(REPORT_DIR)/*.html
