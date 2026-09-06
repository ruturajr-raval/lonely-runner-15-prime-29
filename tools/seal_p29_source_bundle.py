#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lrc15.p29_certificate import is_git_sha, sha256


SOURCE_BUNDLE_PATH = Path("provenance/source-commit.bundle")


def artifact_manifest(root: Path) -> dict[str, dict[str, object]]:
    return {
        path.relative_to(root).as_posix(): {
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in sorted(root.rglob("*"))
        if path.is_file() and path != root / "certificate.json"
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate-dir", type=Path, required=True)
    args = parser.parse_args()

    certificate_path = args.certificate_dir / "certificate.json"
    if not certificate_path.is_file():
        parser.error("missing certificate.json")
    certificate = json.loads(certificate_path.read_text(encoding="ascii"))
    source_commit = certificate.get("source_commit")
    if not is_git_sha(source_commit):
        parser.error("certificate source commit is invalid")
    if certificate.get("source_bundle") is not None:
        parser.error("certificate already declares a source bundle")

    output = args.certificate_dir / SOURCE_BUNDLE_PATH
    if output.exists():
        parser.error("source bundle output already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    reference = f"refs/p29-certificate/{source_commit}"
    created = False
    try:
        subprocess.run(
            ["git", "update-ref", reference, source_commit],
            cwd=ROOT,
            check=True,
        )
        created = True
        subprocess.run(
            ["git", "bundle", "create", str(output), reference],
            cwd=ROOT,
            check=True,
        )
    finally:
        if created:
            subprocess.run(
                ["git", "update-ref", "-d", reference],
                cwd=ROOT,
                check=True,
            )

    certificate["source_bundle"] = SOURCE_BUNDLE_PATH.as_posix()
    certificate["artifacts"] = artifact_manifest(args.certificate_dir)
    certificate_path.write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
