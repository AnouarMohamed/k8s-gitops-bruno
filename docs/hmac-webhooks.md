# Signing Flux v2 Webhook Receivers with Pre-Request Scripts

Flux Notification Controller exposes HTTP webhook endpoints (`/hook/<receiver-hash>`) that trigger immediate reconciliation on `GitRepository`, `OCIRepository`, `Kustomization`, or `HelmRelease` objects. Because these endpoints are frequently exposed behind an Ingress, Flux verifies incoming payloads using shared secrets or HMAC signatures.

## Why Pre-Request Signing Matters in Bruno

When Bruno substitutes `{{variables}}` directly inside `body:json` at send time, calculating an HMAC signature over an uninterpolated template string would produce a digest mismatch against the bytes actually transmitted on the wire.

The Flux webhook requests in `collections/fluxcd-gitops/01-webhook-receivers/` solve this cleanly inside `script:pre-request`:

1. Read `fluxWebhookSecret`, `gitBranch`, and `repoFullName` via `bru.getEnvVar(...)`.
2. Construct the exact JSON string with `JSON.stringify(...)` and bind it to the outgoing request via `req.setBody(rawBody)`.
3. Compute the HMAC-SHA256 hex digest using Node's built-in `crypto` module over the exact UTF-8 bytes of `rawBody`.
4. Populate the signature header variable (`hubSignature256` or `genericHmac`) and a fresh `deliveryUuid` prior to dispatch.

## Supported Receiver Types

### 1. GitHub Receiver (`type: github`)

- **Request**: `01-trigger-github-push-receiver.bru`
- **Headers**:
  - `X-GitHub-Event: push`
  - `X-GitHub-Delivery: <uuid>`
  - `X-Hub-Signature-256: sha256=<hmac-sha256-hex>`
- **Cluster Manifest Example**: See [manifests/flux-webhook-receiver.yaml](../manifests/flux-webhook-receiver.yaml).

### 2. GitLab Receiver (`type: gitlab`)

- **Request**: `02-trigger-gitlab-push-receiver.bru`
- **Headers**:
  - `X-Gitlab-Event: Push Hook`
  - `X-Gitlab-Token: {{fluxWebhookSecret}}`

### 3. Generic HMAC Receiver (`type: generic-hmac`)

- **Request**: `03-trigger-generic-hmac-receiver.bru`
- **Headers**:
  - `X-Signature: sha256=<hmac-sha256-hex>`

### 4. Harbor OCI Receiver (`type: harbor`)

- **Request**: `04-trigger-harbor-oci-webhook.bru`
- **Headers**:
  - `Authorization: Bearer {{fluxWebhookSecret}}`

## Discovering Your Receiver Path ID

Flux computes a deterministic SHA-256 suffix for each `Receiver` resource from its secret token, name, and namespace. Inspect the generated URL path directly from the cluster:

```bash
kubectl -n flux-system get receiver github-gitops-receiver -o jsonpath='{.status.webhookPath}{"\n"}'
```

Copy the hash segment following `/hook/` into the `receiverId` variable in your Bruno environment.
