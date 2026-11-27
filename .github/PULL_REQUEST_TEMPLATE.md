## Summary

Describe the Bruno collection, folder, or endpoint changes included in this pull request.

## Checklist

- [ ] `make validate` passes locally (`python3 scripts/validate-collections.py`)
- [ ] New `.bru` files include `meta`, `tests`, and `docs` blocks
- [ ] `meta.seq` values are contiguous and match the filename numeric prefix
- [ ] No tokens, passwords, private hostnames, or cluster certificates are committed
- [ ] Any new secret variable is declared in `vars:secret [...]` across all environments
