from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lrc15.base import generate_level_one
from lrc15.model import GateModel
from lrc15.pipeline import apply_pipeline


class PipelineTests(unittest.TestCase):
    def test_projection_returns_level_one_orbits(self) -> None:
        model = GateModel(k=3, prime=7)
        rows = {(1, 8, 9)}
        projected, level, stages = apply_pipeline(model, rows, ["p"])
        self.assertEqual(level, 1)
        self.assertEqual(projected, {model.canonical_level_one((1, 1, 2))})
        self.assertEqual(stages[0].operation, "project")
        self.assertEqual(stages[0].search_nodes, 0)

    def test_small_gate_smoke(self) -> None:
        model = GateModel(k=2, prime=5)
        rows = generate_level_one(model)
        final_rows, final_level, stages = apply_pipeline(model, rows, [3])
        self.assertEqual(final_level, 3)
        self.assertEqual(final_rows, set())
        self.assertEqual(stages[-1].output_rows, 0)


if __name__ == "__main__":
    unittest.main()
