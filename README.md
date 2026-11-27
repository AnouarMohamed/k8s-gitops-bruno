# k8s-gitops-bruno

A Git-native [Bruno](https://www.usebruno.com/) API collection repository engineered for **Kubernetes**, **GitOps** (Argo CD and Flux v2), **OCI Supply Chain Security** (Harbor, Trivy, Cosign), and **Cluster Observability** (Prometheus, Alertmanager, Grafana).

Every request, environment template, pre-request signing script, and post-response assertion is stored in Bruno's plain-text `.bru` DSL so API workflows can be reviewed in pull requests, linted in CI, versioned alongside cluster manifests, and executed headlessly with `@usebruno/cli`.

## Why Bruno for Kubernetes and GitOps

Traditional API clients store collections in opaque cloud workspaces or monolithic JSON blobs that produce noisy diffs and tempt teams into syncing tokens to third-party servers. For Kubernetes and GitOps platform engineering, plain-text `.bru` collections solve three practical problems:

1. **Zero-Trust Credential Separation**: Sensitive values (`k8sToken`, `argocdToken`, `fluxWebhookSecret`, `harborPassword`, `grafanaToken`) are declared in `vars:secret [...]` blocks and never serialized into tracked files.
2. **Repeatable Pre-Request Cryptography**: Flux webhook receivers require exact-byte HMAC-SHA256 signatures (`X-Hub-Signature-256` or `X-Signature`). Bruno executes standard Node.js `crypto` inside `script:pre-request`, computing valid signatures dynamically at send time.
3. **CI-Ready Smoke Testing**: Collections run identically in Bruno Desktop for interactive debugging and under `bru run` inside GitHub Actions or post-deploy verification jobs.

## Collections Overview

| Collection | Path | Request Groups | Authentication |
| --- | --- | --- | --- |
| **Kubernetes API** | [collections/kubernetes-api](collections/kubernetes-api) | Cluster Health, Workloads, Networking and Storage, RBAC and Security, GitOps and Platform CRDs | Kubernetes Bearer Token (`ServiceAccount` / OIDC) |
| **Argo CD GitOps** | [collections/argocd-gitops](collections/argocd-gitops) | Auth and Session, Applications, ApplicationSets and Projects, Repositories and Clusters | Session JWT or Account API Token |
| **Flux v2 GitOps** | [collections/fluxcd-gitops](collections/fluxcd-gitops) | Webhook Receivers (HMAC-SHA256), Flux CRDs via Kubernetes API, Controller Metrics | HMAC / Shared Token and Kubernetes Bearer |
| **Harbor OCI Registry** | [collections/harbor-oci-registry](collections/harbor-oci-registry) | System Health, Projects and OCI Artifacts (Trivy/Cosign), Replication and Webhooks | HTTP Basic / Harbor Robot Account |
| **Observability Platform** | [collections/observability-platform](collections/observability-platform) | Prometheus PromQL Queries, Alertmanager Silences, Grafana Dashboards and Annotations | Unauthenticated / Bearer Token |

### Detailed Endpoint Coverage

#### 1. Kubernetes API (`collections/kubernetes-api`)

- **01 Cluster Health**: `/livez`, `/readyz`, `/version`, `/apis` discovery, and node readiness listing.
- **02 Workloads**: Namespace listing, pod listing with dynamic `podName` capture, trailing pod log retrieval, deployment listing, `/scale` subresource merge-patch, strategic-merge rollout restart (`kubectl.kubernetes.io/restartedAt`), and Pod Security Standards (`restricted`) ephemeral smoke Jobs.
- **03 Networking and Storage**: Services, `discovery.k8s.io/v1` EndpointSlices, Ingresses, NetworkPolicies, and PersistentVolumeClaims.
- **04 RBAC and Security**: `SelfSubjectAccessReview`, `SelfSubjectRulesReview`, ServiceAccounts, bound `TokenRequest` minting, and `wgpolicyk8s.io/v1alpha2` Kyverno PolicyReports.
- **05 GitOps and Platform CRDs**: Direct `kube-apiserver` queries for Argo CD `Application`, Flux `Kustomization` and `HelmRelease`, and `cert-manager.io/v1` `Certificate` resources.

#### 2. Argo CD GitOps (`collections/argocd-gitops`)

- **01 Auth and Session**: Session JWT exchange (`/api/v1/session` with automatic `argocdToken` persistence), `userinfo`, `/api/version`, and `/api/v1/settings`.
- **02 Applications**: Filtered application listing, status/history inspection (capturing latest `revisionId`), application upsert with automated prune and Server-Side Apply, manual sync trigger, hard manifest cache refresh (`?refresh=hard`), managed resource live/target state diffs, resource topology tree, history rollback, and cascade deletion.
- **03 ApplicationSets and Projects**: ApplicationSet inspection, AppProject policy auditing, and project-scoped audit events.
- **04 Repositories and Clusters**: Git/OCI repository status, `repo-server` connectivity validation, registered target clusters, and GPG commit-verification keys.

#### 3. Flux v2 GitOps (`collections/fluxcd-gitops`)

- **01 Webhook Receivers**: GitHub push (`X-Hub-Signature-256`), GitLab push (`X-Gitlab-Token`), generic HMAC (`X-Signature`), and Harbor `PUSH_ARTIFACT` OCI webhook triggers.
- **02 Flux CRDs via Kubernetes API**: `GitRepository`, `OCIRepository`, `Kustomization`, immediate reconcile annotation (`reconcile.fluxcd.io/requestedAt`), and `HelmRelease` suspend/resume patches.
- **03 Flux Controller Metrics**: Direct Prometheus `/metrics` scrape checks for `source-controller`, `kustomize-controller`, and `helm-controller` (`gotk_reconcile_condition` and `gotk_reconcile_duration_seconds`).

#### 4. Harbor OCI Registry (`collections/harbor-oci-registry`)

- **01 System Health**: `/ping`, component `/health`, `/systeminfo`, and storage/project `/statistics`.
- **02 Projects and OCI Artifacts**: Project listing, hardened project creation (`prevent_vul`, `auto_scan`, `enable_content_trust_cosign`), repository browsing, artifact listing with scan/accessory expansion, Trivy vulnerability reports, on-demand scan queueing, and Cosign signature accessory verification.
- **03 Replication and Webhooks**: Replication policy listing, manual replication execution, and project webhook policies.

#### 5. Observability Platform (`collections/observability-platform`)

- **01 Prometheus**: `/-/healthy`, `/-/ready`, PromQL checks for `argocd_app_info`, failing `gotk_reconcile_condition`, container restarts over 1h, firing/pending alerts, and active scrape targets.
- **02 Alertmanager**: Cluster peer status, active unsilenced alerts, 30-minute maintenance silence creation (capturing `silenceId`), and silence expiration.
- **03 Grafana**: `/api/health`, provisioned dashboard search, datasource verification, and automated GitOps deployment marker annotations.

## Repository Layout

```text
.
├── .github/
│   ├── ISSUE_TEMPLATE/new-endpoint.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── workflows/validate.yml
│   ├── CODEOWNERS
│   └── dependabot.yml
├── collections/
│   ├── kubernetes-api/
│   ├── argocd-gitops/
│   ├── fluxcd-gitops/
│   ├── harbor-oci-registry/
│   └── observability-platform/
├── docs/
│   ├── architecture.md
│   ├── getting-started.md
│   ├── hmac-webhooks.md
│   └── rbac-least-privilege.md
├── manifests/
│   ├── bruno-ro-serviceaccount.yaml
│   └── flux-webhook-receiver.yaml
├── scripts/
│   ├── export-kubeconfig-env.sh
│   ├── port-forward-all.sh
│   ├── run-smoke.sh
│   └── validate-collections.py
├── .editorconfig
├── .env.example
├── .gitleaks.toml
├── .gitignore
├── .markdownlint-cli2.yaml
├── .pre-commit-config.yaml
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── Makefile
├── README.md
└── package.json
```

## Quick Start

### 1. Clone and Validate

```bash
git clone https://github.com/AnouarMohamed/k8s-gitops-bruno.git
cd k8s-gitops-bruno
make validate
```

### 2. Provision Least-Privilege Cluster Access

Apply the read-only GitOps ServiceAccount and mint a short-lived bound token (1 hour):

```bash
kubectl apply -f manifests/bruno-ro-serviceaccount.yaml
./scripts/export-kubeconfig-env.sh kube-system bruno-reader 1h .env
```

### 3. Port-Forward Local Services

For `local-kind` environments, bind local ports for Argo CD, Flux receiver, Harbor, Prometheus, Alertmanager, and Grafana:

```bash
./scripts/port-forward-all.sh
```

### 4. Execute Collections via CLI or Bruno Desktop

Install the Bruno CLI locally:

```bash
npm install
```

Run any collection headlessly:

```bash
make run-k8s ENV=local-kind
make run-argocd ENV=local-kind
make run-flux ENV=local-kind
make run-harbor ENV=local-kind
make run-obs ENV=local-kind
```

Or open any directory under `collections/` directly in **Bruno Desktop** and select one of the four standardized environments (`local-kind`, `k3s-homelab`, `staging`, `production-ro`).

## Documentation Index

- [Getting Started](docs/getting-started.md) — Desktop and CLI setup, port-forwarding, token minting, and self-signed TLS guidance.
- [Architecture and Conventions](docs/architecture.md) — Collection layout, chained variable flows, environment parity, and quality gates.
- [Least-Privilege RBAC Model](docs/rbac-least-privilege.md) — Read-only baseline permissions, mutating endpoint matrix, and Argo CD RBAC policy alignment.
- [Signing Flux Webhooks](docs/hmac-webhooks.md) — How pre-request Node `crypto` scripts compute `X-Hub-Signature-256` and `X-Signature` headers.
- [Contributing Guide](CONTRIBUTING.md) — Request formatting rules, sequencing invariants, and PR validation checklist.
- [Security Policy](SECURITY.md) — Secret handling and reporting guidelines.

## License

Released under the [MIT License](LICENSE).
