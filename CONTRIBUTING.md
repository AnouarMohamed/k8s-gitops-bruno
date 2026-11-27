# Contributing to k8s-gitops-bruno

Thank you for contributing! Every request in this repository is plain-text `.bru` and reviewed like code.

## Adding or Updating Requests

1. Place new `.bru` files inside the matching collection under `collections/<collection>/<folder>/`.
2. Keep `meta.seq` strictly sequential within each folder (`1, 2, 3, ...`) and match the numeric prefix on the filename (e.g. `04-list-deployments.bru` -> `seq: 4`).
3. Include a `tests { ... }` block with at least a status assertion and structural body assertions where practical.
4. Add a concise `docs { ... }` block explaining required RBAC permissions, expected query parameters, or GitOps side effects (especially for mutating endpoints).
5. Never commit real bearer tokens, passwords, kubeconfigs, or cluster hostnames containing private credentials. Use `vars:secret [...]` in `environments/*.bru`.

## Local Validation

Before opening a pull request, run:

```bash
make validate
```

If you have Node.js and `markdownlint-cli2` installed:

```bash
make lint
```
