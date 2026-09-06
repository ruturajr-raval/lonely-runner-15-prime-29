from __future__ import annotations

from dataclasses import dataclass, field
from math import gcd

from .crt import p29_level15_nontrivial_times
from .model import GateModel, Row, distance_mod


def prime_factors(value: int) -> tuple[int, ...]:
    factors: list[int] = []
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            factors.append(divisor)
            while value % divisor == 0:
                value //= divisor
        divisor += 1
    if value > 1:
        factors.append(value)
    return tuple(factors)


@dataclass
class CNF:
    variables: int
    clauses: list[tuple[int, ...]] = field(default_factory=list)

    def add(self, literals: list[int] | tuple[int, ...]) -> None:
        self.clauses.append(tuple(literals))

    def dimacs(self, comments: list[str] | None = None) -> str:
        lines: list[str] = []
        for comment in comments or []:
            lines.append(f"c {comment}")
        lines.append(f"p cnf {self.variables} {len(self.clauses)}")
        for clause in self.clauses:
            lines.append(" ".join(map(str, clause)) + " 0")
        return "\n".join(lines) + "\n"

    def is_satisfied(self, true_variables: set[int]) -> bool:
        for clause in self.clauses:
            if not any(
                (literal > 0 and literal in true_variables)
                or (literal < 0 and -literal not in true_variables)
                for literal in clause
            ):
                return False
        return True


@dataclass(frozen=True)
class FiberEncoding:
    model: GateModel
    parent: Row
    level: int
    multiplier: int

    def __post_init__(self) -> None:
        if self.level < 1:
            raise ValueError("level must be positive")
        if self.multiplier < 1:
            raise ValueError("multiplier must be positive")

    @property
    def new_level(self) -> int:
        return self.level * self.multiplier

    @property
    def old_modulus(self) -> int:
        return self.level * self.model.prime

    @property
    def new_modulus(self) -> int:
        return self.new_level * self.model.prime

    def variable(self, coordinate: int, choice: int) -> int:
        return coordinate * self.multiplier + choice + 1

    def lifted_value(self, coordinate: int, choice: int) -> int:
        return self.parent[coordinate] + choice * self.old_modulus

    def assignment_row(self, choices: tuple[int, ...]) -> Row:
        return tuple(
            self.lifted_value(coordinate, choice)
            for coordinate, choice in enumerate(choices)
        )

    def true_variables(self, choices: tuple[int, ...]) -> set[int]:
        return {
            self.variable(coordinate, choice)
            for coordinate, choice in enumerate(choices)
        }

    def build(
        self,
        *,
        include_gcd: bool = True,
        time_classes: tuple[int, ...] | None = None,
    ) -> CNF:
        self.model.validate_row(self.parent, self.level)
        cnf = CNF(variables=self.model.k * self.multiplier)

        # Exactly one lift choice per labeled coordinate.
        for coordinate in range(self.model.k):
            choices = [
                self.variable(coordinate, choice)
                for choice in range(self.multiplier)
            ]
            cnf.add(choices)
            for left in range(self.multiplier):
                for right in range(left + 1, self.multiplier):
                    cnf.add(
                        [
                            -self.variable(coordinate, left),
                            -self.variable(coordinate, right),
                        ]
                    )

        # No witness means every time class has at least one bad coordinate.
        if time_classes is None:
            times = tuple(range(1, self.new_modulus // 2 + 1))
        else:
            times = time_classes
            if (
                len(set(times)) != len(times)
                or any(
                    not 1 <= time <= self.new_modulus // 2
                    for time in times
                )
            ):
                raise ValueError("time classes must be unique folded classes")

        for time in times:
            bad_literals: list[int] = []
            for coordinate in range(self.model.k):
                for choice in range(self.multiplier):
                    value = self.lifted_value(coordinate, choice)
                    if (
                        self.model.threshold_denominator
                        * distance_mod(time * value, self.new_modulus)
                        < self.new_modulus
                    ):
                        bad_literals.append(
                            self.variable(coordinate, choice)
                        )
            cnf.add(bad_literals)

        # To avoid the gcd properness clause, each prime factor of the level
        # must fail to divide at least two coordinates.
        if include_gcd:
            for factor in prime_factors(self.new_level):
                for omitted in range(self.model.k):
                    nondivisible_literals: list[int] = []
                    for coordinate in range(self.model.k):
                        if coordinate == omitted:
                            continue
                        for choice in range(self.multiplier):
                            value = self.lifted_value(coordinate, choice)
                            if value % factor != 0:
                                nondivisible_literals.append(
                                    self.variable(coordinate, choice)
                                )
                    cnf.add(nondivisible_literals)

        return cnf

    def build_p29_level15_reduced_time_cover(self) -> CNF:
        expected_parent = tuple(range(1, 15))
        if (
            self.model.k != 14
            or self.model.prime != 29
            or self.parent != expected_parent
            or self.level != 1
            or self.multiplier != 15
        ):
            raise ValueError(
                "the reduced p29 cover applies only to the "
                "full-residue k=14 level-15 fiber"
            )
        times = (29, *p29_level15_nontrivial_times())
        return self.build(
            include_gcd=False,
            time_classes=times,
        )

    def variable_for_folded_value(self, target: int) -> int:
        matches: list[int] = []
        for coordinate in range(self.model.k):
            for choice in range(self.multiplier):
                value = self.lifted_value(coordinate, choice)
                if self.model.fold(value, self.new_modulus) == target:
                    matches.append(self.variable(coordinate, choice))
        if len(matches) != 1:
            raise ValueError(
                f"expected one choice for folded value {target}, "
                f"found {len(matches)}"
            )
        return matches[0]


def add_p29_level15_symmetry_case(
    cnf: CNF,
    encoding: FiberEncoding,
    case: str,
) -> None:
    expected_parent = tuple(range(1, 15))
    if (
        encoding.model.k != 14
        or encoding.model.prime != 29
        or encoding.parent != expected_parent
        or encoding.level != 1
        or encoding.multiplier != 15
    ):
        raise ValueError(
            "the p29 level-15 symmetry split applies only to the "
            "full-residue k=14 fiber"
        )

    if case == "coprime":
        cnf.add([encoding.variable_for_folded_value(1)])
        return

    if case == "noncoprime":
        for coordinate in range(encoding.model.k):
            for choice in range(encoding.multiplier):
                value = encoding.lifted_value(coordinate, choice)
                if gcd(value, encoding.new_level) == 1:
                    cnf.add([-encoding.variable(coordinate, choice)])
        cnf.add([encoding.variable_for_folded_value(3)])
        return

    raise ValueError(f"unknown symmetry case: {case}")
