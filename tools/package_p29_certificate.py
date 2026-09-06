#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELECTED_CERTIFICATE = (
    ROOT / "results" / "p29-level15-certificate-v1"
)
SELECTED_SOURCE_BUNDLE = (
    SELECTED_CERTIFICATE / "provenance" / "source-commit.bundle"
)
sys.path.insert(0, str(ROOT / "src"))

from lrc15.p29_certificate import (
    P29_PARENT,
    P29_ZERO_COORDINATES,
    sha256,
    validate_crt_reduction,
    validate_dual_summary,
    validate_level_one_orbit,
    validate_noncoprime_summary,
    validate_zero_summary,
)


def prepare_output(parser: argparse.ArgumentParser, path: Path) -> None:
    if path.exists():
        if not path.is_dir():
            parser.error("the output path is not a directory")
        if any(path.iterdir()):
            parser.error("the output directory must be empty")
    path.mkdir(parents=True, exist_ok=True)


def matching_sealed_file(
    label: str,
    expected_hash: str,
    candidates: list[Path],
) -> Path:
    for candidate in candidates:
        if candidate.is_file() and sha256(candidate) == expected_hash:
            return candidate
    rendered = ", ".join(str(path) for path in candidates)
    raise ValueError(
        f"no {label} file matches the sealed run hash: {rendered}"
    )


def copy_zero_certificate(
    source_summary: Path,
    destination: Path,
) -> Path:
    summary = validate_zero_summary(source_summary)
    destination.mkdir(parents=True, exist_ok=True)
    log_destination = destination / "logs"
    log_destination.mkdir()
    copied_summary = destination / "summary.json"
    shutil.copy2(source_summary, copied_summary)

    source_logs = source_summary.parent / str(summary["log_directory"])
    for result in summary["results"]:
        name = str(result["log"])
        shutil.copy2(source_logs / name, log_destination / name)

    provenance_destination = destination / "provenance"
    provenance_destination.mkdir()
    implementation_directory = {
        "cpp-direct-1.1.0": "cpp",
        "rust-crt-1.0.0": "rust",
    }.get(str(summary["implementation"]))
    adjacent_provenance = source_summary.parent / "provenance"
    selected_provenance = (
        SELECTED_CERTIFICATE
        / "coprime"
        / implementation_directory
        / "provenance"
        if implementation_directory is not None
        else None
    )
    provenance_sources = {
        "makefile": ROOT / "Makefile",
        "runner": (
            ROOT
            / "tools"
            / str(summary["provenance"]["runner"]["file"])
        ),
        "source": (
            ROOT
            / "tools"
            / str(summary["provenance"]["source"]["file"])
        ),
    }
    for name, current_source in provenance_sources.items():
        expected_hash = str(
            summary["provenance"][name]["sha256_before"]
        )
        candidates = [
            current_source,
            adjacent_provenance / current_source.name,
        ]
        if selected_provenance is not None:
            candidates.append(
                selected_provenance / current_source.name
            )
        source = matching_sealed_file(
            name,
            expected_hash,
            candidates,
        )
        shutil.copy2(source, provenance_destination / source.name)
    validate_zero_summary(copied_summary)
    return copied_summary


def copy_noncoprime_certificate(
    source_summary: Path,
    destination: Path,
) -> Path:
    summary = validate_noncoprime_summary(source_summary)
    destination.mkdir(parents=True, exist_ok=True)
    names = {
        "summary.json",
        str(summary["query"]["file"]),
        str(summary["proof"]["file"]),
        str(summary["solver"]["log"]),
        *(
            str(checker["log"])
            for checker in summary["checkers"]
        ),
    }
    for name in sorted(names):
        source = (
            source_summary
            if name == "summary.json"
            else source_summary.parent / name
        )
        shutil.copy2(source, destination / name)

    provenance_destination = destination / "provenance" / "sources"
    provenance_destination.mkdir(parents=True)
    adjacent_provenance = (
        source_summary.parent / "provenance" / "sources"
    )
    selected_provenance = (
        SELECTED_CERTIFICATE / "noncoprime" / "provenance" / "sources"
    )
    source_locations = {
        "cnf": ROOT / "src" / "lrc15" / "cnf.py",
        "crt": ROOT / "src" / "lrc15" / "crt.py",
        "model": ROOT / "src" / "lrc15" / "model.py",
        "p29-certificate": (
            ROOT / "src" / "lrc15" / "p29_certificate.py"
        ),
        "runner": (
            ROOT / "tools" / "run_p29_noncoprime_proof.py"
        ),
    }
    for name, current_source in source_locations.items():
        expected_hash = str(
            summary["provenance"]["sources"][name]["sha256_before"]
        )
        source = matching_sealed_file(
            f"noncoprime {name}",
            expected_hash,
            [
                current_source,
                adjacent_provenance / current_source.name,
                selected_provenance / current_source.name,
            ],
        )
        shutil.copy2(source, provenance_destination / source.name)
    copied_summary = destination / "summary.json"
    validate_noncoprime_summary(copied_summary)
    return copied_summary


