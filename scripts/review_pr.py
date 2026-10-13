#!/usr/bin/env python3
"""Automated reviewer for registry pull requests.

Validates one or more addon manifests much more strictly than the schema
alone: template leftovers, version style, policy floors (NVDA 2026.1+),
description quality, and download-link sanity. Any fatal problem exits
non-zero so CI can refuse the pull request automatically.

Network checks (link reachability, download size) are warnings only: the
network is flaky and reviewers should be deterministic. Pass --no-network
to skip them entirely.

Usage:
    python scripts/review_pr.py [manifest ...] [--addons-dir DIR] [--no-network]

With no manifest arguments, every *.json in the addons dir is reviewed
(used for full sweeps; CI passes only the files changed in the PR).

Stdlib only. No third-party dependencies.
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ADDONS_DIR = PROJECT_ROOT / "registry" / "addons"


def load_build_module():
    spec = importlib.util.spec_from_file_location(
        "build_registry", Path(__file__).resolve().parent / "build_registry.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build = load_build_module()

# Project policy: nothing enters the catalog untested below this floor.
MIN_LAST_TESTED = (2026, 1)

# Descriptions shorter than this are not descriptions, they are grunts.
MIN_DESCRIPTION_LENGTH = 30

# Downloads above this only earn a warning (networks lie); see the size rule
# in CONTRIBUTING.md for the human-enforced half of this policy.
SIZE_WARN_BYTES = 50 * 1024 * 1024
FETCH_TIMEOUT_SECONDS = 10

# Leftover template text. If any of these survive in a submission, the author
# did not read the template, let alone CONTRIBUTING.md.
PLACEHOLDER_NEEDLES: tuple[str, ...] = (
    "my-addon",
    "my add-on",
    "your name",
    "github.com/you",
    "example.com",
    "paste-the",
    "placeholder",
    "lorem",
    "what the add-on does",
    "who it helps",
    "fixme",
    "changeme",
)

# Any character from these scripts in a description means the description is
# not English (accents and Latin-extended punctuation are fine).
NON_LATIN_RE = re.compile(
    "["
    "\u0370-\u03ff"  # Greek
    "\u0400-\u04ff"  # Cyrillic
    "\u0530-\u058f"  # Armenian
    "\u0590-\u05ff"  # Hebrew
    "\u0600-\u06ff"  # Arabic
    "\u0900-\u097f"  # Devanagari
    "\u0e00-\u0e7f"  # Thai
    "\u0e80-\u0eff"  # Lao
    "\u1000-\u109f"  # Myanmar
    "\u3040-\u30ff"  # Hiragana/Katakana
    "\u4e00-\u9fff"  # CJK
    "\uac00-\ud7af"  # Hangul
    "]"
)

TEXT_FIELDS = ("id", "name", "author", "description", "homepage", "download_url")


def check_placeholders(data: dict) -> list[str]:
    errors = []
    for field in TEXT_FIELDS:
        value = str(data.get(field, "")).lower()
        for needle in PLACEHOLDER_NEEDLES:
            if needle in value:
                errors.append(
                    f"field '{field}' still contains template placeholder "
                    f"text ({needle!r}); replace every placeholder with real values"
                )
                break
    return errors


def check_description(data: dict) -> list[str]:
    errors = []
    desc = str(data.get("description", ""))
    if desc.strip() and len(desc.strip()) < MIN_DESCRIPTION_LENGTH:
        errors.append(
            f"field 'description' is {len(desc.strip())} characters; "
            f"write at least {MIN_DESCRIPTION_LENGTH} that explain what the "
            "add-on does and who it helps"
        )
    if NON_LATIN_RE.search(desc):
        errors.append(
            "field 'description' contains non-Latin script characters; "
            "descriptions must be in English"
        )
    return errors


def check_policy_floor(data: dict) -> list[str]:
    errors = []
    tested = str(data.get("last_tested_nvda_version", ""))
    match = re.match(r"^(\d{4})\.(\d+)", tested)
    if match:
        if (int(match.group(1)), int(match.group(2))) < MIN_LAST_TESTED:
            errors.append(
                f"field 'last_tested_nvda_version' is {tested!r}; this catalog "
                "only accepts add-ons tested on NVDA 2026.1 or newer"
            )
    return errors


def check_min_vs_tested(data: dict) -> list[str]:
    """Warn when the declared minimum is newer than what was tested."""
    warnings = []
    min_v = str(data.get("min_nvda_version", ""))
    tested = str(data.get("last_tested_nvda_version", ""))
    min_m = re.match(r"^(\d{4})\.(\d+)", min_v)
    tested_m = re.match(r"^(\d{4})\.(\d+)", tested)
    if min_m and tested_m:
        if (int(min_m.group(1)), int(min_m.group(2))) > (
            int(tested_m.group(1)),
            int(tested_m.group(2)),
        ):
            warnings.append(
                f"min_nvda_version ({min_v}) is newer than "
                f"last_tested_nvda_version ({tested}); minimum should be "
                "at or below what was tested"
            )
    return warnings


def _norm_num(token: str) -> str:
    """Normalize a dotted number so '2026.08.24' and '2026.8.24' compare equal."""
    return ".".join(str(int(part)) for part in token.split("."))


def check_version_in_url(data: dict) -> list[str]:
    """Warn when the version appears nowhere in the download URL.

    Comparison is format-tolerant: '26.4.0' matches a URL containing
    '26.04', and '2026.8.24' matches '2026.08.24'. Either the full
    version or its major.minor prefix must show up.
    """
    warnings = []
    version = str(data.get("version", ""))
    url = str(data.get("download_url", ""))
    if not version or not url:
        return warnings
    core = re.split(r"[-+]", version, maxsplit=1)[0]
    try:
        norm_ver = _norm_num(core)
    except ValueError:
        return warnings
    parts = norm_ver.split(".")
    candidates = {norm_ver}
    if len(parts) >= 2:
        candidates.add(".".join(parts[:2]))
    url_tokens = set()
    for token in re.findall(r"\d+(?:\.\d+)+", url):
        try:
            url_tokens.add(_norm_num(token))
        except ValueError:
            continue
    if not (candidates & url_tokens):
        warnings.append(
            f"version {version!r} does not appear in download_url; "
            "make sure the link points at the exact file for this version"
        )
    return warnings


def check_network(data: dict) -> list[str]:
    """Warnings only: is the download reachable, and is it enormous?"""
    warnings = []
    url = str(data.get("download_url", ""))
    if not url.startswith(("http://", "https://")):
        return warnings
    try:
        request = Request(url, method="HEAD")
        with urlopen(request, timeout=FETCH_TIMEOUT_SECONDS) as response:
            length = response.headers.get("Content-Length")
    except Exception as exc:
        warnings.append(f"could not verify download_url ({exc}); is the link live?")
        return warnings
    if length:
        try:
            size = int(length)
        except ValueError:
            return warnings
        if size > SIZE_WARN_BYTES:
            warnings.append(
                f"download is ~{size / 1024 / 1024:.0f} MB; per the size rule, "
                "add-ons bigger than the screen reader itself are rejected, "
                "so consider hosting heavy files separately"
            )
    return warnings


def review_manifest(path: Path, check_online: bool) -> tuple[list[str], list[str]]:
    """Return (fatal_errors, warnings) for one manifest file."""
    try:
        data = build.load_manifest(path)
    except ValueError as exc:
        return [f"{exc}"], []

    errors = list(build.validate_manifest(data, path))
    if errors:
        # Schema failures already disqualify; deeper checks would be noise.
        return errors, []

    errors.extend(check_placeholders(data))
    errors.extend(check_description(data))
    errors.extend(check_policy_floor(data))
    warnings = check_min_vs_tested(data)
    warnings.extend(check_version_in_url(data))
    if check_online:
        warnings.extend(check_network(data))
    return errors, warnings


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Strict automated review of registry manifests for PRs."
    )
    parser.add_argument(
        "manifests",
        nargs="*",
        type=Path,
        help="manifest files to review (default: every *.json in --addons-dir)",
    )
    parser.add_argument(
        "--addons-dir",
        type=Path,
        default=DEFAULT_ADDONS_DIR,
        help=f"directory of addon manifests (default: {DEFAULT_ADDONS_DIR})",
    )
    parser.add_argument(
        "--no-network",
        action="store_true",
        help="skip live download-URL checks (warnings only otherwise)",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    if args.manifests:
        targets = sorted(args.manifests)
    else:
        targets = sorted(args.addons_dir.glob("*.json"))
        if not targets:
            print(f"error: no *.json manifests found in {args.addons_dir}",
                  file=sys.stderr)
            return 1

    total_errors = 0
    total_warnings = 0
    for path in targets:
        errors, warnings = review_manifest(path, check_online=not args.no_network)
        for message in errors:
            print(f"FAIL {path.name}: {message}")
        for message in warnings:
            print(f"WARN {path.name}: {message}")
        total_errors += len(errors)
        total_warnings += len(warnings)

    print(f"reviewed {len(targets)} manifest(s): "
          f"{total_errors} problem(s), {total_warnings} warning(s)")
    if total_errors:
        print("REVIEW FAILED: refusing submission until problems are fixed")
        return 1
    print("REVIEW PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
