#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_SLUG = "ruturajr-raval/lonely-runner-15-prime-29"
REPOSITORY_URL = f"https://github.com/{REPOSITORY_SLUG}"
VERSION_DOI = "10.5281/zenodo.22539842"
CONCEPT_DOI = "10.5281/zenodo.22539841"
VERSION_PATTERN = r"[0-9]+\.[0-9]+\.[0-9]+"


def require_match(
    errors: list[str],
    path: Path,
    pattern: str,
    description: str,
) -> str | None:
    match = re.search(pattern, path.read_text(encoding="utf-8"), re.MULTILINE)
    if match is None:
        errors.append(f"{path.name}: missing {description}")
        return None
    return match.group(1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--repository")
    parser.add_argument("--tag")
    args = parser.parse_args()

    root = args.root.resolve()
    errors: list[str] = []
    required = {
        "citation": root / "CITATION.cff",
        "readme": root / "README.md",
        "publication": root / "PUBLICATION.md",
        "release-notes": root / "RELEASE_NOTES.md",
        "arxiv": root / "paper" / "ARXIV_METADATA.md",
        "pyproject": root / "pyproject.toml",
        "zenodo": root / ".zenodo.json",
    }
    for name, path in required.items():
        if not path.is_file():
            errors.append(f"missing {name} file: {path}")
    if errors:
        for error in errors:
            print(f"release metadata error: {error}", file=sys.stderr)
        return 1

    citation_version = require_match(
        errors,
        required["citation"],
        rf"^version:\s*({VERSION_PATTERN})\s*$",
        "top-level version",
    )
    pyproject_version = require_match(
        errors,
        required["pyproject"],
        rf'^version\s*=\s*"({VERSION_PATTERN})"\s*$',
        "project version",
    )
    repository_url = require_match(
        errors,
        required["citation"],
        r'^repository-code:\s*"([^"]+)"\s*$',
        "repository-code",
    )
    release_date = require_match(
        errors,
        required["citation"],
        r"^date-released:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\s*$",
        "date-released",
    )

    try:
        zenodo = json.loads(
            required["zenodo"].read_text(encoding="utf-8")
        )
    except (json.JSONDecodeError, OSError) as error:
        errors.append(f".zenodo.json: {error}")
        zenodo = {}
    zenodo_version = zenodo.get("version")
    if not isinstance(zenodo_version, str):
        errors.append(".zenodo.json: version must be a string")

    if citation_version is not None:
        versions = {
            "CITATION.cff": citation_version,
            "pyproject.toml": pyproject_version,
            ".zenodo.json": zenodo_version,
        }
        for name, version in versions.items():
            if version != citation_version:
                errors.append(
                    f"{name}: version {version!r} does not match "
                    f"{citation_version!r}"
                )

        expected_tag = f"v{citation_version}"
        expected_headers = {
            "PUBLICATION.md": (
                required["publication"],
                f"# Release {expected_tag}",
            ),
            "RELEASE_NOTES.md": (
                required["release-notes"],
                f"# {expected_tag}",
            ),
        }
        for name, (path, expected) in expected_headers.items():
            first_line = path.read_text(encoding="utf-8").splitlines()[0]
            if first_line != expected:
                errors.append(
                    f"{name}: first line {first_line!r} does not match "
                    f"{expected!r}"
                )
        if args.tag is not None and args.tag != expected_tag:
            errors.append(
                f"tag {args.tag!r} does not match metadata tag "
                f"{expected_tag!r}"
            )

    if repository_url != REPOSITORY_URL:
        errors.append(
            "CITATION.cff: repository-code does not match the publication "
            "repository"
        )
    if (
        args.repository is not None
        and args.repository != REPOSITORY_SLUG
    ):
        errors.append(
            f"repository {args.repository!r} does not match publication "
            f"repository {REPOSITORY_SLUG!r}"
        )
    if release_date is None:
        errors.append("CITATION.cff: release date is invalid")

    required_dois = {
        "CITATION.cff": (
            required["citation"],
            (VERSION_DOI, VERSION_DOI),
        ),
        "README.md": (
            required["readme"],
            (VERSION_DOI, CONCEPT_DOI),
        ),
        "PUBLICATION.md": (
            required["publication"],
            (VERSION_DOI, CONCEPT_DOI),
        ),
        "paper/ARXIV_METADATA.md": (
            required["arxiv"],
            (VERSION_DOI, CONCEPT_DOI),
        ),
    }
    for name, (path, dois) in required_dois.items():
        text = path.read_text(encoding="utf-8")
        for doi in set(dois):
            expected_count = dois.count(doi)
            actual_count = text.count(doi)
            if actual_count < expected_count:
                errors.append(
                    f"{name}: expected at least {expected_count} "
                    f"occurrence(s) of {doi}, found {actual_count}"
                )

    if errors:
        for error in errors:
            print(f"release metadata error: {error}", file=sys.stderr)
        return 1

    print(f"release metadata consistent for v{citation_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
