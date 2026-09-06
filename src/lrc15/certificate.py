from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from dataclasses import asdict

from .model import Row
from .pipeline import Stage


def rows_sha256(rows: Iterable[Row]) -> str:
    digest = hashlib.sha256()
    for row in sorted(rows):
        digest.update(" ".join(map(str, row)).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def certificate_document(
    *,
    k: int,
    prime: int,
    pipeline: list[int | str],
    level_one_rows: set[Row],
    final_rows: set[Row],
    final_level: int,
    stages: list[Stage],
) -> dict[str, object]:
    return {
        "schema": 1,
        "parameters": {"k": k, "prime": prime},
        "pipeline": pipeline,
        "level_one": {
            "rows": len(level_one_rows),
            "sha256": rows_sha256(level_one_rows),
        },
        "stages": [asdict(stage) for stage in stages],
        "final": {
            "level": final_level,
            "rows": len(final_rows),
            "sha256": rows_sha256(final_rows),
            "gate_closed": len(final_rows) == 0,
        },
    }


def canonical_json(document: dict[str, object]) -> str:
    return json.dumps(document, indent=2, sort_keys=True) + "\n"

