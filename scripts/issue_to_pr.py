#!/usr/bin/env python3
"""Convert an add-on submission issue into a registry manifest.

Reads a GitHub issue body produced by .github/ISSUE_TEMPLATE/addon-submission.yml,
validates it with the same strict checks as scripts/review_pr.py, and either
writes registry/addons/<id>.json (verdict: valid) or writes a refusal comment
(verdict: invalid). A CI workflow performs the git/GitHub steps.

Usage:
    python scripts/issue_to_pr.py --body-file BODY --issue-number NUM
        --issue-author USER [--registry-dir DIR] [--comment-out FILE]
        [--verdict-out FILE]

Exit codes: 0 verdict reached (check --verdict-out for valid/invalid),
1 usage or infrastructure error.

Stdlib only. No third-party dependencies.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY_DIR = PROJECT_ROOT / "registry" / "addons"

EMPTY_MARKERS = {"", "_no response_", "no response", "none", "n/a"}


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(
        name, Path(__file__).resolve().parent / f"{name}.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build = load_module("build_registry")
review = load_module("review_pr")

# Maps issue-form section headings to manifest fields.
FIELD_SECTIONS = {
    "Add-on ID": "id",
    "Display name": "name",
    "Version": "version",
    "Author": "author",
    "Description": "description",
    "Homepage": "homepage",
    "Download URL": "download_url",
    "SHA-256 checksum": "sha256",
    "Minimum NVDA version": "min_nvda_version",
    "Last tested NVDA version": "last_tested_nvda_version",
    "Last updated": "last_updated",
}
CHECKBOX_SECTION = "Acknowledgments"

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
MAX_ID_LENGTH = 64


def parse_issue_body(raw: str) -> tuple[dict, list[str]]:
    """Split the issue body into field values plus checkbox states.

    Returns (fields, unchecked_items). Checkbox lines look like '- [X] text'
    or '- [ ] text' under the Acknowledgments heading.
    """
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in raw.splitlines():
        if line.startswith("### "):
            current = line[4:].strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)

    fields = {}
    for heading, field in FIELD_SECTIONS.items():
        value = "\n".join(sections.get(heading, [])).strip()
        fields[field] = value

    unchecked: list[str] = []
    for line in sections.get(CHECKBOX_SECTION, []):
        match = re.match(r"\s*-\s*\[( |x|X)\]\s*(.+)", line)
        if match and match.group(1) == " ":
            unchecked.append(match.group(2).strip())
    return fields, unchecked


def is_empty(value: str) -> bool:
    return value.strip().lower() in EMPTY_MARKERS


def validate_submission(fields: dict, unchecked: list[str],
                        registry_dir: Path) -> tuple[dict | None, list[str]]:
    """Return (manifest_or_None, fatal_errors)."""
    errors: list[str] = []

    if unchecked:
        errors.append(
            "all acknowledgment boxes must be checked; "
            f"{len(unchecked)} left unchecked"
        )

    addon_id = fields.get("id", "").strip()
    if not addon_id or is_empty(addon_id):
        errors.append("field 'Add-on ID' is required")
    elif len(addon_id) > MAX_ID_LENGTH:
        errors.append("field 'Add-on ID' is too long (max "
                      f"{MAX_ID_LENGTH} characters)")
    elif not ID_RE.match(addon_id):
        errors.append(
            f"field 'Add-on ID' ({addon_id!r}) may only contain letters, "
            "numbers, dots, dashes, and underscores, and must start with "
            "a letter or number"
        )
    elif (registry_dir / f"{addon_id}.json").exists():
        errors.append(
            f"an add-on with ID {addon_id!r} is already listed; to update it, "
            "open a blank issue instead of a new submission"
        )

    for heading, field in FIELD_SECTIONS.items():
        if field in ("author", "last_updated"):
            continue
        if is_empty(fields.get(field, "")):
            errors.append(f"field '{heading}' is required")

    if errors:
        return None, errors

    manifest = {
        "id": addon_id,
        "name": fields["name"].strip(),
        "version": fields["version"].strip(),
        "author": fields["author"].strip(),
        "description": fields["description"].strip(),
        "homepage": fields["homepage"].strip(),
        "download_url": fields["download_url"].strip(),
        "sha256": fields["sha256"].strip().lower(),
        "min_nvda_version": fields["min_nvda_version"].strip(),
        "last_tested_nvda_version": fields["last_tested_nvda_version"].strip(),
        "last_updated": fields["last_updated"].strip(),
    }
    return manifest, []


def run_review(manifest: dict, filename: str) -> tuple[list[str], list[str]]:
    """Run the strict reviewer against an in-memory manifest."""
    data = dict(manifest)
    errors = list(build.validate_manifest(data, Path(filename)))
    if errors:
        return errors, []
    errors.extend(review.check_placeholders(data))
    errors.extend(review.check_description(data))
    errors.extend(review.check_policy_floor(data))
    warnings = review.check_min_vs_tested(data)
    warnings.extend(review.check_version_in_url(data))
    return errors, warnings


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Turn an add-on submission issue into a registry manifest."
    )
    parser.add_argument("--body-file", type=Path, required=True)
    parser.add_argument("--issue-number", required=True)
    parser.add_argument("--issue-author", required=True)
    parser.add_argument("--registry-dir", type=Path, default=DEFAULT_REGISTRY_DIR)
    parser.add_argument("--comment-out", type=Path, default=None,
                        help="write the refusal comment here on invalid verdict")
    parser.add_argument("--verdict-out", type=Path, default=None,
                        help="append 'verdict=valid|invalid' and manifest path here")
    return parser.parse_args(argv)


def ensure_utf8_output() -> None:
    """Keep Unicode in diagnostics printable when stdout is redirected."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass


def emit_verdict(path: Path | None, lines: list[str]) -> None:
    if path is None:
        return
    with open(path, "a", encoding="utf-8") as handle:
        for line in lines:
            handle.write(line + "\n")


def main(argv=None) -> int:
    ensure_utf8_output()
    args = parse_args(argv)

    try:
        raw = args.body_file.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read body file: {exc}", file=sys.stderr)
        return 1

    fields, unchecked = parse_issue_body(raw)
    manifest, errors = validate_submission(fields, unchecked, args.registry_dir)

    if manifest is not None:
        if is_empty(manifest["author"]):
            manifest["author"] = f"@{args.issue_author}"
        if is_empty(manifest["last_updated"]):
            manifest["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        filename = f"{manifest['id']}.json"
        review_errors, warnings = run_review(manifest, filename)
        errors.extend(review_errors)
    else:
        warnings = []

    if errors:
        comment = [
            "Your add-on submission was automatically refused for the following reasons:",
            "",
            *[f"- {message}" for message in errors],
            "",
            "Fix everything and open a new submission issue. If you believe the reviewer is wrong, say so in a comment and a human will take a look.",
        ]
        if args.comment_out is not None:
            args.comment_out.write_text("\n".join(comment) + "\n", encoding="utf-8")
        else:
            print("\n".join(comment))
        emit_verdict(args.verdict_out, ["verdict=invalid"])
        print(f"verdict: invalid ({len(errors)} problem(s))")
        return 0

    ordered = {field: manifest[field] for field in build.REQUIRED_FIELDS}
    out_path = args.registry_dir / filename
    out_path.write_text(
        json.dumps(ordered, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    if warnings:
        print("warnings (non-blocking):")
        for message in warnings:
            print(f"  WARN: {message}")
    emit_verdict(args.verdict_out, ["verdict=valid", f"manifest={out_path}"])
    print(f"verdict: valid, wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
