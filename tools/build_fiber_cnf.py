#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lrc15.base import generate_level_one
from lrc15.cnf import FiberEncoding, add_p29_level15_symmetry_case
from lrc15.model import GateModel


def parse_row(value: str) -> tuple[int, ...]:
    return tuple(int(token) for token in value.split(","))


def parse_fix(value: str) -> tuple[int, int]:
    try:
        coordinate, choice = value.split(":", maxsplit=1)
        return int(coordinate), int(choice)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "fixed choices must use COORDINATE:CHOICE"
        ) from error


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, required=True)
    parser.add_argument("--prime", type=int, required=True)
    parser.add_argument("--level", type=int, default=1)
    parser.add_argument("--multiplier", type=int, required=True)
    parser.add_argument("--row", type=parse_row)
    parser.add_argument(
        "--symmetry-case",
        choices=("coprime", "noncoprime"),
    )
    parser.add_argument(
        "--p29-reduced-cover",
        action="store_true",
        help=(
            "encode the 196 nontrivial CRT cells plus the mandatory-zero "
            "clause, without gcd constraints"
        ),
    )
    parser.add_argument(
        "--fix",
        action="append",
        type=parse_fix,
        default=[],
        metavar="COORDINATE:CHOICE",
        help="fix a one-based coordinate to a zero-based lift choice",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.level < 1:
        parser.error("--level must be positive")
    if args.multiplier < 1:
        parser.error("--multiplier must be positive")

    model = GateModel(k=args.k, prime=args.prime)
    if args.row is None:
        if args.level != 1:
            parser.error("--row is required above level one")
        rows = generate_level_one(model)
        if len(rows) != 1:
            parser.error(
                "automatic row selection requires exactly one level-one orbit"
            )
        row = next(iter(rows))
    else:
        row = args.row

    encoding = FiberEncoding(
        model=model,
        parent=row,
        level=args.level,
        multiplier=args.multiplier,
    )
    if args.p29_reduced_cover:
        if args.symmetry_case != "coprime":
            parser.error(
                "--p29-reduced-cover requires --symmetry-case coprime"
            )
        cnf = encoding.build_p29_level15_reduced_time_cover()
    else:
        cnf = encoding.build()
    if args.symmetry_case is not None:
        add_p29_level15_symmetry_case(cnf, encoding, args.symmetry_case)
    for coordinate, choice in args.fix:
        if not 1 <= coordinate <= args.k:
            parser.error(f"fixed coordinate {coordinate} is out of range")
        if not 0 <= choice < args.multiplier:
            parser.error(f"fixed choice {choice} is out of range")
        cnf.add([encoding.variable(coordinate - 1, choice)])
    comments = [
        (
            "Lonely Runner reduced p29 time-cover query"
            if args.p29_reduced_cover
            else "Lonely Runner exact improper-fiber query"
        ),
        f"k={args.k}",
        f"p={args.prime}",
        f"input_level={args.level}",
        f"multiplier={args.multiplier}",
        "parent=" + " ".join(map(str, row)),
        (
            "SAT means a lifted row covers every folded time class"
            if args.p29_reduced_cover
            else (
                "SAT means an improper lifted row satisfying every "
                "listed constraint exists"
            )
        ),
        "UNSAT excludes only the listed symmetry case and fixed choices",
    ]
    if args.p29_reduced_cover:
        comments.extend(
            [
                "crt_nontrivial_time_classes=196",
                "mandatory_zero_time=29",
                "gcd_constraints=omitted",
            ]
        )
    if args.symmetry_case is not None:
        comments.append(f"symmetry_case={args.symmetry_case}")
    for coordinate, choice in args.fix:
        comments.append(f"fixed_choice={coordinate}:{choice}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(cnf.dimacs(comments), encoding="ascii")
    print(
        f"wrote {args.output} with {cnf.variables} variables "
        f"and {len(cnf.clauses)} clauses"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
