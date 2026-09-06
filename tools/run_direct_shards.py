#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import itertools
import json
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_coordinates(value: str) -> tuple[int, ...]:
    if value == "none":
        return ()
    try:
        coordinates = tuple(int(token) for token in value.split(","))
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "coordinates must be a comma-separated integer list"
        ) from error
    return coordinates


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def command_output(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    return completed.stdout.strip()


def paths_overlap(left: Path, right: Path) -> bool:
    left = left.resolve()
    right = right.resolve()
    return left == right or left in right.parents or right in left.parents


def run_one(
    solver: Path,
    symmetry_case: str,
    coordinates: tuple[int, ...],
    choices: tuple[int, ...],
    log_dir: Path,
) -> tuple[dict[str, object], float]:
    fixed = [
        f"{coordinate}:{choice}"
        for coordinate, choice in zip(coordinates, choices)
    ]
    name = "-".join(
        f"c{coordinate:02d}a{choice:02d}"
        for coordinate, choice in zip(coordinates, choices)
    ) or "unsharded"
    log = log_dir / f"{name}.log"
    started = time.monotonic()
    completed = subprocess.run(
        [str(solver), symmetry_case, *fixed],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    seconds = time.monotonic() - started
    log.write_text(completed.stdout, encoding="utf-8")
    status = {
        10: "SAT",
        20: "UNSAT",
    }.get(completed.returncode, "ERROR")
    result = {
        "choices": list(choices),
        "coordinates": list(coordinates),
        "exit_code": completed.returncode,
        "log": log.name,
        "log_sha256": sha256(log),
        "status": status,
    }
    return result, seconds


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solver", type=Path, required=True)
    parser.add_argument(
        "--case",
        choices=("coprime", "noncoprime"),
        required=True,
    )
    parser.add_argument(
        "--coordinates",
        type=parse_coordinates,
        default=(2, 3),
    )
    parser.add_argument("--log-dir", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()

    if len(set(args.coordinates)) != len(args.coordinates):
        parser.error("coordinates must be distinct")
    if any(not 2 <= coordinate <= 14 for coordinate in args.coordinates):
        parser.error("coordinates must be between 2 and 14")
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    if not args.solver.is_file():
        parser.error("the solver path is not a file")

    if args.summary.exists():
        parser.error("the summary path already exists")
    if paths_overlap(args.summary, args.log_dir):
        parser.error("the summary path must be outside the log directory")
    if args.log_dir.exists():
        if not args.log_dir.is_dir():
            parser.error("the log path is not a directory")
        if any(args.log_dir.iterdir()):
            parser.error("the log directory must be empty")

    source = ROOT / "tools" / "solve_p29_level15.cpp"
    runner = Path(__file__).resolve()
    makefile = ROOT / "Makefile"
    provenance_paths = {
        "makefile": makefile,
        "runner": runner,
        "solver": args.solver,
        "source": source,
    }
    hashes_before = {
        name: sha256(path)
        for name, path in provenance_paths.items()
    }
    solver_version = command_output([str(args.solver), "--version"])

    args.log_dir.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    tasks = list(
        itertools.product(range(15), repeat=len(args.coordinates))
    )
    results: list[dict[str, object]] = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=args.jobs
    ) as executor:
        futures = [
            executor.submit(
                run_one,
                args.solver,
                args.case,
                args.coordinates,
                choices,
                args.log_dir,
            )
            for choices in tasks
        ]
        for future in concurrent.futures.as_completed(futures):
            result, seconds = future.result()
            results.append(result)
            fixed = ",".join(
                f"{coordinate}:{choice}"
                for coordinate, choice in zip(
                    result["coordinates"],
                    result["choices"],
                )
            )
            print(
                f"{fixed}: {result['status']} "
                f"in {seconds:.3f}s",
                flush=True,
            )

    results.sort(key=lambda result: tuple(result["choices"]))
    hashes_after = {
        name: sha256(path)
        for name, path in provenance_paths.items()
    }
    provenance_unchanged = hashes_before == hashes_after
    args.summary.write_text(
        json.dumps(
            {
                "case": args.case,
                "coordinates": list(args.coordinates),
                "expected_shards": len(tasks),
                "format_version": 1,
                "partition_scope": (
                    f"exhaustive and disjoint within the {args.case} "
                    "symmetry case"
                ),
                "parameters": {
                    "k": 14,
                    "level": 15,
                    "p": 29,
                    "parent": list(range(1, 15)),
                },
                "provenance": {
                    name: {
                        "file": path.name,
                        "sha256_after": hashes_after[name],
                        "sha256_before": hashes_before[name],
                    }
                    for name, path in provenance_paths.items()
                },
                "provenance_unchanged_during_run": provenance_unchanged,
                "shards": results,
                "solver_version": solver_version,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="ascii",
    )
    statuses = {str(result["status"]) for result in results}
    if statuses == {"UNSAT"} and provenance_unchanged:
        print(
            f"all {len(results)} direct shards in the "
            f"{args.case} case are UNSAT",
            flush=True,
        )
        return 0
    if not provenance_unchanged:
        print("a provenance file changed during the run", flush=True)
        return 1
    if "SAT" in statuses:
        print("at least one direct shard is SAT", flush=True)
        return 10
    print(f"incomplete direct statuses: {sorted(statuses)}", flush=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