def artifact_manifest(root: Path) -> dict[str, dict[str, object]]:
    artifacts: dict[str, dict[str, object]] = {}
    for path in sorted(root.rglob("*")):
        if (
            not path.is_file()
            or path == root / "certificate.json"
        ):
            continue
        relative = path.relative_to(root).as_posix()
        artifacts[relative] = {
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
    return artifacts


def git_has_commit(source_commit: str) -> bool:
    completed = subprocess.run(
        ["git", "cat-file", "-e", f"{source_commit}^{{commit}}"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return completed.returncode == 0


def bundle_contains_commit(path: Path, source_commit: str) -> bool:
    if not path.is_file():
        return False
    completed = subprocess.run(
        ["git", "bundle", "list-heads", str(path)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return False
    return any(
        line.split(maxsplit=1)[0] == source_commit
        for line in completed.stdout.splitlines()
        if line.strip()
    )


def create_source_bundle(root: Path, source_commit: str) -> Path:
    output = root / "provenance" / "source-commit.bundle"
    output.parent.mkdir(parents=True)
    if not git_has_commit(source_commit):
        if not bundle_contains_commit(
            SELECTED_SOURCE_BUNDLE,
            source_commit,
        ):
            raise ValueError(
                "the source commit is absent and no matching tracked "
                "source bundle is available"
            )
        shutil.copy2(SELECTED_SOURCE_BUNDLE, output)
        return output

    reference = f"refs/p29-certificate/{source_commit}"
    created = False
    try:
        subprocess.run(
            ["git", "update-ref", reference, source_commit],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        created = True
        subprocess.run(
            ["git", "bundle", "create", str(output), reference],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    finally:
        if created:
            subprocess.run(
                ["git", "update-ref", "-d", reference],
                cwd=ROOT,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cpp-summary", type=Path, required=True)
    parser.add_argument("--rust-summary", type=Path, required=True)
    parser.add_argument("--noncoprime-summary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    for name in ("cpp_summary", "rust_summary", "noncoprime_summary"):
        path = getattr(args, name)
        if not path.is_file():
            parser.error(f"{name.replace('_', '-')} is not a file")
    prepare_output(parser, args.output_dir)

    cpp_summary = copy_zero_certificate(
        args.cpp_summary,
        args.output_dir / "coprime" / "cpp",
    )
    rust_summary = copy_zero_certificate(
        args.rust_summary,
        args.output_dir / "coprime" / "rust",
    )
    summaries = [
        (cpp_summary, validate_zero_summary(cpp_summary)),
        (rust_summary, validate_zero_summary(rust_summary)),
    ]
    if [
        summary["implementation"]
        for _, summary in summaries
    ] != ["cpp-direct-1.1.0", "rust-crt-1.0.0"]:
        parser.error(
            "--cpp-summary and --rust-summary do not match their labels"
        )

    dual_path = args.output_dir / "coprime" / "dual-verification.json"
    dual = {
        "format_version": 1,
        "independent_implementations": [
            {
                "implementation": summary["implementation"],
                "source_sha256": summary["provenance"]["source"][
                    "sha256_before"
                ],
                "summary": summary_path.name,
                "summary_sha256": sha256(summary_path),
            }
            for summary_path, summary in summaries
        ],
        "status": "VERIFIED_UNSAT",
        "theorem_scope": (
            "no level-15 lift in the coprime symmetry case covers "
            "all folded time classes"
        ),
        "zero_case_coverage": list(P29_ZERO_COORDINATES),
    }
    dual_path.write_text(
        json.dumps(dual, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
    )
    validate_dual_summary(dual_path, summaries)

    noncoprime_summary = copy_noncoprime_certificate(
        args.noncoprime_summary,
        args.output_dir / "noncoprime",
    )
    noncoprime_data = validate_noncoprime_summary(noncoprime_summary)
    source_commits = {
        summary["repository"]["head_before"]
        for _, summary in summaries
    }
    source_commits.add(
        noncoprime_data["repository"]["head_before"]
    )
    if len(source_commits) != 1:
        parser.error("all sealed runs must use the same source commit")
    source_commit = next(iter(source_commits))
    source_bundle = create_source_bundle(
        args.output_dir,
        source_commit,
    )
    validate_crt_reduction()
    level_one_sha256 = validate_level_one_orbit()

    certificate = {
        "artifacts": artifact_manifest(args.output_dir),
        "claim_boundary": (
            "closes the prime-29 gate only; does not prove LRC(14)"
        ),
        "conclusion": {
            "gate_closed": True,
            "statement": "J(14,29) = empty",
        },
        "coprime_branch": {
            "dual_verification": "coprime/dual-verification.json",
            "summaries": [
                "coprime/cpp/summary.json",
                "coprime/rust/summary.json",
            ],
            "status": "VERIFIED_UNSAT",
            "zero_case_coverage": list(P29_ZERO_COORDINATES),
        },
        "format_version": 1,
        "level_one": {
            "orbit_count": 1,
            "representative": list(P29_PARENT),
            "rows_sha256": level_one_sha256,
        },
        "noncoprime_branch": {
            "status": "VERIFIED_UNSAT",
            "summary": noncoprime_summary.relative_to(
                args.output_dir
            ).as_posix(),
            "summary_sha256": sha256(noncoprime_summary),
        },
        "parameters": {
            "k": 14,
            "level": 15,
            "p": 29,
            "parent": list(P29_PARENT),
        },
        "source_commit": source_commit,
        "source_bundle": source_bundle.relative_to(
            args.output_dir
        ).as_posix(),
        "status": "ORIGINAL_RUNS_VERIFIED",
        "theorem": (
            "the unique level-one improper orbit for k=14, p=29 "
            "has no improper level-15 lift"
        ),
        "verification": {
            "fast_mode": "integrity-and-reconstruction-only",
            "full_replay_available": True,
        },
    }
    certificate_path = args.output_dir / "certificate.json"
    certificate_path.write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
    )
    print(f"wrote complete certificate to {args.output_dir}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
