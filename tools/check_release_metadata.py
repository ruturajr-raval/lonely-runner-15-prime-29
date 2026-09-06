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
CONCEPT_DOI = "10.5281/zenodo.22539841"
VERSION_PATTERN = r"[0-9]+\.[0-9]+\.[0-9]+"
DOI_PATTERN = r"10\.5281/zenodo\.[0-9]+"
SHA256_PATTERN = r"[0-9a-f]{64}"
COMMIT_PATTERN = r"[0-9a-f]{40}"
EXPECTED_ASSETS = (
    "lonely-runner-15-prime-29-paper.pdf",
    "lonely-runner-15-prime-29-source.tar.gz",
    "lonely-runner-15-prime-29-certificate-v1.tar.gz",
    "SHA256SUMS",
)


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
        "release-record": root / ".release-record.json",
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

    try:
        release_record = json.loads(
            required["release-record"].read_text(encoding="utf-8")
        )
    except (json.JSONDecodeError, OSError) as error:
        errors.append(f".release-record.json: {error}")
        release_record = {}
    if release_record.get("schema") != 1:
        errors.append(".release-record.json: schema must be 1")
    record_version = release_record.get("version")
    record_tag = release_record.get("tag")
    version_doi = release_record.get("version_doi")
    release_commit = release_record.get("release_commit")
    assets = release_record.get("assets")
    archive = release_record.get("zenodo_archive")

    if citation_version is not None:
        versions = {
            "CITATION.cff": citation_version,
            "pyproject.toml": pyproject_version,
            ".release-record.json": record_version,
            ".zenodo.json": zenodo_version,
        }
        for name, version in versions.items():
            if version != citation_version:
                errors.append(
                    f"{name}: version {version!r} does not match "
                    f"{citation_version!r}"
                )

        expected_tag = f"v{citation_version}"
        if record_tag != expected_tag:
            errors.append(
                ".release-record.json: tag "
                f"{record_tag!r} does not match {expected_tag!r}"
            )
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

    archived = version_doi is not None
    if archived:
        if not isinstance(version_doi, str) or re.fullmatch(
            DOI_PATTERN, version_doi
        ) is None:
            errors.append(".release-record.json: invalid version_doi")
        if not isinstance(release_commit, str) or re.fullmatch(
            COMMIT_PATTERN, release_commit
        ) is None:
            errors.append(".release-record.json: invalid release_commit")
        if not isinstance(assets, dict) or set(assets) != set(EXPECTED_ASSETS):
            errors.append(".release-record.json: invalid asset set")
        else:
            for name in EXPECTED_ASSETS:
                digest = assets.get(name)
                if not isinstance(digest, str) or re.fullmatch(
                    SHA256_PATTERN, digest
                ) is None:
                    errors.append(
                        f".release-record.json: invalid SHA-256 for {name}"
                    )
        if not isinstance(archive, dict):
            errors.append(".release-record.json: invalid zenodo_archive")
        else:
            filename = archive.get("filename")
            archive_sha256 = archive.get("sha256")
            file_count = archive.get("file_count")
            if not isinstance(filename, str) or not filename.endswith(".zip"):
                errors.append(
                    ".release-record.json: invalid archive filename"
                )
            if not isinstance(archive_sha256, str) or re.fullmatch(
                SHA256_PATTERN, archive_sha256
            ) is None:
                errors.append(
                    ".release-record.json: invalid archive SHA-256"
                )
            if (
                not isinstance(file_count, int)
                or isinstance(file_count, bool)
                or file_count <= 0
            ):
                errors.append(
                    ".release-record.json: invalid archive file_count"
                )
    else:
        if release_commit is not None:
            errors.append(
                ".release-record.json: release_commit must be null "
                "before archival"
            )
        if not isinstance(assets, dict) or set(assets) != set(EXPECTED_ASSETS):
            errors.append(".release-record.json: invalid asset set")
        elif any(assets.get(name) is not None for name in EXPECTED_ASSETS):
            errors.append(
                ".release-record.json: asset hashes must be null "
                "before archival"
            )
        expected_archive = {
            "filename": None,
            "sha256": None,
            "file_count": None,
        }
        if archive != expected_archive:
            errors.append(
                ".release-record.json: archive fields must be null "
                "before archival"
            )

    required_dois: dict[str, tuple[Path, tuple[str, ...]]] = {
        "README.md": (
            required["readme"],
            (CONCEPT_DOI,),
        ),
        "PUBLICATION.md": (
            required["publication"],
            (CONCEPT_DOI,),
        ),
        "paper/ARXIV_METADATA.md": (
            required["arxiv"],
            (CONCEPT_DOI,),
        ),
    }
    if isinstance(version_doi, str):
        required_dois["CITATION.cff"] = (
            required["citation"],
            (version_doi, version_doi),
        )
        for name in ("README.md", "PUBLICATION.md", "paper/ARXIV_METADATA.md"):
            path, dois = required_dois[name]
            required_dois[name] = (path, dois + (version_doi,))
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

    release_facing: dict[str, Path] = {
        ".zenodo.json": required["zenodo"],
        "CITATION.cff": required["citation"],
        "README.md": required["readme"],
        "PUBLICATION.md": required["publication"],
        "paper/ARXIV_METADATA.md": required["arxiv"],
    }
    allowed_dois = {CONCEPT_DOI}
    if isinstance(version_doi, str):
        allowed_dois.add(version_doi)
    for name, path in release_facing.items():
        text = path.read_text(encoding="utf-8")
        for doi in set(re.findall(DOI_PATTERN, text)):
            if doi not in allowed_dois:
                errors.append(f"{name}: contains unrecognized Zenodo DOI {doi}")

    if archived and isinstance(assets, dict) and isinstance(archive, dict):
        publication = required["publication"].read_text(encoding="utf-8")
        expected_lines = (
            f"- Version DOI: `{version_doi}`",
            f"- Release commit: `{release_commit}`",
            *(
                f"- `{name}`: `{assets.get(name)}`"
                for name in EXPECTED_ASSETS
            ),
            f"- Zenodo archive: `{archive.get('filename')}`",
            f"- Zenodo archive SHA-256: `{archive.get('sha256')}`",
            f"- Archived file count: `{archive.get('file_count')}`",
        )
        for line in expected_lines:
            if line not in publication:
                errors.append(
                    f"PUBLICATION.md: missing archival record line: {line}"
                )

    if errors:
        for error in errors:
            print(f"release metadata error: {error}", file=sys.stderr)
        return 1

    print(f"release metadata consistent for v{citation_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
