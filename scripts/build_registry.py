#!/usr/bin/env python3
"""Compile individual addon manifests into a single static registry index.

Reads every ``*.json`` manifest from ``registry/addons/``, validates each one
against the addon schema, and writes a deterministic ``dist/index.json`` keyed
by addon id.

The build is fail-fast: if any manifest is invalid the process exits with a
non-zero status and no output file is written, so a malformed record can never
reach the published registry.

Stdlib only. No third-party dependencies.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ADDONS_DIR = PROJECT_ROOT / "registry" / "addons"
DEFAULT_OUTPUT = PROJECT_ROOT / "dist" / "index.json"

# Schema contract: every addon manifest must carry all of these keys, and each
# value must be a non-empty string. Emission order is also this order, with the
# date last.
REQUIRED_FIELDS: tuple[str, ...] = (
    "id",
    "name",
    "version",
    "author",
    "description",
    "homepage",
    "download_url",
    "sha256",
    "min_nvda_version",
    "last_tested_nvda_version",
    "last_updated",
)

# Accepts semver, shallow or full, with optional pre-release/build metadata.
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
# Accepts NVDA-style calendar versions such as "2024.1" or "2026.3".
# "0.0" is the sentinel for "no minimum" (legacy manifests that declare 0.0.0).
NVDA_VERSION_RE = re.compile(r"^(?:\d{4}\.\d+|0\.0)$")
# Last-tested versions may carry an optional patch component, e.g. "2026.1.0".
LAST_TESTED_RE = re.compile(r"^\d{4}\.\d+(?:\.\d+)?$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class BuildError(Exception):
    """Raised when the registry cannot be built (missing inputs or bad data)."""


def ensure_utf8_output() -> None:
    """Keep Unicode in diagnostics printable when stdout is redirected."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass


def load_manifest(path: Path) -> dict:
    """Read one manifest file. Raises ValueError with a readable message."""
    try:
        # utf-8-sig accepts both plain UTF-8 and UTF-8 with BOM (Windows editors).
        raw = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise ValueError(f"cannot read file: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("top-level JSON value must be an object")
    return data


def validate_manifest(data: dict, path: Path) -> list[str]:
    """Return a list of human-readable validation errors (empty means valid)."""
    errors: list[str] = []

    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"missing required field '{field}'")
        elif not isinstance(data[field], str):
            errors.append(f"field '{field}' must be a string")
        elif not data[field].strip():
            errors.append(f"field '{field}' must not be empty")

    # If a required field is absent or mistyped, deeper checks would raise.
    # Bail out early to keep the error list focused.
    if errors:
        return errors

    if not SEMVER_RE.match(data["version"]):
        errors.append(f"field 'version' is not valid semver: {data['version']!r}")

    if not NVDA_VERSION_RE.match(data["min_nvda_version"]):
        errors.append(
            "field 'min_nvda_version' must look like 'YYYY.N' "
            "(or '0.0' for no minimum): "
            f"{data['min_nvda_version']!r}"
        )

    if not LAST_TESTED_RE.match(data["last_tested_nvda_version"]):
        errors.append(
            "field 'last_tested_nvda_version' must look like 'YYYY.N' or "
            f"'YYYY.N.N': {data['last_tested_nvda_version']!r}"
        )

    for url_field in ("homepage", "download_url"):
        parsed = urlparse(data[url_field])
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            errors.append(f"field '{url_field}' is not a valid http(s) URL")

    if not data["download_url"].endswith(".nvda-addon"):
        errors.append("field 'download_url' must point to a .nvda-addon file")

    if not SHA256_RE.match(data["sha256"]):
        errors.append("field 'sha256' must be 64 lowercase hex characters")

    try:
        date.fromisoformat(data["last_updated"])
    except ValueError:
        errors.append(
            f"field 'last_updated' must be an ISO date (YYYY-MM-DD): "
            f"{data['last_updated']!r}"
        )

    if data["id"] != path.stem:
        errors.append(
            f"field 'id' ({data['id']!r}) must match the filename ({path.stem!r})"
        )

    return errors


def build_registry(addons_dir: Path) -> dict:
    """Validate every manifest and return the compiled registry document."""
    if not addons_dir.is_dir():
        raise BuildError(f"addons directory not found: {addons_dir}")

    manifest_paths = sorted(addons_dir.glob("*.json"))
    if not manifest_paths:
        raise BuildError(f"no *.json manifests found in {addons_dir}")

    addons: dict[str, dict] = {}
    all_errors: list[str] = []

    for path in manifest_paths:
        try:
            data = load_manifest(path)
        except ValueError as exc:
            all_errors.append(f"{path.name}: {exc}")
            continue

        errors = validate_manifest(data, path)
        if errors:
            all_errors.extend(f"{path.name}: {err}" for err in errors)
            continue

        addon_id = data["id"]
        if addon_id in addons:
            all_errors.append(f"{path.name}: duplicate addon id '{addon_id}'")
            continue

        addons[addon_id] = data

    if all_errors:
        for message in all_errors:
            print(f"error: {message}", file=sys.stderr)
        raise BuildError(f"{len(all_errors)} problem(s); registry not written")

    # Normalise ordering so rebuilds produce byte-identical output.
    # Emit every manifest in the canonical field order (date last); any
    # unexpected extra keys follow, then addons are sorted by id.
    def canonical(manifest: dict) -> dict:
        ordered = {field: manifest[field] for field in REQUIRED_FIELDS}
        for key in manifest:
            if key not in ordered:
                ordered[key] = manifest[key]
        return ordered

    ordered = {
        addon_id: canonical(addons[addon_id]) for addon_id in sorted(addons)
    }
    return {
        "generated_at": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "addon_count": len(ordered),
        "addons": ordered,
    }


def write_registry(registry: dict, output: Path) -> None:
    """Write the registry to disk, creating the parent directory if needed."""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(registry, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compile registry/addons/*.json into dist/index.json."
    )
    parser.add_argument(
        "--addons-dir",
        type=Path,
        default=DEFAULT_ADDONS_DIR,
        help=f"directory of addon manifests (default: {DEFAULT_ADDONS_DIR})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"compiled registry path (default: {DEFAULT_OUTPUT})",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    ensure_utf8_output()
    args = parse_args(argv)
    try:
        registry = build_registry(args.addons_dir)
    except BuildError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    write_registry(registry, args.output)
    print(f"Wrote {registry['addon_count']} addon(s) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
