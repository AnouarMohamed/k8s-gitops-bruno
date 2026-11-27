# Changelog

All notable additions and updates to `k8s-gitops-bruno` are documented here.

## [1.0.0] - 2026-11-27

### Added
- `kubernetes-api` collection: cluster probes (`/livez`, `/readyz`), workloads, rollout restart strategic patch, RBAC `SelfSubjectAccessReview` & `TokenRequest`, NetworkPolicies, Kyverno PolicyReports, and GitOps CRDs.
- `argocd-gitops` collection: session auth, Application lifecycle (create, sync, hard-refresh, resource tree, rollback, delete), ApplicationSets, Projects, Repositories, and Clusters.
- `fluxcd-gitops` collection: GitHub/GitLab/Generic HMAC-SHA256 webhook triggers with pre-request Node `crypto` signing, Flux CRD inspection/reconciliation, and controller Prometheus metrics.
- `harbor-oci-registry` collection: system health, project/repository browsing, Trivy vulnerability scans, Cosign signature accessory checks, and replication policies.
- `observability-platform` collection: Prometheus PromQL GitOps health queries, Alertmanager silences, and Grafana deploy annotations.
- Repository validation (`scripts/validate-collections.py`), kubeconfig env exporter, port-forward helper, least-privilege RBAC manifest, and GitHub Actions CI.
