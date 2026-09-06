from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lrc15.p29_certificate import (
    checker_verified,
    expected_noncoprime_cnf,
    parse_dimacs,
    sha256,
    validate_level_one_orbit,
    validate_zero_summary,
)
from lrc15.model import GateModel


class P29CertificateTests(unittest.TestCase):
    def make_zero_summary(self, root: Path) -> Path:
        logs = root / "logs"
        logs.mkdir()
        results = []
        for coordinate in range(2, 15):
            log = logs / f"zero-c{coordinate:02d}.log"
            log.write_text(
                "\n".join(
                    [
                        "case coprime",
                        "constraint_mode time-cover-only",
                        "status UNSAT",
                        "nodes 1",
                        "propagations 2",
                        "domain_branches 0",
                        f"fixed {coordinate}:{coordinate}",
                        "",
                    ]
                ),
                encoding="ascii",
            )
            results.append(
                {
                    "coordinate": coordinate,
                    "domain_branches": 0,
                    "exit_code": 20,
                    "lift_choice": coordinate,
                    "log": log.name,
                    "log_sha256": sha256(log),
                    "nodes": 1,
                    "propagations": 2,
                    "status": "UNSAT",
                }
            )
        digest = "0" * 64
        summary = {
            "case_coverage": (
                "every coprime time cover has a zero residue modulo 15; "
                "the listed coordinate-zero cases cover all possibilities"
            ),
            "cases_are_disjoint": False,
            "expected_cases": 13,
            "format_version": 1,
            "implementation": "cpp-direct-1.1.0",
            "log_directory": "logs",
            "parameters": {
                "k": 14,
                "level": 15,
                "p": 29,
                "parent": list(range(1, 15)),
                "symmetry_case": "coprime",
            },
            "provenance": {
                "makefile": {
                    "file": "Makefile",
                    "sha256_after": digest,
                    "sha256_before": digest,
                },
                "runner": {
                    "file": "run_p29_zero_cases.py",
                    "sha256_after": digest,
                    "sha256_before": digest,
                },
                "solver": {
                    "file": "solve_p29_level15",
                    "sha256_after": digest,
                    "sha256_before": digest,
                },
                "source": {
                    "file": "solve_p29_level15.cpp",
                    "sha256_after": digest,
                    "sha256_before": digest,
                },
            },
            "provenance_unchanged_during_run": True,
            "repository": {
                "head_after": "1" * 40,
                "head_before": "1" * 40,
                "tracked_worktree_clean_after": True,
                "tracked_worktree_clean_before": True,
                "unchanged_during_run": True,
            },
            "results": results,
            "solver_version": (
                "solve_p29_level15 1.1.0\ncompiler test\n"
            ),
            "theorem_scope": (
                "no level-15 lift in the coprime symmetry case covers "
                "all folded time classes"
            ),
        }
        path = root / "summary.json"
        path.write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="ascii",
        )
        return path

    def test_level_one_orbit_is_unique(self) -> None:
        self.assertEqual(
            validate_level_one_orbit(),
            "a8d0f6ffa5961efb0405e27450d85cef2"
            "b471d9dcb4d2afc73b5f71c7127ed08",
        )

    def test_level_one_bad_masks_partition_folded_times(self) -> None:
        model = GateModel(k=14, prime=29)
        masks = [model.bad_mask(speed) for speed in range(1, 15)]
        self.assertTrue(
            all(bin(mask).count("1") == 1 for mask in masks)
        )
        self.assertEqual(
            sum(masks),
            (1 << model.folded_size) - 1,
        )

    def test_noncoprime_cnf_round_trip(self) -> None:
        expected = expected_noncoprime_cnf()
        self.assertEqual(expected.variables, 210)
        self.assertEqual(len(expected.clauses), 1842)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "query.cnf"
            path.write_text(expected.dimacs(["test query"]), encoding="ascii")
            actual = parse_dimacs(path)
        self.assertEqual(actual.variables, expected.variables)
        self.assertEqual(actual.clauses, expected.clauses)

    def test_dimacs_parser_rejects_wrong_clause_count(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.cnf"
            path.write_text(
                "p cnf 2 2\n1 0\n",
                encoding="ascii",
            )
            with self.assertRaises(ValueError):
                parse_dimacs(path)

    def test_checker_requires_exact_verified_line(self) -> None:
        self.assertTrue(checker_verified("c details\ns VERIFIED\n"))
        self.assertFalse(checker_verified("prefix s VERIFIED suffix\n"))

    def test_zero_summary_validator_accepts_complete_cases(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.make_zero_summary(Path(directory))
            summary = validate_zero_summary(path)
        self.assertEqual(len(summary["results"]), 13)

    def test_zero_summary_validator_fails_closed_on_malformed_result(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.make_zero_summary(Path(directory))
            summary = json.loads(path.read_text(encoding="ascii"))
            summary["results"][0] = "not an object"
            path.write_text(
                json.dumps(summary, indent=2, sort_keys=True) + "\n",
                encoding="ascii",
            )
            with self.assertRaises(ValueError):
                validate_zero_summary(path)


if __name__ == "__main__":
    unittest.main()
