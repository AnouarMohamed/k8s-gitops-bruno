# Collection Architecture and Design Conventions

This repository models the API control plane of a modern Kubernetes and GitOps platform as five decoupled, composable Bruno collections.

## Design Principles

1. **Git-Native Plain Text**: Every collection uses Bruno's `.bru` DSL so diffs remain human-readable during code review. No proprietary JSON exports or workspace state files are committed.
2. **Environment Parity**: Every collection implements the exact same four environment profiles (`local-kind`, `k3s-homelab`, `staging`, `production-ro`) to make switching cluster targets predictable.
3. **Zero Committed Secrets**: Credential variables (`k8sToken`, `argocdPassword`, `argocdToken`, `fluxWebhookSecret`, `harborPassword`, `grafanaToken`, `prometheusToken`) are declared strictly inside `vars:secret [...]`.
4. **Chained Operational Flows**: Where endpoints form a natural workflow, `script:post-response` persists state into runtime variables:
   - `argocd-gitops`: `01-create-session.bru` captures `argocdToken`; `02-get-application.bru` captures the latest `revisionId` for rollback testing.
   - `kubernetes-api`: `02-list-pods.bru` captures `podName` for `03-get-pod-logs.bru`.
   - `observability-platform`: `03-create-silence.bru` captures `silenceId` for `04-delete-silence.bru`.
5. **Defensive Assertions**: Every `.bru` file includes a `tests { ... }` block validating HTTP status codes and expected Kubernetes/GitOps response fields (`kind`, `status`, `metadata`, `items`).

## Repository Quality Gates

The Python validator at [scripts/validate-collections.py](../scripts/validate-collections.py) enforces structural invariants across every commit:

- Valid `bruno.json` (`version: "1"`, `type: "collection"`).
- Presence of all four standardized environments per collection.
- Balanced block braces across all `.bru` files.
- Presence of `meta`, HTTP method, `tests`, and `docs` blocks on every request.
- Contiguous `seq` numbering matching folder and request ordering (`1..N`).
- Pattern-based secret scanning complementing `gitleaks`.
