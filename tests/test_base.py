from __future__ import annotations

import sys
import unittest
from itertools import combinations_with_replacement
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lrc15.base import generate_level_one, positive_compositions
from lrc15.model import GateModel


class BaseTests(unittest.TestCase):
    def test_positive_compositions(self) -> None:
        values = list(positive_compositions(5, 3))
        self.assertEqual(len(values), 6)
        self.assertTrue(all(sum(value) == 5 for value in values))
        self.assertTrue(all(min(value) >= 1 for value in values))

    def test_generator_matches_direct_small_case(self) -> None:
        model = GateModel(k=3, prime=7)
        direct = {
            model.canonical_level_one(row)
            for row in combinations_with_replacement(
                range(1, model.folded_size + 1), model.k
            )
            if model.is_improper(row, level=1)
        }
        self.assertEqual(generate_level_one(model), direct)


if __name__ == "__main__":
    unittest.main()

