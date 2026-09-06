from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lrc15.model import GateModel, distance_mod


class ModelTests(unittest.TestCase):
    def test_distance_mod(self) -> None:
        self.assertEqual(distance_mod(0, 11), 0)
        self.assertEqual(distance_mod(3, 11), 3)
        self.assertEqual(distance_mod(8, 11), 3)
        self.assertEqual(distance_mod(-3, 11), 3)

    def test_level_one_unit_canonicalization(self) -> None:
        model = GateModel(k=3, prime=11)
        row = (1, 2, 5)
        scaled = tuple(model.fold(3 * value, 11) for value in row)
        self.assertEqual(
            model.canonical_level_one(row),
            model.canonical_level_one(scaled),
        )

    def test_sign_canonicalization(self) -> None:
        model = GateModel(k=3, prime=11)
        self.assertEqual(
            model.canonical_signs((1, 7, 20), level=2),
            (1, 2, 7),
        )

    def test_gcd_clause(self) -> None:
        model = GateModel(k=3, prime=5)
        self.assertTrue(model.satisfies_gcd_clause((2, 4, 1), level=2))
        self.assertFalse(model.satisfies_gcd_clause((1, 2, 3), level=2))


if __name__ == "__main__":
    unittest.main()

