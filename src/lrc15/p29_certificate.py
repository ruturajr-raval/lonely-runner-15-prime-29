from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .base import generate_level_one
from .cnf import CNF, FiberEncoding, add_p29_level15_symmetry_case
from .crt import (
    P29_LEVEL15_TIMES,
    p29_level15_bad_by_crt,
    p29_level15_nontrivial_times,
    p29_level15_residue_from_choice,
)
from .model import GateModel, distance_mod


P29_PARENT = tuple(range(1, 15))
P29_ZERO_COORDINATES = tuple(range(2, 15))
ZERO_IMPLEMENTATION_PROFILES = {
    "cpp-direct-1.1.0": {
        "solver": "solve_p29_level15",
        "source": "solve_p29_level15.cpp",
        "version_prefix": "solve_p29_level15 1.1.0\n",
    },
    "rust-crt-1.0.0": {
        "solver": "verify_p29_level15",
        "source": "verify_p29_level15.rs",
        "version_prefix": "verify_p29_level15 1.0.0\n",
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def is_git_sha(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(character in "0123456789abcdef" for character in value)
    )


def exact_fields(output: str, name: str) -> list[str]:
    prefix = f"{name} "
    return [
        line[len(prefix) :]
        for line in output.splitlines()
        if line.startswith(prefix)
    ]


def last_integer_field(output: str, name: str) -> int | None:
    values = exact_fields(output, name)
    if not values:
        return None


def integer_fields(output: str, name: str) -> list[int] | None:
    try:
        return [int(value) for value in exact_fields(output, name)]
    except ValueError:
        return None
    try:
        return int(values[-1])
    except ValueError:
        return None


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_zero_summary(path: Path) -> dict[str, object]:
    summary = json.loads(path.read_text(encoding="ascii"))
    _require(isinstance(summary, dict), f"invalid summary object: {path}")
    _require(
        summary.get("format_version") == 1,
        f"invalid format version: {path}",
    )
    _require(
        summary.get("expected_cases") == len(P29_ZERO_COORDINATES),
        f"invalid expected case count: {path}",
    )
    _require(
        summary.get("case_coverage")
        == (
            "every coprime time cover has a zero residue modulo 15; "
            "the listed coordinate-zero cases cover all possibilities"
        )
        and summary.get("cases_are_disjoint") is False,
        f"invalid case-coverage statement: {path}",
    )
    _require(
        summary.get("provenance_unchanged_during_run") is True,
        f"provenance changed during run: {path}",
    )
    repository = summary.get("repository")
    _require(
        isinstance(repository, dict)
        and is_git_sha(repository.get("head_before"))
        and repository.get("head_before") == repository.get("head_after")
        and repository.get("tracked_worktree_clean_before") is True
        and repository.get("tracked_worktree_clean_after") is True
        and repository.get("unchanged_during_run") is True,
        f"invalid repository provenance: {path}",
    )
    _require(
        summary.get("parameters")
        == {
            "k": 14,
            "level": 15,
            "p": 29,
            "parent": list(P29_PARENT),
            "symmetry_case": "coprime",
        },
        f"invalid parameters: {path}",
    )
    _require(
        summary.get("theorem_scope")
        == (
            "no level-15 lift in the coprime symmetry case covers "
            "all folded time classes"
        ),
        f"invalid theorem scope: {path}",
    )

    implementation = summary.get("implementation")
    _require(
        implementation in ZERO_IMPLEMENTATION_PROFILES,
        f"invalid implementation label: {path}",
    )
    profile = ZERO_IMPLEMENTATION_PROFILES[str(implementation)]
    solver_version = summary.get("solver_version")
    _require(
        isinstance(solver_version, str)
        and solver_version.startswith(str(profile["version_prefix"])),
        f"missing solver version: {path}",
    )

    provenance = summary.get("provenance")
    _require(isinstance(provenance, dict), f"invalid provenance: {path}")
    _require(
        set(provenance) == {"makefile", "runner", "solver", "source"},
        f"incomplete provenance: {path}",
    )
    for name, entry in provenance.items():
        _require(
            isinstance(entry, dict),
            f"invalid provenance entry {name}: {path}",
        )
        file_name = entry.get("file")
        before = entry.get("sha256_before")
        after = entry.get("sha256_after")
        _require(
            isinstance(file_name, str)
            and Path(file_name).name == file_name,
            f"invalid provenance filename {name}: {path}",
        )
        _require(
            is_sha256(before) and before == after,
            f"invalid provenance hash {name}: {path}",
        )
    _require(
        provenance["makefile"]["file"] == "Makefile"
        and provenance["runner"]["file"] == "run_p29_zero_cases.py"
        and provenance["solver"]["file"] == profile["solver"]
        and provenance["source"]["file"] == profile["source"],
        f"provenance files do not match the implementation: {path}",
    )

    log_directory = summary.get("log_directory")
    _require(
        isinstance(log_directory, str)
        and log_directory == "logs",
        f"invalid log directory: {path}",
    )
    log_root = path.parent / log_directory

    results = summary.get("results")
    _require(
        isinstance(results, list)
        and len(results) == len(P29_ZERO_COORDINATES),
        f"invalid result list: {path}",
    )
    _require(
        all(isinstance(result, dict) for result in results)
        and [result.get("coordinate") for result in results]
        == list(P29_ZERO_COORDINATES),
        f"incomplete coordinate coverage: {path}",
    )
    for result in results:
        coordinate = result["coordinate"]
        _require(
            result.get("lift_choice") == coordinate,
            f"invalid zero choice for coordinate {coordinate}: {path}",
        )
        _require(
            result.get("exit_code") == 20
            and result.get("status") == "UNSAT",
            f"case {coordinate} is not UNSAT: {path}",
        )
        log_name = result.get("log")
        _require(
            isinstance(log_name, str)
            and Path(log_name).name == log_name,
            f"invalid log name for coordinate {coordinate}: {path}",
        )
        log = log_root / log_name
        _require(log.is_file(), f"missing log: {log}")
        _require(
            sha256(log) == result.get("log_sha256"),
            f"log hash mismatch: {log}",
        )
        output = log.read_text(encoding="utf-8")
        expected = {
            "case": ["coprime"],
            "constraint_mode": ["time-cover-only"],
            "fixed": [f"{coordinate}:{coordinate}"],
            "status": ["UNSAT"],
        }
        for field, values in expected.items():
            _require(
                exact_fields(output, field) == values,
                f"invalid {field} field: {log}",
            )
        for field in ("nodes", "propagations", "domain_branches"):
            value = result.get(field)
            values = integer_fields(output, field)
            _require(
                isinstance(value, int)
                and value >= 0
                and values is not None
                and bool(values)
                and values[-1] == value,
                f"invalid {field} count: {log}",
            )
            if field == "nodes":
                _require(
                    values == sorted(values)
                    and len(values) == len(set(values)),
                    f"nonmonotone node transcript: {log}",
                )
            else:
                _require(
                    len(values) == 1,
                    f"duplicate {field} transcript: {log}",
                )
        _require(
            result.get("domain_branches") == 0,
            f"unexpected fallback branch: {log}",
        )
    return summary


def validate_dual_summary(
    path: Path,
    summaries: list[tuple[Path, dict[str, object]]],
) -> dict[str, object]:
    dual = json.loads(path.read_text(encoding="ascii"))
    _require(isinstance(dual, dict), f"invalid dual summary: {path}")
    _require(
        dual.get("format_version") == 1,
        f"invalid dual format version: {path}",
    )
    _require(
        dual.get("status") == "VERIFIED_UNSAT",
        f"dual verification is incomplete: {path}",
    )
    _require(
        dual.get("zero_case_coverage") == list(P29_ZERO_COORDINATES),
        f"dual coverage is incomplete: {path}",
    )
    entries = dual.get("independent_implementations")
    _require(
        isinstance(entries, list) and len(entries) == len(summaries),
        f"invalid independent implementation list: {path}",
    )
    _require(
        all(isinstance(entry, dict) for entry in entries),
        f"malformed independent implementation list: {path}",
    )
    _require(
        dual.get("theorem_scope")
        == (
            "no level-15 lift in the coprime symmetry case covers "
            "all folded time classes"
        ),
        f"invalid dual theorem scope: {path}",
    )
    expected = [
        {
            "implementation": summary["implementation"],
            "source_sha256": summary["provenance"]["source"][
                "sha256_before"
            ],
            "summary": summary_path.name,
            "summary_sha256": sha256(summary_path),
        }
        for summary_path, summary in summaries
    ]
    _require(entries == expected, f"dual summary mismatch: {path}")
    _require(
        len({entry["implementation"] for entry in entries})
        == len(entries),
        f"duplicate implementation labels: {path}",
    )
    _require(
        len({entry["source_sha256"] for entry in entries})
        == len(entries),
        f"duplicate source implementations: {path}",
    )
    return dual


def expected_noncoprime_cnf() -> CNF:
    model = GateModel(k=14, prime=29)
    encoding = FiberEncoding(
        model=model,
        parent=P29_PARENT,
        level=1,
        multiplier=15,
    )
    cnf = encoding.build()
    add_p29_level15_symmetry_case(cnf, encoding, "noncoprime")
    return cnf


def parse_dimacs(path: Path) -> CNF:
    variables: int | None = None
    declared_clauses: int | None = None
    clauses: list[tuple[int, ...]] = []
    pending: list[int] = []

    for raw_line in path.read_text(encoding="ascii").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("c"):
            continue
        if line.startswith("p "):
            _require(variables is None, f"duplicate DIMACS header: {path}")
            parts = line.split()
            _require(
                len(parts) == 4 and parts[:2] == ["p", "cnf"],
                f"invalid DIMACS header: {path}",
            )
            variables = int(parts[2])
            declared_clauses = int(parts[3])
            continue
        _require(variables is not None, f"clause before header: {path}")
        for token in line.split():
            literal = int(token)
            if literal == 0:
                clauses.append(tuple(pending))
                pending.clear()
            else:
                _require(
                    1 <= abs(literal) <= variables,
                    f"literal out of range: {path}",
                )
                pending.append(literal)

    _require(variables is not None, f"missing DIMACS header: {path}")
    _require(not pending, f"unterminated DIMACS clause: {path}")
    _require(
        declared_clauses == len(clauses),
        f"DIMACS clause count mismatch: {path}",
    )
    return CNF(variables=variables, clauses=clauses)


def validate_noncoprime_cnf(path: Path) -> CNF:
    actual = parse_dimacs(path)
    expected = expected_noncoprime_cnf()
    _require(
        actual.variables == expected.variables,
        f"noncoprime variable count mismatch: {path}",
    )
    _require(
        actual.clauses == expected.clauses,
        f"noncoprime clause mismatch: {path}",
    )
    return actual


def validate_level_one_orbit() -> str:
    rows = generate_level_one(GateModel(k=14, prime=29))
    _require(
        rows == {P29_PARENT},
        "the level-one generator did not return the unique expected orbit",
    )
    digest = hashlib.sha256()
    for row in sorted(rows):
        digest.update(" ".join(map(str, row)).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def validate_crt_reduction() -> None:
    modulus = 15 * 29
    for time in range(1, P29_LEVEL15_TIMES + 1):
        for coordinate in range(1, 15):
            for choice in range(15):
                residue = p29_level15_residue_from_choice(
                    coordinate,
                    choice,
                )
                speed = coordinate + 29 * choice
                direct = (
                    15 * distance_mod(time * speed, modulus) < modulus
                )
                _require(
                    p29_level15_bad_by_crt(
                        time,
                        coordinate,
                        residue,
                    )
                    == direct,
                    "CRT predicate mismatch",
                )
    _require(
        len(p29_level15_nontrivial_times()) == 196,
        "unexpected nontrivial CRT time count",
    )


def checker_verified(output: str) -> bool:
    return any(
        line.strip() == "s VERIFIED"
        for line in output.splitlines()
    )


def validate_noncoprime_summary(path: Path) -> dict[str, object]:
    summary = json.loads(path.read_text(encoding="ascii"))
    _require(
        isinstance(summary, dict),
        f"invalid noncoprime summary: {path}",
    )
    _require(
        summary.get("format_version") == 1,
        f"invalid noncoprime format version: {path}",
    )
    _require(
        summary.get("status") == "VERIFIED_UNSAT",
        f"noncoprime proof is incomplete: {path}",
    )
    _require(
        summary.get("parameters")
        == {
            "k": 14,
            "level": 15,
            "p": 29,
            "parent": list(P29_PARENT),
            "symmetry_case": "noncoprime",
        },
        f"invalid noncoprime parameters: {path}",
    )
    _require(
        summary.get("theorem_scope")
        == (
            "no improper level-15 lift exists in the normalized "
            "noncoprime symmetry branch"
        ),
        f"invalid noncoprime theorem scope: {path}",
    )

    query_entry = summary.get("query")
    _require(isinstance(query_entry, dict), f"missing query: {path}")
    query_name = query_entry.get("file")
    _require(
        isinstance(query_name, str)
        and Path(query_name).name == query_name,
        f"invalid query filename: {path}",
    )
    query = path.parent / query_name
    _require(query.is_file(), f"missing query: {query}")
    _require(
        query_entry.get("sha256") == sha256(query),
        f"query hash mismatch: {query}",
    )
    parsed = validate_noncoprime_cnf(query)
    _require(
        query_entry.get("variables") == parsed.variables
        and query_entry.get("clauses") == len(parsed.clauses),
        f"query dimensions mismatch: {query}",
    )

    proof_entry = summary.get("proof")
    _require(isinstance(proof_entry, dict), f"missing proof: {path}")
    proof_name = proof_entry.get("file")
    _require(
        isinstance(proof_name, str)
        and Path(proof_name).name == proof_name,
        f"invalid proof filename: {path}",
    )
    proof = path.parent / proof_name
    _require(proof.is_file(), f"missing proof: {proof}")
    _require(
        proof_entry.get("format") == "DRAT"
        and proof_entry.get("bytes") == proof.stat().st_size
        and proof_entry.get("sha256") == sha256(proof),
        f"proof metadata mismatch: {proof}",
    )

    solver = summary.get("solver")
    _require(isinstance(solver, dict), f"missing solver record: {path}")
    solver_log_name = solver.get("log")
    _require(
        isinstance(solver_log_name, str)
        and Path(solver_log_name).name == solver_log_name,
        f"invalid solver log filename: {path}",
    )
    solver_log = path.parent / solver_log_name
    _require(solver_log.is_file(), f"missing solver log: {solver_log}")
    _require(
        solver.get("exit_code") == 20
        and solver.get("log_sha256") == sha256(solver_log)
        and isinstance(solver.get("version"), str)
        and bool(str(solver.get("version")).strip()),
        f"invalid solver record: {path}",
    )
    _require(
        any(
            line.strip() == "s UNSATISFIABLE"
            for line in solver_log.read_text(
                encoding="utf-8",
            ).splitlines()
        ),
        f"solver log has no exact UNSAT line: {solver_log}",
    )

    checkers = summary.get("checkers")
    _require(
        isinstance(checkers, list)
        and all(isinstance(checker, dict) for checker in checkers)
        and [checker.get("name") for checker in checkers]
        == ["drat-trim", "rate"],
        f"invalid checker records: {path}",
    )
    for checker in checkers:
        log_name = checker.get("log")
        _require(
            isinstance(log_name, str)
            and Path(log_name).name == log_name,
            f"invalid checker log filename: {path}",
        )
        log = path.parent / log_name
        _require(log.is_file(), f"missing checker log: {log}")
        output = log.read_text(encoding="utf-8")
        _require(
            checker.get("exit_code") == 0
            and checker.get("verified") is True
            and checker.get("log_sha256") == sha256(log)
            and checker_verified(output),
            f"checker did not verify the proof: {log}",
        )

    provenance = summary.get("provenance")
    _require(isinstance(provenance, dict), f"missing provenance: {path}")
    _require(
        provenance.get("unchanged_during_run") is True,
        f"provenance changed during run: {path}",
    )
    repository = summary.get("repository")
    _require(
        isinstance(repository, dict)
        and is_git_sha(repository.get("head_before"))
        and repository.get("head_before") == repository.get("head_after")
        and repository.get("tracked_worktree_clean_before") is True
        and repository.get("tracked_worktree_clean_after") is True
        and repository.get("unchanged_during_run") is True,
        f"invalid repository provenance: {path}",
    )
    expected_groups = {
        "sources": {
            "cnf": "cnf.py",
            "crt": "crt.py",
            "model": "model.py",
            "p29-certificate": "p29_certificate.py",
            "runner": "run_p29_noncoprime_proof.py",
        },
        "tools": {
            "drat-trim": "drat-trim",
            "rate": "rate",
            "solver": "kissat",
        },
    }
    for group_name in ("sources", "tools"):
        group = provenance.get(group_name)
        _require(
            isinstance(group, dict)
            and set(group) == set(expected_groups[group_name]),
            f"missing provenance group {group_name}: {path}",
        )
        for name, entry in group.items():
            _require(
                isinstance(entry, dict),
                f"invalid provenance entry {group_name}.{name}: {path}",
            )
            file_name = entry.get("file")
            before = entry.get("sha256_before")
            after = entry.get("sha256_after")
            _require(
                isinstance(file_name, str)
                and Path(file_name).name == file_name
                and is_sha256(before)
                and before == after,
                f"invalid provenance entry {group_name}.{name}: {path}",
            )
            _require(
                file_name == expected_groups[group_name][name],
                f"unexpected provenance file {group_name}.{name}: {path}",
            )
    return summary
