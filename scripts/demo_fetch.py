#!/usr/bin/env python3
"""Simulate an NVDA Add-on Store client fetching the static registry.

Reads the compiled ``dist/index.json`` by default, or any local path / URL
passed as the positional ``source`` argument, and prints a screen-reader
friendly listing. Pass ``--addon-id`` for full metadata on a single addon.

Stdlib only. No third-party dependencies.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = PROJECT_ROOT / "dist" / "index.json"

FETCH_TIMEOUT_SECONDS = 15

# Display order for the detail view; keys absent from a manifest are skipped.
DETAIL_FIELDS: tuple[tuple[str, str], ...] = (
    ("name", "Name"),
    ("version", "Version"),
    ("author", "Author"),
    ("description", "Description"),
    ("id", "Addon ID"),
    ("min_nvda_version", "Minimum NVDA version"),
    ("last_tested_nvda_version", "Last tested NVDA version"),
    ("last_updated", "Last updated"),
    ("sha256", "SHA-256"),
    ("homepage", "Homepage"),
    ("download_url", "Download URL"),
)


def is_url(source: str) -> bool:
    return source.startswith(("http://", "https://"))


def ensure_utf8_output() -> None:
    """Make printing Unicode (e.g. author names) safe when stdout is piped.

    On Windows a redirected stdout uses a legacy code page that cannot encode
    characters like U+011F, crashing the listing. Reconfigure to UTF-8.
    """
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass


def load_registry(source: str) -> dict:
    """Load and parse the registry from a local path or URL.

    Raises ValueError with a readable message on any I/O or parse failure.
    """
    if is_url(source):
        try:
            with urlopen(source, timeout=FETCH_TIMEOUT_SECONDS) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            raise ValueError(f"HTTP {exc.code} fetching {source}") from exc
        except URLError as exc:
            raise ValueError(f"network error fetching {source}: {exc.reason}") from exc
    else:
        path = Path(source)
        if not path.is_file():
            raise ValueError(f"file not found: {path}")
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ValueError(f"cannot read {path}: {exc}") from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc

    if not isinstance(data, dict) or not isinstance(data.get("addons"), dict):
        raise ValueError("registry must be an object containing an 'addons' object")
    return data


def print_listing(registry: dict) -> None:
    """Print a summary line group per addon, sorted by display name."""
    addons = registry["addons"]
    ordered = sorted(addons.values(), key=lambda item: item.get("name", "").lower())

    print(f"Add-on Store registry: {len(ordered)} add-on(s) available.")
    print(f"Generated at: {registry.get('generated_at', 'unknown')}")
    print()

    for addon in ordered:
        print(f"Name: {addon.get('name', '(unnamed)')}")
        print(f"Version: {addon.get('version', 'unknown')}")
        print(f"Author: {addon.get('author', 'unknown')}")
        print(f"Download URL: {addon.get('download_url', 'unknown')}")
        print()


def print_detail(registry: dict, addon_id: str) -> int:
    """Print full metadata for one addon. Returns a process exit code."""
    addons = registry["addons"]
    addon = addons.get(addon_id)
    if addon is None:
        print(f"error: add-on '{addon_id}' not found", file=sys.stderr)
        available = ", ".join(sorted(addons)) or "(none)"
        print(f"available add-on IDs: {available}", file=sys.stderr)
        return 1

    print(f"Details for add-on: {addon_id}")
    print()
    for key, label in DETAIL_FIELDS:
        value = addon.get(key)
        if value:
            print(f"{label}: {value}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch and print the NVDA Add-on Store registry."
    )
    parser.add_argument(
        "source",
        nargs="?",
        default=str(DEFAULT_SOURCE),
        help=(
            "local path or http(s) URL to the registry JSON "
            f"(default: {DEFAULT_SOURCE})"
        ),
    )
    parser.add_argument(
        "--addon-id",
        help="show full details for a single add-on instead of the listing",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    ensure_utf8_output()
    args = parse_args(argv)
    try:
        registry = load_registry(args.source)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.addon_id:
        return print_detail(registry, args.addon_id)

    print_listing(registry)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
