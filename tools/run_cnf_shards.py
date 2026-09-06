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


EXPECTED_PARENT = list(range(1, 15))
EXPECTED_SCOPE = "exhaustive and disjoint within the coprime symmetry case"


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


def check_output_directory(parser: argparse.ArgumentParser, path: Path) -> None:
    if path.exists():
        if not path.is_dir():
            parser.error(f"output path is not a directory: {path}")
        if any(path.iterdir()):
            parser.error(f"output directory must be empty: {path}")
    path.mkdir(parents=True, exist_ok=True)


def paths_overlap(left: Path, right: Path) -> bool:
    left = left.resolve()
    right = right.resolve()
    return left == right or left in right.parents or right in left.parents


def expected_shard_names(coordinates: list[int]) -> list[str]:
    return [
        "-".join(
            f"c{coordinate:02d}a{choice:02d}"
            for coordinate, choice in zip(coordinates, choices)
        )
        + ".cnf"
        for choices in itertools.product(
            range(15),
            repeat=len(coordinates),
        )
    ]


def load_corpus(
    parser: argparse.ArgumentParser,
    input_dir: Path,
) -> tuple[Path, dict[str, object], list[Path]]:
    if not input_dir.is_dir():
        parser.error("the input path is not a directory")
    manifest_path = input_dir / "manifest.json"
    if not manifest_path.is_file():
        parser.error("the input directory has no manifest.json")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        parser.error(f"invalid shard manifest: {error}")
    if not isinstance(manifest, dict):
        parser.error("the shard manifest must be a JSON object")

    expected_fields = {
        "case": "coprime",
        "choices_per_coordinate": 15,
        "format_version": 1,
        "k": 14,
        "level": 15,
        "p": 29,
        "parent": EXPECTED_PARENT,
        "partition_scope": EXPECTED_SCOPE,
    }
    for field, expected_value in expected_fields.items():
        if manifest.get(field) != expected_value:
            parser.error(f"the shard manifest has invalid {field!r}")

    coordinates = manifest.get("coordinates")
    if (
        not isinstance(coordinates, list)
        or not coordinates
        or any(
            isinstance(coordinate, bool) or not isinstance(coordinate, int)
            for coordinate in coordinates
        )
        or len(set(coordinates)) != len(coordinates)
        or any(not 2 <= coordinate <= 14 for coordinate in coordinates)
    ):
        parser.error("the shard manifest has invalid coordinates")

    entries = manifest.get("shards")
    expected = manifest.get("expected_shards")
    expected_count = 15 ** len(coordinates)
    if (
        not isinstance(entries, list)
        or expected != expected_count
        or len(entries) != expected_count
    ):
        parser.error("the shard manifest has an invalid expected count")

    expected_names = expected_shard_names(coordinates)
    listed: list[Path] = []
    declared_names: list[str] = []
    input_root = input_dir.resolve()
    for entry, expected_name in zip(entries, expected_names):
        if not isinstance(entry, dict):
            parser.error("the shard manifest contains an invalid entry")
        name = entry.get("file")
        digest = entry.get("sha256")
        if (
            not isinstance(name, str)
            or name != expected_name
            or Path(name).is_absolute()
            or Path(name).name != name
            or not isinstance(digest, str)
            or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
        ):
            parser.error("the shard manifest entry is incomplete")
        path = (input_dir / name).resolve()
        if path.parent != input_root:
            parser.error(f"shard path escapes the input directory: {name}")
        if not path.is_file() or sha256(path) != digest:
            parser.error(f"shard does not match its manifest: {name}")
        declared_names.append(name)
        listed.append(path)

    actual = sorted(path.name for path in input_dir.glob("*.cnf"))
    if actual != sorted(declared_names):
        parser.error("the input directory contains undeclared or missing CNFs")
    return manifest_path, manifest, listed


def run_checker(
    name: str,
    command: list[str],
    log: Path,
) -> dict[str, object]:
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    log.write_text(completed.stdout, encoding="utf-8")
    verified = completed.returncode == 0 and any(
        line.strip() == "s VERIFIED"
        for line in completed.stdout.splitlines()
    )
    return {
        "exit_code": completed.returncode,
        "log": log.name,
        "log_sha256": sha256(log),
        "name": name,
        "verified": verified,
    }


