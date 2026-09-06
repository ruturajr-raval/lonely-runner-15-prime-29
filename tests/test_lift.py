from __future__ import annotations

import sys
import unittest
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lrc15.lift import (
    lift_improper_rows_for_one_parent,
    lift_rows_for_one_parent,
    weak_compositions,
)
from lrc15.model import GateModel


class LiftTests(unittest.TestCase):
    def test_weak_compositions(self) -> None:
        values = list(weak_compositions(4, 3))
        self.assertEqual(len(values), 15)
        self.assertTrue(all(sum(value) == 4 for value in values))

    def test_grouped_lifts_match_naive_coordinate_lifts(self) -> None:
        model = GateModel(k=3, prime=5)
        row = (1, 1, 2)
        grouped = set(lift_rows_for_one_parent(model, row, 1, 2))
        modulus = model.prime
        naive = {
            model.canonical_signs(
                tuple(
                    value + offset * modulus
                    for value, offset in zip(row, offsets)
                ),
                level=2,
            )
            for offsets in product(range(2), repeat=model.k)
        }
        self.assertEqual(grouped, naive)

    def test_pruned_lift_matches_brute_improper_filter(self) -> None:
        model = GateModel(k=3, prime=7)
        row = (1, 2, 3)
        brute = {
            lifted
            for lifted in lift_rows_for_one_parent(model, row, 1, 2)
            if model.is_improper(lifted, level=2)
        }
        pruned = lift_improper_rows_for_one_parent(model, row, 1, 2)
        self.assertEqual(pruned, brute)


if __name__ == "__main__":
    unittest.main()
