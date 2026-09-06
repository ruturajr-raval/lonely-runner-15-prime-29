from __future__ import annotations

import sys
import unittest
from itertools import product
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lrc15.cnf import (
    FiberEncoding,
    add_p29_level15_symmetry_case,
    prime_factors,
)
from lrc15.model import GateModel


class CnfTests(unittest.TestCase):
    def test_prime_factors(self) -> None:
        self.assertEqual(prime_factors(1), ())
        self.assertEqual(prime_factors(15), (3, 5))
        self.assertEqual(prime_factors(60), (2, 3, 5))

    def test_encoding_matches_direct_improperness(self) -> None:
        model = GateModel(k=3, prime=7)
        parent = (1, 2, 3)
        encoding = FiberEncoding(model, parent, level=1, multiplier=2)
        cnf = encoding.build()
        for choices in product(range(2), repeat=model.k):
            row = encoding.assignment_row(choices)
            expected = model.is_improper(row, level=2)
            actual = cnf.is_satisfied(encoding.true_variables(choices))
            self.assertEqual(actual, expected, choices)

    def test_composite_level_encoding_matches_direct_improperness(self) -> None:
        model = GateModel(k=2, prime=5)
        encoding = FiberEncoding(model, (1, 2), level=1, multiplier=15)
        cnf = encoding.build()
        for choices in product(range(15), repeat=model.k):
            row = encoding.assignment_row(choices)
            expected = model.is_improper(row, level=15)
            actual = cnf.is_satisfied(encoding.true_variables(choices))
            self.assertEqual(actual, expected, choices)

    def test_dimacs_header(self) -> None:
        model = GateModel(k=2, prime=5)
        cnf = FiberEncoding(model, (1, 2), 1, 3).build()
        self.assertIn(
            f"p cnf {cnf.variables} {len(cnf.clauses)}",
            cnf.dimacs(),
        )

    def test_p29_level15_coprime_symmetry_case_fixes_speed_one(self) -> None:
        model = GateModel(k=14, prime=29)
        encoding = FiberEncoding(
            model,
            tuple(range(1, 15)),
            level=1,
            multiplier=15,
        )
        cnf = encoding.build()
        before = len(cnf.clauses)
        add_p29_level15_symmetry_case(cnf, encoding, "coprime")
        self.assertEqual(len(cnf.clauses), before + 1)
        self.assertEqual(
            cnf.clauses[-1],
            (encoding.variable_for_folded_value(1),),
        )

    def test_p29_level15_noncoprime_symmetry_case(self) -> None:
        model = GateModel(k=14, prime=29)
        encoding = FiberEncoding(
            model,
            tuple(range(1, 15)),
            level=1,
            multiplier=15,
        )
        cnf = encoding.build()
        before = len(cnf.clauses)
        add_p29_level15_symmetry_case(cnf, encoding, "noncoprime")
        forbidden = [
            clause for clause in cnf.clauses[before:] if clause[0] < 0
        ]
        self.assertEqual(len(forbidden), 112)
        self.assertEqual(
            cnf.clauses[-1],
            (encoding.variable_for_folded_value(3),),
        )

    def test_p29_symmetry_case_rejects_other_fibers(self) -> None:
        model = GateModel(k=3, prime=7)
        encoding = FiberEncoding(model, (1, 2, 3), 1, 2)
        with self.assertRaises(ValueError):
            add_p29_level15_symmetry_case(
                encoding.build(),
                encoding,
                "coprime",
            )

    def test_p29_symmetry_normalization_orbits(self) -> None:
        modulus = 15 * 29
        units = [
            value for value in range(1, modulus) if gcd(value, modulus) == 1
        ]
        signed = [
            value
            for value in range(1, modulus // 2 + 1)
            if value % 29 != 0
        ]
        coprime = [value for value in signed if gcd(value, 15) == 1]
        exact_three = [value for value in signed if gcd(value, 15) == 3]
        self.assertEqual(len(units), 224)
        self.assertEqual(len(coprime), 112)
        self.assertEqual(len(exact_three), 56)
        for value in coprime:
            self.assertTrue(
                any(
                    GateModel.fold(unit * value, modulus) == 1
                    for unit in units
                )
            )
        for value in exact_three:
            self.assertTrue(
                any(
                    GateModel.fold(unit * value, modulus) == 3
                    for unit in units
                )
            )

    def test_two_coordinate_shards_are_exhaustive_and_disjoint(self) -> None:
        model = GateModel(k=14, prime=29)
        encoding = FiberEncoding(
            model,
            tuple(range(1, 15)),
            level=1,
            multiplier=15,
        )
        shards = {
            (
                encoding.variable(1, left),
                encoding.variable(2, right),
            )
            for left, right in product(range(15), repeat=2)
        }
        self.assertEqual(len(shards), 225)
        self.assertEqual(
            {
                (
                    (left_variable - 1) % 15,
                    (right_variable - 1) % 15,
                )
                for left_variable, right_variable in shards
            },
            set(product(range(15), repeat=2)),
        )

    def test_encoding_rejects_nonpositive_levels(self) -> None:
        model = GateModel(k=2, prime=5)
        with self.assertRaises(ValueError):
            FiberEncoding(model, (1, 2), level=0, multiplier=1)
        with self.assertRaises(ValueError):
            FiberEncoding(model, (1, 2), level=1, multiplier=0)

    def test_reduced_p29_cover_has_expected_constraints(self) -> None:
        model = GateModel(k=14, prime=29)
        encoding = FiberEncoding(
            model,
            tuple(range(1, 15)),
            level=1,
            multiplier=15,
        )
        cnf = encoding.build_p29_level15_reduced_time_cover()
        exactly_one_clauses = 14 * (1 + 15 * 14 // 2)
        self.assertEqual(
            len(cnf.clauses),
            exactly_one_clauses + 197,
        )
        zero_clause = cnf.clauses[exactly_one_clauses]
        self.assertEqual(
            zero_clause,
            tuple(
                encoding.variable(
                    coordinate - 1,
                    coordinate,
                )
                for coordinate in range(1, 15)
            ),
        )

    def test_reduced_p29_cover_rejects_other_fibers(self) -> None:
        model = GateModel(k=3, prime=7)
        encoding = FiberEncoding(model, (1, 2, 3), 1, 2)
        with self.assertRaises(ValueError):
            encoding.build_p29_level15_reduced_time_cover()

    def test_custom_time_classes_must_be_unique_and_folded(self) -> None:
        model = GateModel(k=2, prime=5)
        encoding = FiberEncoding(model, (1, 2), 1, 3)
        with self.assertRaises(ValueError):
            encoding.build(time_classes=(1, 1))
        with self.assertRaises(ValueError):
            encoding.build(time_classes=(8,))

    def test_fixed_choice_is_a_unit_clause(self) -> None:
        model = GateModel(k=3, prime=7)
        encoding = FiberEncoding(model, (1, 2, 3), 1, 2)
        cnf = encoding.build()
        cnf.add([encoding.variable(1, 0)])
        self.assertEqual(cnf.clauses[-1], (3,))


if __name__ == "__main__":
    unittest.main()
