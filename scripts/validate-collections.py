#!/usr/bin/env python3
"""Validate Bruno collection structure, .bru syntax invariants, sequencing, and secret hygiene."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COLLECTIONS_DIR = ROOT / "collections"
EXPECTED_ENVS = {"local-kind.bru", "k3s-homelab.bru", "staging.bru", "production-ro.bru"}
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}
SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"gho_[A-Za-z0-9]{20,}"),
    re.compile(r"glpat-[A-Za-z0-9_-]{20,}"),
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]


def parse_meta_block(text: str) -> dict[str, str]:
    match = re.search(r"^meta\s*\{(.*?)^\}", text, flags=re.MULTILINE | re.DOTALL)
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if ":" in stripped:
            k, v = stripped.split(":", 1)
            result[k.strip()] = v.strip()
    return result


def check_balanced_braces(text: str) -> bool:
    """Verify top-level block delimiters balance outside quoted strings and docs blocks."""
    cleaned = re.sub(r"^docs\s*\{.*?^\}", "", text, flags=re.MULTILINE | re.DOTALL)
    depth = 0
    in_string = False
    escape = False
    for ch in cleaned:
        if escape:
            escape = False
            continue
        if ch == "\\" and in_string:
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if not in_string:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth < 0:
                    return False
    return depth == 0


def validate_collection(col_dir: Path) -> list[str]:
    errors: list[str] = []
    bruno_json = col_dir / "bruno.json"
    if not bruno_json.is_file():
        return [f"{col_dir.name}: missing bruno.json"]

    try:
        meta = json.loads(bruno_json.read_text(encoding="utf-8"))
        if meta.get("type") != "collection" or meta.get("version") != "1":
            errors.append(f"{col_dir.name}: bruno.json must set version='1' and type='collection'")
    except json.JSONDecodeError as exc:
        errors.append(f"{col_dir.name}: invalid bruno.json ({exc})")

    env_dir = col_dir / "environments"
    if not env_dir.is_dir():
        errors.append(f"{col_dir.name}: missing environments/ directory")
    else:
        found_envs = {p.name for p in env_dir.glob("*.bru")}
        missing = EXPECTED_ENVS - found_envs
        if missing:
            errors.append(f"{col_dir.name}: missing environments {sorted(missing)}")
        for env_file in sorted(env_dir.glob("*.bru")):
            env_text = env_file.read_text(encoding="utf-8")
            if not check_balanced_braces(env_text):
                errors.append(f"{env_file.relative_to(ROOT)}: unbalanced braces")

    folder_seqs: list[int] = []
    for folder in sorted(p for p in col_dir.iterdir() if p.is_dir() and p.name != "environments"):
        folder_bru = folder / "folder.bru"
        if not folder_bru.is_file():
            errors.append(f"{folder.relative_to(ROOT)}: missing folder.bru")
        else:
            fmeta = parse_meta_block(folder_bru.read_text(encoding="utf-8"))
            if "seq" not in fmeta or not fmeta["seq"].isdigit():
                errors.append(f"{folder_bru.relative_to(ROOT)}: missing numeric meta.seq")
            else:
                folder_seqs.append(int(fmeta["seq"]))

        req_seqs: list[int] = []
        for bru_file in sorted(p for p in folder.glob("*.bru") if p.name != "folder.bru"):
            rel = bru_file.relative_to(ROOT)
            content = bru_file.read_text(encoding="utf-8")
            for pattern in SECRET_PATTERNS:
                if pattern.search(content):
                    errors.append(f"{rel}: potential hardcoded secret matched {pattern.pattern}")

            if not check_balanced_braces(content):
                errors.append(f"{rel}: unbalanced braces")

            rmeta = parse_meta_block(content)
            if not rmeta.get("name") or rmeta.get("type") not in {"http", "graphql"}:
                errors.append(f"{rel}: meta block must define name and type (http/graphql)")
            seq_val = rmeta.get("seq", "")
            if not seq_val.isdigit():
                errors.append(f"{rel}: meta.seq must be an integer")
            else:
                req_seqs.append(int(seq_val))

            has_method = any(
                re.search(rf"^{m}\s*\{{", content, flags=re.MULTILINE) for m in HTTP_METHODS
            )
            if not has_method:
                errors.append(f"{rel}: missing HTTP method block")
            if not re.search(r"^tests\s*\{", content, flags=re.MULTILINE):
                errors.append(f"{rel}: missing tests block")
            if not re.search(r"^docs\s*\{", content, flags=re.MULTILINE):
                errors.append(f"{rel}: missing docs block")

        if req_seqs and req_seqs != list(range(1, len(req_seqs) + 1)):
            errors.append(
                f"{folder.relative_to(ROOT)}: request seq values must be contiguous 1..{len(req_seqs)}, got {req_seqs}"
            )

    if folder_seqs and sorted(folder_seqs) != list(range(1, len(folder_seqs) + 1)):
        errors.append(
            f"{col_dir.name}: folder seq values must be contiguous 1..{len(folder_seqs)}, got {folder_seqs}"
        )

    return errors


def main() -> int:
    if not COLLECTIONS_DIR.is_dir():
        print("ERROR: collections/ directory not found", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    collections = sorted(p for p in COLLECTIONS_DIR.iterdir() if p.is_dir())
    total_requests = 0

    for col in collections:
        all_errors.extend(validate_collection(col))
        total_requests += sum(
            1 for p in col.rglob("*.bru") if p.name != "folder.bru" and p.name != "collection.bru" and p.parent.name != "environments"
        )

    if all_errors:
        print("Validation failed:", file=sys.stderr)
        for err in all_errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"Validated {len(collections)} collections and {total_requests} request files cleanly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
