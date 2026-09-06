from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from math import gcd


Row = tuple[int, ...]


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 1
    return True


def distance_mod(value: int, modulus: int) -> int:
    residue = value % modulus
    return min(residue, modulus - residue)


@dataclass(frozen=True)
class GateModel:
    k: int
    prime: int

    def __post_init__(self) -> None:
        if self.k < 2:
            raise ValueError("k must be at least 2")
        if not is_prime(self.prime):
            raise ValueError("prime must be prime")

    @property
    def threshold_denominator(self) -> int:
        return self.k + 1

    @property
    def folded_size(self) -> int:
        return self.prime // 2

    @staticmethod
    def fold(value: int, modulus: int) -> int:
        residue = value % modulus
        return min(residue, modulus - residue)

    @cache
    def bad_mask(self, speed: int) -> int:
        mask = 0
        for time in range(1, self.folded_size + 1):
            if (
                self.threshold_denominator
                * distance_mod(time * speed, self.prime)
                < self.prime
            ):
                mask |= 1 << (time - 1)
        return mask

    @cache
    def good_mask(self, level: int, speed: int) -> int:
        modulus = level * self.prime
        mask = 0
        for time in range(1, modulus // 2 + 1):
            if (
                self.threshold_denominator
                * distance_mod(time * speed, modulus)
                >= modulus
            ):
                mask |= 1 << (time - 1)
        return mask

    @cache
    def bad_mask_at_level(self, level: int, speed: int) -> int:
        modulus = level * self.prime
        mask = 0
        for time in range(1, modulus // 2 + 1):
            if (
                self.threshold_denominator
                * distance_mod(time * speed, modulus)
                < modulus
            ):
                mask |= 1 << (time - 1)
        return mask

    def has_witness(self, row: Row, level: int) -> bool:
        modulus = level * self.prime
        possible = (1 << (modulus // 2)) - 1
        for speed in row:
            possible &= self.good_mask(level, speed)
            if possible == 0:
                return False
        return possible != 0

    def satisfies_gcd_clause(self, row: Row, level: int) -> bool:
        if level == 1:
            return False
        for omitted in range(self.k):
            common = level
            for index, speed in enumerate(row):
                if index != omitted:
                    common = gcd(common, speed)
                    if common == 1:
                        break
            if common > 1:
                return True
        return False

    def is_proper(self, row: Row, level: int) -> bool:
        self.validate_row(row, level)
        return self.satisfies_gcd_clause(row, level) or self.has_witness(
            row, level
        )

    def is_improper(self, row: Row, level: int) -> bool:
        return not self.is_proper(row, level)

    def canonical_level_one(self, row: Row) -> Row:
        if len(row) != self.k:
            raise ValueError("row has the wrong length")
        best: Row | None = None
        for unit in range(1, self.folded_size + 1):
            candidate = tuple(
                sorted(self.fold(unit * value, self.prime) for value in row)
            )
            if best is None or candidate < best:
                best = candidate
        assert best is not None
        return best

    def project_level_one(self, row: Row) -> Row:
        projected = tuple(
            sorted(self.fold(value, self.prime) for value in row)
        )
        if 0 in projected:
            raise ValueError("row contains a coordinate divisible by p")
        return self.canonical_level_one(projected)

    def canonical_signs(self, row: Row, level: int) -> Row:
        modulus = level * self.prime
        return tuple(sorted(self.fold(value, modulus) for value in row))

    def validate_row(self, row: Row, level: int) -> None:
        if len(row) != self.k:
            raise ValueError("row has the wrong length")
        modulus = level * self.prime
        if any(value <= 0 or value >= modulus for value in row):
            raise ValueError("row coordinate is outside the level")
        if any(value % self.prime == 0 for value in row):
            raise ValueError("row coordinate is zero modulo p")
