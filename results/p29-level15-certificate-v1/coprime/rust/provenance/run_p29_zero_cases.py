#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ZERO_COORDINATES = tuple(range(2, 15))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def command_output(
    command: list[str],
    *,
    cwd: Path | None = None,
) -> str:
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
        cwd=cwd,
    )
    return completed.stdout.strip()


def exact_field(output: str, name: str) -> list[str]:
    prefix = f"{name} "
    return [
        line[len(prefix) :]
        for line in output.splitlines()
        if line.startswith(prefix)
    ]


def last_integer_field(output: str, name: str) -> int | None:
    values = exact_field(output, name)
    if not values:
        return None
    try:
        return int(values[-1])
    except ValueError:
        return None


def run_one(
    solver: Path,
    coordinate: int,
    log_dir: Path,
) -> tuple[dict[str, object], float]:
    lift_choice = coordinate
    log = log_dir / f"zero-c{coordinate:02d}.log"
    started = time.monotonic()
    completed = subprocess.run(
        [
            str(solver),
            "coprime-cover",
            f"{coordinate}:{lift_choice}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    seconds = time.monotonic() - started
    log.write_text(completed.stdout, encoding="utf-8")

    expected_fields = {
        "case": ["coprime"],
        "constraint_mode": ["time-cover-only"],
        "fixed": [f"{coordinate}:{lift_choice}"],
        "status": ["UNSAT"],
    }
    fields_match = all(
        exact_field(completed.stdout, name) == expected
        for name, expected in expected_fields.items()
    )
    status = (
        "UNSAT"
        if completed.returncode == 20 and fields_match
        else "ERROR"
    )
    return (
        {
            "coordinate": coordinate,
            "domain_branches": last_integer_field(
                completed.stdout,
                "domain_branches",
            ),
            "exit_code": completed.returncode,
            "lift_choice": lift_choice,
            "log": log.name,
            "log_sha256": sha256(log),
            "nodes": last_integer_field(completed.stdout, "nodes"),
            "propagations": last_integer_field(
                completed.stdout,
                "propagations",
            ),
            "status": status,
        },
        seconds,
    )


def paths_overlap(left: Path, right: Path) -> bool:
    left = left.resolve()
    right = right.resolve()
    return left == right or left in right.parents or right in left.parents


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solver", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--implementation", required=True)
    parser.add_argument("--log-dir", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()

    if args.jobs < 1:
        parser.error("--jobs must be positive")
    if not args.solver.is_file():
        parser.error("the solver path is not a file")
    if not args.source.is_file():
        parser.error("the source path is not a file")
    if not args.implementation.strip():
        parser.error("--implementation must not be empty")
    if args.summary.exists():
        parser.error("the summary path already exists")
    if paths_overlap(args.summary, args.log_dir):
        parser.error("the summary path must be outside the log directory")
    if args.log_dir.exists():
        if not args.log_dir.is_dir():
            parser.error("the log path is not a directory")
        if any(args.log_dir.iterdir()):
            parser.error("the log directory must be empty")

    git_head_before = command_output(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
    )
    git_status_before = command_output(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=ROOT,
    )
    if len(git_head_before) != 40 or git_status_before:
        parser.error(
            "the tracked worktree must be clean at a committed revision"
        )

    runner = Path(__file__).resolve()
    makefile = ROOT / "Makefile"
    provenance_paths = {
        "makefile": makefile,
        "runner": runner,
        "solver": args.solver,
        "source": args.source,
    }
    hashes_before = {
        name: sha256(path)
        for name, path in provenance_paths.items()
    }
    solver_version = command_output([str(args.solver), "--version"])

    args.log_dir.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, object]] = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=args.jobs
    ) as executor:
        futures = [
            executor.submit(
                run_one,
                args.solver,
                coordinate,
                args.log_dir,
            )
            for coordinate in ZERO_COORDINATES
        ]
        for future in concurrent.futures.as_completed(futures):
            result, seconds = future.result()
            results.append(result)
            print(
                f"zero coordinate {result['coordinate']}: "
                f"{result['status']} in {seconds:.3f}s",
                flush=True,
            )
    results.sort(key=lambda result: int(result["coordinate"]))

    hashes_after = {
        name: sha256(path)
        for name, path in provenance_paths.items()
    }
    git_head_after = command_output(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
    )
    git_status_after = command_output(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=ROOT,
    )
    provenance_unchanged = hashes_before == hashes_after
    repository_unchanged = (
        git_head_before == git_head_after
        and not git_status_before
        and not git_status_after
    )
    summary = {
        "case_coverage": (
            "every coprime time cover has a zero residue modulo 15; "
            "the listed coordinate-zero cases cover all possibilities"
        ),
        "cases_are_disjoint": False,
        "expected_cases": len(ZERO_COORDINATES),
        "format_version": 1,
        "implementation": args.implementation,
        "log_directory": args.log_dir.name,
        "parameters": {
            "k": 14,
            "level": 15,
            "p": 29,
            "parent": list(range(1, 15)),
            "symmetry_case": "coprime",
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
        "repository": {
            "head_after": git_head_after,
            "head_before": git_head_before,
            "tracked_worktree_clean_after": not git_status_after,
            "tracked_worktree_clean_before": not git_status_before,
            "unchanged_during_run": repository_unchanged,
        },
        "results": results,
        "solver_version": solver_version,
        "theorem_scope": (
            "no level-15 lift in the coprime symmetry case covers "
            "all folded time classes"
        ),
    }
    args.summary.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
    )

    statuses = {str(result["status"]) for result in results}
    if (
        statuses == {"UNSAT"}
        and len(results) == len(ZERO_COORDINATES)
        and provenance_unchanged
        and repository_unchanged
    ):
        print(
            "all 13 coordinate-zero cases are UNSAT",
            flush=True,
        )
        return 0
    if not provenance_unchanged:
        print("a provenance file changed during the run", flush=True)
    if not repository_unchanged:
        print("the source repository changed during the run", flush=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
