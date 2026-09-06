#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import io
import subprocess
import sys
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CERTIFICATE = ROOT / "results" / "p29-level15-certificate-v1"
ARCHIVE_ROOT = Path("lonely-runner-15-prime-29-certificate-v1")
ARCHIVE_CERTIFICATE = ARCHIVE_ROOT / "results" / CERTIFICATE.name


def add_bytes(
    archive: tarfile.TarFile,
    relative: Path,
    data: bytes,
) -> None:
    info = tarfile.TarInfo(relative.as_posix())
    info.size = len(data)
    info.mode = 0o644
    info.mtime = 0
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    archive.addfile(info, io.BytesIO(data))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if not (CERTIFICATE / "certificate.json").is_file():
        parser.error("the selected certificate is missing")
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "verify_p29_certificate.py"),
            "--certificate-dir",
            str(CERTIFICATE),
        ],
        cwd=ROOT,
        check=True,
    )

    members: list[tuple[Path, Path]] = [
        (ROOT / "LICENSE", ARCHIVE_ROOT / "LICENSE"),
        (
            ROOT / "docs" / "CERTIFICATE_ARCHIVE_README.md",
            ARCHIVE_ROOT / "README.md",
        ),
        (
            ROOT / "tools" / "verify_p29_certificate.py",
            ARCHIVE_ROOT / "tools" / "verify_p29_certificate.py",
        ),
    ]
    members.extend(
        (
            source,
            ARCHIVE_ROOT / "src" / "lrc15" / source.name,
        )
        for source in sorted((ROOT / "src" / "lrc15").glob("*.py"))
    )
    members.extend(
        (
            source,
            ARCHIVE_CERTIFICATE / source.relative_to(CERTIFICATE),
        )
        for source in sorted(CERTIFICATE.rglob("*"))
        if source.is_file()
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    buffer = io.BytesIO()
    with tarfile.open(
        fileobj=buffer,
        mode="w",
        format=tarfile.PAX_FORMAT,
    ) as archive:
        for source, relative in members:
            add_bytes(archive, relative, source.read_bytes())

    with args.output.open("wb") as raw:
        with gzip.GzipFile(
            filename="",
            mode="wb",
            fileobj=raw,
            mtime=0,
        ) as compressed:
            compressed.write(buffer.getvalue())
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
