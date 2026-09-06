from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lrc15.crt import (
    P29_LEVEL15_TIMES,
    p29_level15_bad_by_crt,
    p29_level15_choice_for_residue,
    p29_level15_nontrivial_times,
    p29_level15_residue_from_choice,
    p29_level15_zero_choice,
)
from lrc15.model import distance_mod


class CrtTests(unittest.TestCase):
    def test_residue_choice_bijection(self) -> None:
        for coordinate in range(1, 15):
            residues = {
                p29_level15_residue_from_choice(coordinate, choice)
                for choice in range(15)
            }
            self.assertEqual(residues, set(range(15)))
            for residue in range(15):
                choice = p29_level15_choice_for_residue(
                    coordinate,
                    residue,
                )
                self.assertEqual(
                    p29_level15_residue_from_choice(coordinate, choice),
                    residue,
                )

    def test_crt_predicate_matches_direct_modular_arithmetic(self) -> None:
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
                    self.assertEqual(
                        p29_level15_bad_by_crt(
                            time,
                            coordinate,
                            residue,
                        ),
                        direct,
                        (time, coordinate, choice),
                    )

    def test_time_29_forces_a_zero_residue(self) -> None:
        for coordinate in range(1, 15):
            bad_residues = {
                residue
                for residue in range(15)
                if p29_level15_bad_by_crt(29, coordinate, residue)
            }
            self.assertEqual(bad_residues, {0})
            self.assertEqual(
                p29_level15_residue_from_choice(
                    coordinate,
                    p29_level15_zero_choice(coordinate),
                ),
                0,
            )

    def test_multiples_of_15_are_automatically_covered(self) -> None:
        for time in range(15, P29_LEVEL15_TIMES + 1, 15):
            automatic_coordinates = []
            for coordinate in range(1, 15):
                values = {
                    p29_level15_bad_by_crt(
                        time,
                        coordinate,
                        residue,
                    )
                    for residue in range(15)
                }
                if values == {True}:
                    automatic_coordinates.append(coordinate)
                else:
                    self.assertEqual(values, {False})
            self.assertEqual(len(automatic_coordinates), 1)

    def test_exactly_196_time_classes_remain_nontrivial(self) -> None:
        times = p29_level15_nontrivial_times()
        self.assertEqual(len(times), 196)
        self.assertTrue(
            all(time % 15 != 0 and time % 29 != 0 for time in times)
        )


if __name__ == "__main__":
    unittest.main()
