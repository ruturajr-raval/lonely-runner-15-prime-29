#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lrc15.p29_certificate import (
    P29_ZERO_COORDINATES,
    sha256,
    validate_dual_summary,
    validate_zero_summary,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if len(args.summary) < 2:
        parser.error("at least two independent summaries are required")
    if args.output.exists():
        parser.error("the output path already exists")

    summaries = [
        (path, validate_zero_summary(path))
        for path in args.summary
    ]
    implementations = [
        summary.get("implementation")
        for _, summary in summaries
    ]
    source_hashes = [
        summary["provenance"]["source"]["sha256_before"]
        for _, summary in summaries
    ]
    if len(set(implementations)) != len(implementations):
        parser.error("implementation labels must be distinct")
    if len(set(source_hashes)) != len(source_hashes):
        parser.error("source hashes must be distinct")

    result = {
        "format_version": 1,
        "independent_implementations": [
            {
                "implementation": summary["implementation"],
                "source_sha256": summary["provenance"]["source"][
                    "sha256_before"
                ],
                "summary": path.name,
                "summary_sha256": sha256(path),
            }
            for path, summary in summaries
        ],
        "status": "VERIFIED_UNSAT",
        "theorem_scope": (
            "no level-15 lift in the coprime symmetry case covers "
            "all folded time classes"
        ),
        "zero_case_coverage": list(P29_ZERO_COORDINATES),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
    )
    validate_dual_summary(args.output, summaries)
    print(
        f"verified {len(summaries)} independent zero-case summaries",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
