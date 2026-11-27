# Least-Privilege RBAC Model for Bruno API Collections

Connecting an interactive HTTP client directly to `kube-apiserver` carries operational risk if backed by `cluster-admin` credentials. This repository separates read-only inspection workflows from mutating operational requests and documents the exact Kubernetes RBAC verbs required for each group.

## Recommended Baseline: Read-Only GitOps Auditor

Apply [manifests/bruno-ro-serviceaccount.yaml](../manifests/bruno-ro-serviceaccount.yaml) to create `kube-system/bruno-reader` bound to `ClusterRole/bruno-gitops-reader`.

Permissions granted by `bruno-gitops-reader`:

- **Core read**: `get`, `list` on `namespaces`, `nodes`, `pods`, `pods/log`, `services`, `serviceaccounts`, `persistentvolumeclaims`
- **Workloads read**: `get`, `list` on `apps` (`deployments`, `replicasets`, `statefulsets`, `daemonsets`)
- **Discovery & Networking read**: `get`, `list` on `endpointslices`, `ingresses`, `networkpolicies`
- **Authorization self-inspection**: `create` on `selfsubjectaccessreviews` and `selfsubjectrulesreviews` (never grants access to other identities)
- **GitOps & Platform CRDs read**: `get`, `list` on `argoproj.io` (`applications`, `applicationsets`, `appprojects`), Flux `*.toolkit.fluxcd.io` (`gitrepositories`, `ocirepositories`, `kustomizations`, `helmreleases`), `cert-manager.io` (`certificates`, `certificaterequests`), and `wgpolicyk8s.io` (`policyreports`, `clusterpolicyreports`)

Notice what is intentionally excluded:

- **Secrets**: `bruno-gitops-reader` cannot read `Secret` objects anywhere in the cluster.
- **Exec / Port-Forward**: `pods/exec`, `pods/attach`, and `pods/portforward` are omitted.
- **Mutating verbs**: `create`, `update`, `patch`, and `delete` are omitted except for `SelfSubject*Review`.

## Opt-In Permissions for Mutating Requests

Specific requests in `kubernetes-api` and `fluxcd-gitops` perform mutations intended for non-production or break-glass troubleshooting:

| Request File | Target Resource | Required Verb | Namespace Scope |
| --- | --- | --- | --- |
| `02-workloads/05-scale-deployment.bru` | `apps/deployments/scale` | `patch` | Target app namespace |
| `02-workloads/06-rollout-restart-patch.bru` | `apps/deployments` | `patch` | Target app namespace |
| `02-workloads/07-create-ephemeral-job.bru` | `batch/jobs` | `create` | Target app namespace |
| `04-rbac-security/04-create-token-request.bru` | `serviceaccounts/token` | `create` | Target SA namespace |
| `02-k8s-flux-crds/04-annotate-reconcile-kustomization.bru` | `kustomize.toolkit.fluxcd.io/kustomizations` | `patch` | `flux-system` |
| `02-k8s-flux-crds/05-suspend-helmrelease.bru` | `helm.toolkit.fluxcd.io/helmreleases` | `patch` | `flux-system` |
| `02-k8s-flux-crds/06-resume-helmrelease.bru` | `helm.toolkit.fluxcd.io/helmreleases` | `patch` | `flux-system` |

When granting these permissions in `staging`, use a namespace-scoped `Role` and `RoleBinding` rather than a `ClusterRoleBinding`, and mint short-lived tokens (`--duration=15m` or `1h`) via the Kubernetes `TokenRequest` API.

## Argo CD RBAC Alignment

For `production-ro`, configure an Argo CD project or global policy (`argocd-rbac-cm`) granting only `get` actions:

```csv
p, role:bruno-ro, applications, get, */*, allow
p, role:bruno-ro, applicationsets, get, */*, allow
p, role:bruno-ro, projects, get, *, allow
p, role:bruno-ro, repositories, get, *, allow
p, role:bruno-ro, clusters, get, *, allow
p, role:bruno-ro, gpgkeys, get, *, allow
```
