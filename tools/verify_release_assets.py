#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


EXPECTED_ASSETS = (
    "lonely-runner-15-prime-29-paper.pdf",
    "lonely-runner-15-prime-29-source.tar.gz",
    "lonely-runner-15-prime-29-certificate-v1.tar.gz",
    "SHA256SUMS",
)
CHECKSUM_ASSETS = EXPECTED_ASSETS[:-1]
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_checksums(path: Path) -> tuple[dict[str, str], list[str]]:
    entries: dict[str, str] = {}
    errors: list[str] = []
    if not path.is_file() or path.is_symlink():
        return entries, [f"missing regular file: {path}"]
    for line_number, line in enumerate(
        path.read_text(encoding="ascii").splitlines(),
        start=1,
    ):
        try:
            digest, name = line.split("  ", 1)
        except ValueError:
            errors.append(
                f"{path}:{line_number}: expected '<sha256>  <name>'"
            )
            continue
        if SHA256_PATTERN.fullmatch(digest) is None:
            errors.append(f"{path}:{line_number}: invalid SHA-256")
            continue
        relative = Path(name)
        if (
            relative.is_absolute()
            or len(relative.parts) != 1
            or relative.name != name
        ):
            errors.append(f"{path}:{line_number}: invalid asset name")
            continue
        if name in entries:
            errors.append(f"{path}:{line_number}: duplicate asset {name}")
            continue
        entries[name] = digest
    return entries, errors


def verify_release(root: Path) -> tuple[str, ...]:
    errors: list[str] = []
    release_dir = root / "dist" / "release"
    record_path = root / ".release-record.json"
    if not record_path.is_file() or record_path.is_symlink():
        return (f"missing release record: {record_path}",)
    try:
        record = json.loads(record_path.read_text(encoding="ascii"))
    except (OSError, json.JSONDecodeError) as error:
        return (f"invalid release record: {error}",)

    if not release_dir.is_dir() or release_dir.is_symlink():
        return (f"missing release directory: {release_dir}",)
    actual_names = {path.name for path in release_dir.iterdir()}
    if actual_names != set(EXPECTED_ASSETS):
        errors.append(
            "release directory entry mismatch: "
            f"expected={sorted(EXPECTED_ASSETS)} "
            f"found={sorted(actual_names)}"
        )

    assets = record.get("assets")
    if not isinstance(assets, dict) or set(assets) != set(EXPECTED_ASSETS):
        errors.append("release record has an invalid asset set")
        assets = {}

    for name in EXPECTED_ASSETS:
        path = release_dir / name
        if not path.is_file() or path.is_symlink():
            errors.append(f"missing regular file: {path}")
            continue
        expected = assets.get(name)
        actual = sha256_file(path)
        if expected != actual:
            errors.append(
                f"release record hash mismatch: {name}: "
                f"expected {expected}, found {actual}"
            )

    checksums, checksum_errors = parse_checksums(
        release_dir / "SHA256SUMS"
    )
    errors.extend(checksum_errors)
    if set(checksums) != set(CHECKSUM_ASSETS):
        errors.append(
            "checksum asset set mismatch: "
            f"expected={sorted(CHECKSUM_ASSETS)} "
            f"found={sorted(checksums)}"
        )
    for name, expected in checksums.items():
        path = release_dir / name
        if not path.is_file() or path.is_symlink():
            continue
        actual = sha256_file(path)
        if actual != expected:
            errors.append(
                f"checksum mismatch: {name}: expected {expected}, "
                f"found {actual}"
            )
    return tuple(errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args()
    errors = verify_release(args.root.resolve())
    if errors:
        for error in errors:
            print(f"release asset error: {error}", file=sys.stderr)
        return 1
    print("release assets and checksum manifest verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
