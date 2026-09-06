#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lrc15.cnf import FiberEncoding, add_p29_level15_symmetry_case
from lrc15.model import GateModel


def parse_coordinates(value: str) -> tuple[int, ...]:
    try:
        coordinates = tuple(int(token) for token in value.split(","))
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "coordinates must be a comma-separated integer list"
        ) from error
    if not coordinates:
        raise argparse.ArgumentTypeError("at least one coordinate is required")
    return coordinates


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--coordinates",
        type=parse_coordinates,
        default=(2,),
        help="one-based coordinates used for the exhaustive partition",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    if len(set(args.coordinates)) != len(args.coordinates):
        parser.error("shard coordinates must be distinct")
    if any(not 2 <= coordinate <= 14 for coordinate in args.coordinates):
        parser.error("every shard coordinate must be between 2 and 14")

    model = GateModel(k=14, prime=29)
    parent = tuple(range(1, 15))
    encoding = FiberEncoding(
        model=model,
        parent=parent,
        level=1,
        multiplier=15,
    )
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        parser.error("the output directory must be empty")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    shards: list[dict[str, str]] = []
    for choices in product(range(15), repeat=len(args.coordinates)):
        cnf = encoding.build()
        add_p29_level15_symmetry_case(cnf, encoding, "coprime")
        for coordinate, choice in zip(args.coordinates, choices):
            cnf.add([encoding.variable(coordinate - 1, choice)])
        fixed = [
            f"{coordinate}:{choice}"
            for coordinate, choice in zip(args.coordinates, choices)
        ]
        comments = [
            "Lonely Runner p29 level-15 coprime symmetry shard",
            "k=14",
            "p=29",
            "input_level=1",
            "multiplier=15",
            "parent=" + " ".join(map(str, parent)),
            "symmetry_case=coprime",
            *(f"fixed_choice={value}" for value in fixed),
            "this shard belongs only to the coprime symmetry case",
            "all assignments over the listed coordinates form an exhaustive disjoint partition",
        ]
        name = "-".join(
            f"c{coordinate:02d}a{choice:02d}"
            for coordinate, choice in zip(args.coordinates, choices)
        )
        output = (
            args.output_dir
            / f"{name}.cnf"
        )
        output.write_text(cnf.dimacs(comments), encoding="ascii")
        shards.append(
            {
                "file": output.name,
                "sha256": sha256(output),
            }
        )
        print(
            f"wrote {output} with {cnf.variables} variables "
            f"and {len(cnf.clauses)} clauses"
        )

    manifest = {
        "case": "coprime",
        "choices_per_coordinate": 15,
        "coordinates": list(args.coordinates),
        "expected_shards": 15 ** len(args.coordinates),
        "format_version": 1,
        "k": 14,
        "level": 15,
        "p": 29,
        "parent": list(parent),
        "partition_scope": (
            "exhaustive and disjoint within the coprime symmetry case"
        ),
        "shards": shards,
    }
    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
    )
    print(f"wrote {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
