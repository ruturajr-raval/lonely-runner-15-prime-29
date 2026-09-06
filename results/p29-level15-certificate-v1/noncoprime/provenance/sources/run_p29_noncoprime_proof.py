#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lrc15.p29_certificate import (
    P29_PARENT,
    checker_verified,
    expected_noncoprime_cnf,
    sha256,
)


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


def run_checker(
    name: str,
    command: list[str],
    log: Path,
) -> dict[str, object]:
    started = time.monotonic()
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    seconds = time.monotonic() - started
    log.write_text(completed.stdout, encoding="utf-8")
    return {
        "exit_code": completed.returncode,
        "log": log.name,
        "log_sha256": sha256(log),
        "name": name,
        "seconds": seconds,
        "verified": (
            completed.returncode == 0
            and checker_verified(completed.stdout)
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solver", type=Path, required=True)
    parser.add_argument("--drat-trim", type=Path, required=True)
    parser.add_argument("--rate", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    tool_paths = {
        "drat-trim": args.drat_trim,
        "rate": args.rate,
        "solver": args.solver,
    }
    for name, path in tool_paths.items():
        if not path.is_file():
            parser.error(f"{name} path is not a file")
    if args.output_dir.exists():
        if not args.output_dir.is_dir():
            parser.error("the output path is not a directory")
        if any(args.output_dir.iterdir()):
            parser.error("the output directory must be empty")
    args.output_dir.mkdir(parents=True, exist_ok=True)

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
    source_paths = {
        "cnf": ROOT / "src" / "lrc15" / "cnf.py",
        "crt": ROOT / "src" / "lrc15" / "crt.py",
        "model": ROOT / "src" / "lrc15" / "model.py",
        "p29-certificate": (
            ROOT / "src" / "lrc15" / "p29_certificate.py"
        ),
        "runner": runner,
    }
    source_hashes_before = {
        name: sha256(path)
        for name, path in source_paths.items()
    }
    tool_hashes_before = {
        name: sha256(path)
        for name, path in tool_paths.items()
    }

    query = args.output_dir / "query.cnf"
    proof = args.output_dir / "proof.drat"
    solver_log = args.output_dir / "solver.log"
    drat_trim_log = args.output_dir / "drat-trim.log"
    rate_log = args.output_dir / "rate.log"
    summary_path = args.output_dir / "summary.json"

    cnf = expected_noncoprime_cnf()
    comments = [
        "Lonely Runner exact improper-fiber query",
        "k=14",
        "p=29",
        "input_level=1",
        "multiplier=15",
        "parent=" + " ".join(map(str, P29_PARENT)),
        "symmetry_case=noncoprime",
        "SAT means a normalized improper level-15 lift exists",
        "UNSAT excludes the complete noncoprime symmetry branch",
    ]
    query.write_text(cnf.dimacs(comments), encoding="ascii")

    solver_version = command_output([str(args.solver), "--version"])
    started = time.monotonic()
    completed = subprocess.run(
        [str(args.solver), str(query), str(proof)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    solver_seconds = time.monotonic() - started
    solver_log.write_text(completed.stdout, encoding="utf-8")

    checkers: list[dict[str, object]] = []
    if completed.returncode == 20 and proof.is_file():
        checkers = [
            run_checker(
                "drat-trim",
                [str(args.drat_trim), str(query), str(proof)],
                drat_trim_log,
            ),
            run_checker(
                "rate",
                [
                    str(args.rate),
                    "--skip-unit-deletions",
                    str(query),
                    str(proof),
                ],
                rate_log,
            ),
        ]

    source_hashes_after = {
        name: sha256(path)
        for name, path in source_paths.items()
    }
    tool_hashes_after = {
        name: sha256(path)
        for name, path in tool_paths.items()
    }
    git_head_after = command_output(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
    )
    git_status_after = command_output(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=ROOT,
    )
    provenance_unchanged = (
        source_hashes_before == source_hashes_after
        and tool_hashes_before == tool_hashes_after
    )
    repository_unchanged = (
        git_head_before == git_head_after
        and not git_status_before
        and not git_status_after
    )
    verified = (
        completed.returncode == 20
        and proof.is_file()
        and len(checkers) == 2
        and all(bool(checker["verified"]) for checker in checkers)
        and provenance_unchanged
        and repository_unchanged
    )

    summary = {
        "checkers": checkers,
        "format_version": 1,
        "parameters": {
            "k": 14,
            "level": 15,
            "p": 29,
            "parent": list(P29_PARENT),
            "symmetry_case": "noncoprime",
        },
        "proof": (
            {
                "bytes": proof.stat().st_size,
                "file": proof.name,
                "format": "DRAT",
                "sha256": sha256(proof),
            }
            if proof.is_file()
            else None
        ),
        "provenance": {
            "sources": {
                name: {
                    "file": path.name,
                    "sha256_after": source_hashes_after[name],
                    "sha256_before": source_hashes_before[name],
                }
                for name, path in source_paths.items()
            },
            "tools": {
                name: {
                    "file": path.name,
                    "sha256_after": tool_hashes_after[name],
                    "sha256_before": tool_hashes_before[name],
                }
                for name, path in tool_paths.items()
            },
            "unchanged_during_run": provenance_unchanged,
        },
        "query": {
            "clauses": len(cnf.clauses),
            "file": query.name,
            "sha256": sha256(query),
            "variables": cnf.variables,
        },
        "repository": {
            "head_after": git_head_after,
            "head_before": git_head_before,
            "tracked_worktree_clean_after": not git_status_after,
            "tracked_worktree_clean_before": not git_status_before,
            "unchanged_during_run": repository_unchanged,
        },
        "solver": {
            "exit_code": completed.returncode,
            "log": solver_log.name,
            "log_sha256": sha256(solver_log),
            "seconds": solver_seconds,
            "version": solver_version,
        },
        "status": "VERIFIED_UNSAT" if verified else "INCOMPLETE",
        "theorem_scope": (
            "no improper level-15 lift exists in the normalized "
            "noncoprime symmetry branch"
        ),
    }
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
    )

    if verified:
        print(
            "noncoprime branch is UNSAT and both proof checkers verified it",
            flush=True,
        )
        return 0
    print("noncoprime proof certificate is incomplete", flush=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
