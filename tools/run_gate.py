#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lrc15.base import generate_level_one
from lrc15.certificate import canonical_json, certificate_document
from lrc15.model import GateModel
from lrc15.pipeline import apply_pipeline


def parse_pipeline(value: str) -> list[int | str]:
    operations: list[int | str] = []
    for token in value.split(","):
        token = token.strip().lower()
        if token == "p":
            operations.append("p")
        else:
            multiplier = int(token)
            if multiplier < 2:
                raise argparse.ArgumentTypeError(
                    "lift multipliers must be at least 2"
                )
            operations.append(multiplier)
    return operations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, required=True)
    parser.add_argument("--prime", type=int, required=True)
    parser.add_argument(
        "--pipeline",
        type=parse_pipeline,
        required=True,
        help="comma-separated lift multipliers and p for projection",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    model = GateModel(k=args.k, prime=args.prime)
    level_one = generate_level_one(model)
    final_rows, final_level, stages = apply_pipeline(
        model, level_one, args.pipeline
    )
    document = certificate_document(
        k=args.k,
        prime=args.prime,
        pipeline=args.pipeline,
        level_one_rows=level_one,
        final_rows=final_rows,
        final_level=final_level,
        stages=stages,
    )
    text = canonical_json(document)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="ascii")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