def run_one(
    solver: Path,
    drat_trim: Path,
    rate: Path,
    cnf: Path,
    log_dir: Path,
    proof_dir: Path,
    checker_log_dir: Path,
) -> tuple[dict[str, object], float]:
    solver_log = log_dir / f"{cnf.stem}.solver.log"
    proof = proof_dir / f"{cnf.stem}.drat"
    command = [str(solver), str(cnf), str(proof)]

    started = time.monotonic()
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    seconds = time.monotonic() - started
    solver_log.write_text(completed.stdout, encoding="utf-8")

    result: dict[str, object] = {
        "cnf": cnf.name,
        "cnf_sha256": sha256(cnf),
        "solver_exit_code": completed.returncode,
        "solver_log": solver_log.name,
        "solver_log_sha256": sha256(solver_log),
    }
    if completed.returncode == 10:
        result["status"] = "SAT"
        return result, seconds
    if completed.returncode != 20 or not proof.is_file():
        result["status"] = "ERROR"
        return result, seconds

    result["proof"] = proof.name
    result["proof_bytes"] = proof.stat().st_size
    result["proof_format"] = "DRAT"
    result["proof_sha256"] = sha256(proof)
    checker_results = [
        run_checker(
            "drat-trim",
            [str(drat_trim), str(cnf), str(proof)],
            checker_log_dir / f"{cnf.stem}.drat-trim.log",
        ),
        run_checker(
            "rate",
            [
                str(rate),
                "--skip-unit-deletions",
                str(cnf),
                str(proof),
            ],
            checker_log_dir / f"{cnf.stem}.rate.log",
        ),
    ]
    result["checkers"] = checker_results
    result["status"] = (
        "VERIFIED_UNSAT"
        if all(bool(checker["verified"]) for checker in checker_results)
        else "UNVERIFIED_UNSAT"
    )
    return result, seconds


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solver", type=Path, required=True)
    parser.add_argument("--drat-trim", type=Path, required=True)
    parser.add_argument("--rate", type=Path, required=True)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--log-dir", type=Path, required=True)
    parser.add_argument("--proof-dir", type=Path, required=True)
    parser.add_argument("--checker-log-dir", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()

    if args.jobs < 1:
        parser.error("--jobs must be positive")
    for name in ("solver", "drat_trim", "rate"):
        path = getattr(args, name)
        if not path.is_file():
            parser.error(f"{name.replace('_', '-')} path is not a file")

    manifest_path, manifest, cnfs = load_corpus(parser, args.input_dir)
    output_dirs = [
        args.log_dir,
        args.proof_dir,
        args.checker_log_dir,
    ]
    for left_index, left in enumerate(output_dirs):
        if paths_overlap(left, args.input_dir):
            parser.error("output directories must not overlap the input corpus")
        for right in output_dirs[left_index + 1 :]:
            if paths_overlap(left, right):
                parser.error("output directories must not overlap")
    if paths_overlap(args.summary, args.input_dir):
        parser.error("the summary path must not overlap the input corpus")
    if any(
        args.summary.resolve() == output_dir.resolve()
        or output_dir.resolve() in args.summary.resolve().parents
        for output_dir in output_dirs
    ):
        parser.error("the summary path must be outside output directories")
    if args.summary.exists():
        parser.error("the summary path already exists")

    tool_paths = {
        "solver": args.solver,
        "drat-trim": args.drat_trim,
        "rate": args.rate,
    }
    tool_hashes_before = {
        name: sha256(path)
        for name, path in tool_paths.items()
    }
    solver_version = command_output([str(args.solver), "--version"])

    check_output_directory(parser, args.log_dir)
    check_output_directory(parser, args.proof_dir)
    check_output_directory(parser, args.checker_log_dir)
    args.summary.parent.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, object]] = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=args.jobs
    ) as executor:
        futures = [
            executor.submit(
                run_one,
                args.solver,
                args.drat_trim,
                args.rate,
                cnf,
                args.log_dir,
                args.proof_dir,
                args.checker_log_dir,
            )
            for cnf in cnfs
        ]
        for future in concurrent.futures.as_completed(futures):
            result, seconds = future.result()
            results.append(result)
            print(
                f"{result['cnf']}: {result['status']} in {seconds:.3f}s",
                flush=True,
            )

    results.sort(key=lambda result: str(result["cnf"]))
    tool_hashes_after = {
        name: sha256(path)
        for name, path in tool_paths.items()
    }
    tools_unchanged = tool_hashes_before == tool_hashes_after
    summary = {
        "checkers": {
            "drat-trim": {
                "sha256_after": tool_hashes_after["drat-trim"],
                "sha256_before": tool_hashes_before["drat-trim"],
            },
            "rate": {
                "sha256_after": tool_hashes_after["rate"],
                "sha256_before": tool_hashes_before["rate"],
            },
        },
        "format_version": 1,
        "input_manifest": manifest_path.name,
        "input_manifest_sha256": sha256(manifest_path),
        "partition_case": manifest.get("case"),
        "partition_scope": manifest.get("partition_scope"),
        "proof_format": "DRAT",
        "shards": results,
        "solver": {
            "sha256_after": tool_hashes_after["solver"],
            "sha256_before": tool_hashes_before["solver"],
            "version": solver_version,
        },
        "tools_unchanged_during_run": tools_unchanged,
    }
    args.summary.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
    )

    statuses = {str(result["status"]) for result in results}
    if statuses == {"VERIFIED_UNSAT"} and tools_unchanged:
        print(
            f"all {len(results)} shard proofs are independently verified",
            flush=True,
        )
        return 0
    if not tools_unchanged:
        print("a solver or checker changed during the run", flush=True)
        return 1
    if "SAT" in statuses:
        print("at least one shard is SAT", flush=True)
        return 10
    print(f"incomplete certificate statuses: {sorted(statuses)}", flush=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
