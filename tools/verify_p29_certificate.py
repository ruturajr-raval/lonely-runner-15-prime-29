#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lrc15.p29_certificate import (
    P29_PARENT,
    P29_ZERO_COORDINATES,
    checker_verified,
    exact_fields,
    is_git_sha,
    is_sha256,
    sha256,
    validate_crt_reduction,
    validate_dual_summary,
    validate_level_one_orbit,
    validate_noncoprime_summary,
    validate_zero_summary,
)

SOURCE_BUNDLE_PATH = "provenance/source-commit.bundle"
SOURCE_BINDINGS = {
    "coprime/cpp/provenance/Makefile": "Makefile",
    "coprime/cpp/provenance/run_p29_zero_cases.py": (
        "tools/run_p29_zero_cases.py"
    ),
    "coprime/cpp/provenance/solve_p29_level15.cpp": (
        "tools/solve_p29_level15.cpp"
    ),
    "coprime/rust/provenance/Makefile": "Makefile",
    "coprime/rust/provenance/run_p29_zero_cases.py": (
        "tools/run_p29_zero_cases.py"
    ),
    "coprime/rust/provenance/verify_p29_level15.rs": (
        "tools/verify_p29_level15.rs"
    ),
    "noncoprime/provenance/sources/cnf.py": "src/lrc15/cnf.py",
    "noncoprime/provenance/sources/crt.py": "src/lrc15/crt.py",
    "noncoprime/provenance/sources/model.py": "src/lrc15/model.py",
    "noncoprime/provenance/sources/p29_certificate.py": (
        "src/lrc15/p29_certificate.py"
    ),
    "noncoprime/provenance/sources/run_p29_noncoprime_proof.py": (
        "tools/run_p29_noncoprime_proof.py"
    ),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_artifacts(
    certificate_dir: Path,
    declared: object,
) -> None:
    require(isinstance(declared, dict), "invalid artifact manifest")
    actual = {
        path.relative_to(certificate_dir).as_posix(): path
        for path in certificate_dir.rglob("*")
        if (
            path.is_file()
            and path != certificate_dir / "certificate.json"
        )
    }
    require(
        set(declared) == set(actual),
        "artifact manifest does not match the directory",
    )
    root = certificate_dir.resolve()
    for relative, entry in declared.items():
        require(
            isinstance(relative, str)
            and not Path(relative).is_absolute()
            and ".." not in Path(relative).parts,
            f"invalid artifact path: {relative}",
        )
        path = (certificate_dir / relative).resolve()
        require(
            root in path.parents,
            f"artifact path escapes the certificate: {relative}",
        )
        require(
            isinstance(entry, dict)
            and entry.get("bytes") == path.stat().st_size
            and is_sha256(entry.get("sha256"))
            and entry.get("sha256") == sha256(path),
            f"artifact metadata mismatch: {relative}",
        )


def validate_source_bundle(
    certificate_dir: Path,
    certificate: dict[str, object],
) -> None:
    require(
        certificate.get("source_bundle") == SOURCE_BUNDLE_PATH,
        "certificate source-bundle field mismatch",
    )
    bundle = certificate_dir / SOURCE_BUNDLE_PATH
    require(bundle.is_file(), "missing source commit bundle")
    git = shutil.which("git")
    require(git is not None, "git is required for source-bundle replay")
    source_commit = str(certificate["source_commit"])
    heads = subprocess.run(
        [git, "bundle", "list-heads", str(bundle.resolve())],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    head_lines = heads.stdout.splitlines()
    require(
        heads.returncode == 0
        and len(head_lines) == 1
        and head_lines[0].startswith(f"{source_commit} "),
        "source bundle head does not match the declared commit",
    )
    source_reference = head_lines[0].split(maxsplit=1)[1]

    with tempfile.TemporaryDirectory(
        prefix="p29-source-bundle-"
    ) as directory:
        checkout = Path(directory) / "source"
        initialize = subprocess.run(
            [git, "init", "--quiet", str(checkout)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        require(
            initialize.returncode == 0,
            f"source bundle checkout initialization failed:\n"
            f"{initialize.stdout}",
        )
        configure = subprocess.run(
            [
                git,
                "-C",
                str(checkout),
                "config",
                "core.autocrlf",
                "false",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        require(
            configure.returncode == 0,
            f"source bundle checkout configuration failed:\n"
            f"{configure.stdout}",
        )
        fetch = subprocess.run(
            [
                git,
                "-C",
                str(checkout),
                "fetch",
                "--quiet",
                str(bundle.resolve()),
                source_reference,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        require(
            fetch.returncode == 0,
            f"source bundle fetch failed:\n{fetch.stdout}",
        )
        checkout_result = subprocess.run(
            [
                git,
                "-C",
                str(checkout),
                "checkout",
                "--quiet",
                "--detach",
                "FETCH_HEAD",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        require(
            checkout_result.returncode == 0,
            "source bundle checkout failed",
        )
        head = subprocess.run(
            [git, "-C", str(checkout), "rev-parse", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        require(
            head.returncode == 0 and head.stdout.strip() == source_commit,
            "source bundle checkout does not match the declared commit",
        )

        for packaged_relative, source_relative in SOURCE_BINDINGS.items():
            packaged = certificate_dir / packaged_relative
            source = subprocess.run(
                [
                    git,
                    "-C",
                    str(checkout),
                    "show",
                    f"{source_commit}:{source_relative}",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            require(
                source.returncode == 0
                and packaged.read_bytes() == source.stdout,
                "packaged source does not match the declared commit: "
                f"{packaged_relative}",
            )

        original_verifier = checkout / "tools" / "verify_p29_certificate.py"
        require(
            original_verifier.is_file(),
            "declared source commit has no certificate verifier",
        )
        replay = subprocess.run(
            [
                sys.executable,
                str(original_verifier),
                "--certificate-dir",
                str(certificate_dir.resolve()),
            ],
            cwd=checkout,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        require(
            replay.returncode == 0
            and (
                "integrity and mathematical reconstruction VERIFIED"
                in replay.stdout
            ),
            "source-commit reconstruction failed:\n"
            f"{replay.stdout}",
        )


def replay_checker(command: list[str]) -> None:
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    require(
        completed.returncode == 0 and checker_verified(completed.stdout),
        f"proof checker failed: {command[0]}",
    )


def validate_packaged_provenance(
    summary_path: Path,
    summary: dict[str, object],
) -> None:
    provenance_root = summary_path.parent / "provenance"
    expected_names = {
        str(summary["provenance"][name]["file"])
        for name in ("makefile", "runner", "source")
    }
    actual_names = {
        path.name
        for path in provenance_root.iterdir()
        if path.is_file()
    } if provenance_root.is_dir() else set()
    require(
        actual_names == expected_names,
        f"packaged provenance is incomplete: {provenance_root}",
    )
    for name in ("makefile", "runner", "source"):
        entry = summary["provenance"][name]
        packaged = provenance_root / str(entry["file"])
        require(
            sha256(packaged) == entry["sha256_before"],
            f"packaged provenance hash mismatch: {packaged}",
        )


def validate_packaged_noncoprime_provenance(
    summary_path: Path,
    summary: dict[str, object],
) -> None:
    provenance_root = summary_path.parent / "provenance" / "sources"
    sources = summary["provenance"]["sources"]
    expected_names = {
        str(entry["file"])
        for entry in sources.values()
    }
    actual_names = {
        path.name
        for path in provenance_root.iterdir()
        if path.is_file()
    } if provenance_root.is_dir() else set()
    require(
        actual_names == expected_names,
        f"packaged noncoprime provenance is incomplete: {provenance_root}",
    )
    for entry in sources.values():
        packaged = provenance_root / str(entry["file"])
        require(
            sha256(packaged) == entry["sha256_before"],
            f"packaged noncoprime source hash mismatch: {packaged}",
        )


def compile_solver(
    command: list[str],
    label: str,
) -> None:
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    require(
        completed.returncode == 0,
        f"{label} compilation failed:\n{completed.stdout}",
    )


def replay_zero_case(binary: Path, coordinate: int) -> None:
    completed = subprocess.run(
        [
            str(binary),
            "coprime-cover",
            f"{coordinate}:{coordinate}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    require(
        completed.returncode == 20,
        f"coprime replay failed for coordinate {coordinate}: {binary}",
    )
    expected = {
        "case": ["coprime"],
        "constraint_mode": ["time-cover-only"],
        "fixed": [f"{coordinate}:{coordinate}"],
        "status": ["UNSAT"],
        "domain_branches": ["0"],
    }
    for field, values in expected.items():
        require(
            exact_fields(completed.stdout, field) == values,
            f"invalid replay field {field} for coordinate {coordinate}: "
            f"{binary}",
        )


def full_coprime_replay(
    certificate_dir: Path,
    *,
    cxx: str,
    rustc: str,
    jobs: int,
) -> None:
    cxx_path = shutil.which(cxx)
    rustc_path = shutil.which(rustc)
    require(cxx_path is not None, f"C++ compiler not found: {cxx}")
    require(rustc_path is not None, f"Rust compiler not found: {rustc}")

    cpp_source = (
        certificate_dir
        / "coprime"
        / "cpp"
        / "provenance"
        / "solve_p29_level15.cpp"
    )
    rust_source = (
        certificate_dir
        / "coprime"
        / "rust"
        / "provenance"
        / "verify_p29_level15.rs"
    )
    with tempfile.TemporaryDirectory(prefix="p29-full-replay-") as directory:
        build = Path(directory)
        cpp_binary = build / "solve_p29_level15"
        rust_binary = build / "verify_p29_level15"
        compile_solver(
            [
                cxx_path,
                "-std=c++17",
                "-O3",
                "-DNDEBUG",
                "-Wall",
                "-Wextra",
                "-pedantic",
                str(cpp_source),
                "-o",
                str(cpp_binary),
            ],
            "C++ solver",
        )
        rust_version_result = subprocess.run(
            [rustc_path, "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        require(
            rust_version_result.returncode == 0,
            f"Rust compiler version check failed: {rustc_path}",
        )
        rust_version = rust_version_result.stdout.strip()
        environment = {
            **os.environ,
            "RUSTC_VERSION": rust_version,
        }
        completed = subprocess.run(
            [
                rustc_path,
                "--edition",
                "2024",
                "-O",
                "-C",
                "overflow-checks=yes",
                "-D",
                "warnings",
                str(rust_source),
                "-o",
                str(rust_binary),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            env=environment,
        )
        require(
            completed.returncode == 0,
            f"Rust verifier compilation failed:\n{completed.stdout}",
        )
        self_test = subprocess.run(
            [str(rust_binary), "--self-test"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        require(
            self_test.returncode == 0
            and exact_fields(self_test.stdout, "self_test") == ["PASS"],
            "Rust CRT self-test failed",
        )

        tasks = [
            (binary, coordinate)
            for binary in (cpp_binary, rust_binary)
            for coordinate in P29_ZERO_COORDINATES
        ]
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=jobs
        ) as executor:
            futures = [
                executor.submit(replay_zero_case, binary, coordinate)
                for binary, coordinate in tasks
            ]
            for future in concurrent.futures.as_completed(futures):
                future.result()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate-dir", type=Path, required=True)
    parser.add_argument("--drat-trim", type=Path)
    parser.add_argument("--rate", type=Path)
    parser.add_argument("--full-replay", action="store_true")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--cxx", default="c++")
    parser.add_argument("--rustc", default="rustc")
    args = parser.parse_args()

    if (args.drat_trim is None) != (args.rate is None):
        parser.error("--drat-trim and --rate must be supplied together")
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    if args.full_replay and args.drat_trim is None:
        parser.error(
            "--full-replay requires --drat-trim and --rate"
        )
    if not args.certificate_dir.is_dir():
        parser.error("the certificate directory does not exist")
    for name in ("drat_trim", "rate"):
        path = getattr(args, name)
        if path is not None and not path.is_file():
            parser.error(f"{name.replace('_', '-')} is not a file")

    certificate_path = args.certificate_dir / "certificate.json"
    require(certificate_path.is_file(), "missing certificate.json")
    certificate = json.loads(certificate_path.read_text(encoding="ascii"))
    require(isinstance(certificate, dict), "invalid certificate object")
    require(
        certificate.get("format_version") == 1
        and certificate.get("status") == "ORIGINAL_RUNS_VERIFIED",
        "certificate original runs are not verified",
    )
    require(
        certificate.get("theorem")
        == (
            "the unique level-one improper orbit for k=14, p=29 "
            "has no improper level-15 lift"
        ),
        "certificate theorem field mismatch",
    )
    require(
        certificate.get("claim_boundary")
        == "closes the prime-29 gate only; does not prove LRC(14)",
        "certificate claim boundary mismatch",
    )
    require(
        certificate.get("verification")
        == {
            "fast_mode": "integrity-and-reconstruction-only",
            "full_replay_available": True,
        },
        "certificate verification-mode field mismatch",
    )
    require(
        is_git_sha(certificate.get("source_commit")),
        "certificate source commit is invalid",
    )
    require(
        certificate.get("parameters")
        == {
            "k": 14,
            "level": 15,
            "p": 29,
            "parent": list(P29_PARENT),
        },
        "certificate parameters do not match the theorem",
    )
    require(
        certificate.get("conclusion")
        == {
            "gate_closed": True,
            "statement": "J(14,29) = empty",
        },
        "certificate conclusion does not match the theorem",
    )
    validate_artifacts(
        args.certificate_dir,
        certificate.get("artifacts"),
    )
    validate_source_bundle(args.certificate_dir, certificate)

    level_one = certificate.get("level_one")
    require(isinstance(level_one, dict), "missing level-one certificate")
    require(
        level_one.get("orbit_count") == 1
        and level_one.get("representative") == list(P29_PARENT)
        and level_one.get("rows_sha256") == validate_level_one_orbit(),
        "level-one orbit certificate failed",
    )
    validate_crt_reduction()

    cpp_path = args.certificate_dir / "coprime" / "cpp" / "summary.json"
    rust_path = args.certificate_dir / "coprime" / "rust" / "summary.json"
    summaries = [
        (cpp_path, validate_zero_summary(cpp_path)),
        (rust_path, validate_zero_summary(rust_path)),
    ]
    require(
        [
            summary["implementation"]
            for _, summary in summaries
        ]
        == ["cpp-direct-1.1.0", "rust-crt-1.0.0"],
        "coprime implementation directories are mislabeled",
    )
    for summary_path, summary in summaries:
        validate_packaged_provenance(summary_path, summary)
    dual_path = (
        args.certificate_dir
        / "coprime"
        / "dual-verification.json"
    )
    validate_dual_summary(dual_path, summaries)
    require(
        certificate.get("coprime_branch")
        == {
            "dual_verification": "coprime/dual-verification.json",
            "summaries": [
                "coprime/cpp/summary.json",
                "coprime/rust/summary.json",
            ],
            "status": "VERIFIED_UNSAT",
            "zero_case_coverage": list(P29_ZERO_COORDINATES),
        },
        "coprime branch manifest mismatch",
    )

    noncoprime_path = (
        args.certificate_dir
        / "noncoprime"
        / "summary.json"
    )
    noncoprime_summary = validate_noncoprime_summary(noncoprime_path)
    validate_packaged_noncoprime_provenance(
        noncoprime_path,
        noncoprime_summary,
    )
    require(
        certificate.get("noncoprime_branch")
        == {
            "status": "VERIFIED_UNSAT",
            "summary": "noncoprime/summary.json",
            "summary_sha256": sha256(noncoprime_path),
        },
        "noncoprime branch manifest mismatch",
    )
    require(
        {
            summary["repository"]["head_before"]
            for _, summary in summaries
        }
        | {noncoprime_summary["repository"]["head_before"]}
        == {certificate["source_commit"]},
        "sealed runs do not share the certificate source commit",
    )

    print(
        "source-bound integrity and mathematical reconstruction PASSED",
        flush=True,
    )
    if args.drat_trim is not None and args.rate is not None:
        query = args.certificate_dir / "noncoprime" / "query.cnf"
        proof = args.certificate_dir / "noncoprime" / "proof.drat"
        replay_checker([str(args.drat_trim), str(query), str(proof)])
        replay_checker(
            [
                str(args.rate),
                "--skip-unit-deletions",
                str(query),
                str(proof),
            ]
        )
        print("noncoprime DRAT replay VERIFIED", flush=True)
    if args.full_replay:
        full_coprime_replay(
            args.certificate_dir,
            cxx=args.cxx,
            rustc=args.rustc,
            jobs=args.jobs,
        )
        print("full coprime dual replay VERIFIED", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        AttributeError,
        KeyError,
        OSError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ) as error:
        print(f"verification failed: {error}", file=sys.stderr)
        raise SystemExit(1)
