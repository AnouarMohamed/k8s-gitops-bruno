# Security Policy

## Credential Hygiene

This repository stores API request definitions and non-sensitive environment templates only.

- **Do not** commit Kubernetes ServiceAccount tokens, client certificates, private keys, Argo CD JWTs, Harbor robot secrets, or Flux HMAC keys.
- All sensitive variables belong in `vars:secret [...]` blocks in `environments/*.bru` or an untracked `.env` file.
- Production environments (`production-ro`) should only be used with read-only credentials (`get`, `list`, `watch`). See [docs/rbac-least-privilege.md](docs/rbac-least-privilege.md).

## Reporting a Vulnerability

If you discover an accidentally committed secret or unsafe script/manifest in this repository, please open a private security advisory on GitHub or contact the maintainer directly.
