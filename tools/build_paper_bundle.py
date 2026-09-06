#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import io
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER_FILES = (
    "paper/ARXIV_METADATA.md",
    "paper/README.md",
    "paper/RIGHTS.md",
    "paper/main.tex",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for relative in PAPER_FILES:
            source = ROOT / relative
            data = source.read_bytes()
            info = tarfile.TarInfo(relative)
            info.size = len(data)
            info.mode = 0o644
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            archive.addfile(info, io.BytesIO(data))

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
