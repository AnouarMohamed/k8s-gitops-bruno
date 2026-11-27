# Getting Started with k8s-gitops-bruno

This guide walks through installing Bruno, configuring cluster environments, injecting ephemeral credentials, and executing individual or full-folder API smoke suites against local `kind` / `k3s` clusters or remote environments.

## Prerequisites

- **Bruno Desktop** (v1.30+) or **Node.js 20+** with `@usebruno/cli`
- `kubectl` configured for your target cluster context
- `python3` (3.10+) for running `scripts/validate-collections.py`

## 1. Opening Collections in Bruno Desktop

Each subdirectory under `collections/` is an independent Bruno collection containing its own `bruno.json`, collection-level defaults (`collection.bru`), environment definitions (`environments/*.bru`), and sequenced folders.

1. Launch Bruno Desktop and choose **Open Collection**.
2. Select one of the collection directories:
   - `collections/kubernetes-api`
   - `collections/argocd-gitops`
   - `collections/fluxcd-gitops`
   - `collections/harbor-oci-registry`
   - `collections/observability-platform`
3. In the top-right environment selector, pick the target profile (`local-kind`, `k3s-homelab`, `staging`, or `production-ro`).
4. Open **Configure Environment** and populate the secret fields listed under `vars:secret [...]`. Bruno stores secret values locally outside the repository tree so `git status` remains clean.

## 2. Running Against a Local Cluster via Port-Forwards

When targeting a cluster without external ingress, run the helper script to bind local ports matching the `local-kind` environment URLs:

```bash
chmod +x scripts/*.sh
./scripts/port-forward-all.sh
```

Default port mappings used by `local-kind.bru`:

| Service | Namespace | Local Port | Target Port |
| --- | --- | --- | --- |
| Argo CD Server | `argocd` | `8080` | `443` |
| Flux Notification Receiver | `flux-system` | `9292` | `80` |
| Harbor Portal / Core | `harbor` | `8085` | `80` |
| Prometheus | `monitoring` | `9090` | `9090` |
| Alertmanager | `monitoring` | `9093` | `9093` |
| Grafana | `monitoring` | `3000` | `80` |

## 3. Minting Short-Lived Kubernetes Tokens

Instead of copying long-lived static secrets from `kubeconfig`, apply the least-privilege ServiceAccount manifest and mint a 1-hour bound token:

```bash
kubectl apply -f manifests/bruno-ro-serviceaccount.yaml
./scripts/export-kubeconfig-env.sh kube-system bruno-reader 1h .env
```

The script writes `K8S_API_URL` and `K8S_TOKEN` into an untracked `.env` file with `0600` permissions.

## 4. Executing Suites with the Bruno CLI

Install `@usebruno/cli` once at the repository root:

```bash
npm install
```

Run any collection via `scripts/run-smoke.sh` or the `Makefile`:

```bash
make run-k8s ENV=local-kind
make run-argocd ENV=local-kind
make run-flux ENV=k3s-homelab
```

JSON execution reports are written to `reports/<collection>-<env>.json` (gitignored).

## 5. Handling Self-Signed TLS Certificates

Homelab and `kind` clusters frequently use self-signed or private-CA certificates on `kube-apiserver` (`:6443`) and `argocd-server` (`:8080`).

- **Bruno Desktop**: Navigate to **Preferences -> General -> SSL/TLS Certificate Verification** and either import your cluster CA bundle or disable strict verification exclusively for local development profiles.
- **Bruno CLI**: Pass `--cacert /path/to/cluster-ca.crt` or use `--insecure` only in isolated `local-kind` test runs.
