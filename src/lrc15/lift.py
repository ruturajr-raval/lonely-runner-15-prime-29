from __future__ import annotations

from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass

from .model import GateModel, Row


@dataclass
class LiftStats:
    parents: int = 0
    nodes: int = 0
    leaves: int = 0
    potential_prunes: int = 0
    gcd_prunes: int = 0
    survivors_before_deduplication: int = 0


def popcount(value: int) -> int:
    method = getattr(value, "bit_count", None)
    if method is not None:
        return method()
    return bin(value).count("1")


def weak_compositions(total: int, parts: int) -> Iterator[tuple[int, ...]]:
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in weak_compositions(total - first, parts - 1):
            yield (first, *tail)


def lift_rows_for_one_parent(
    model: GateModel,
    row: Row,
    level: int,
    multiplier: int,
) -> Iterator[Row]:
    if multiplier < 2:
        raise ValueError("lift multiplier must be at least 2")
    model.validate_row(row, level)
    old_modulus = level * model.prime
    new_level = level * multiplier
    groups = sorted(Counter(row).items())

    partial: list[int] = []

    def visit(group_index: int) -> Iterator[Row]:
        if group_index == len(groups):
            yield model.canonical_signs(tuple(partial), new_level)
            return

        value, multiplicity = groups[group_index]
        lifted_values = [
            value + offset * old_modulus for offset in range(multiplier)
        ]
        for counts in weak_compositions(multiplicity, multiplier):
            start = len(partial)
            for lifted, count in zip(lifted_values, counts):
                partial.extend([lifted] * count)
            yield from visit(group_index + 1)
            del partial[start:]

    yield from visit(0)


def _group_options(
    model: GateModel,
    *,
    value: int,
    multiplicity: int,
    level: int,
    multiplier: int,
) -> list[tuple[Row, int]]:
    old_modulus = level * model.prime
    new_level = level * multiplier
    new_modulus = new_level * model.prime
    lifted_values = [
        value + offset * old_modulus for offset in range(multiplier)
    ]
    options: set[tuple[Row, int]] = set()
    for counts in weak_compositions(multiplicity, multiplier):
        values = tuple(
            sorted(
                model.fold(lifted, new_modulus)
                for lifted, count in zip(lifted_values, counts)
                for _ in range(count)
            )
        )
        bad_mask = 0
        for lifted, count in zip(lifted_values, counts):
            if count:
                bad_mask |= model.bad_mask_at_level(new_level, lifted)
        options.add((values, bad_mask))
    return sorted(options, key=lambda option: (-popcount(option[1]), option[0]))


def lift_improper_rows_for_one_parent(
    model: GateModel,
    row: Row,
    level: int,
    multiplier: int,
    stats: LiftStats | None = None,
) -> set[Row]:
    if multiplier < 2:
        raise ValueError("lift multiplier must be at least 2")
    model.validate_row(row, level)
    if stats is None:
        stats = LiftStats()
    stats.parents += 1

    new_level = level * multiplier
    full_mask = (1 << (new_level * model.prime // 2)) - 1
    groups = [
        _group_options(
            model,
            value=value,
            multiplicity=multiplicity,
            level=level,
            multiplier=multiplier,
        )
        for value, multiplicity in sorted(Counter(row).items())
    ]

    # Process restrictive groups first. The order does not change the set of
    # assignments because each group represents one distinct parent value.
    groups.sort(
        key=lambda options: (
            len(options),
            -sum(popcount(mask) for _, mask in options),
        )
    )

    guaranteed = 0
    for options in groups:
        common = full_mask
        for _, mask in options:
            common &= mask
        guaranteed |= common

    suffix_possible = [0] * (len(groups) + 1)
    for index in range(len(groups) - 1, -1, -1):
        possible = 0
        for _, mask in groups[index]:
            possible |= mask
        suffix_possible[index] = suffix_possible[index + 1] | possible

    survivors: set[Row] = set()
    partial: list[int] = []

    def visit(group_index: int, covered: int) -> None:
        stats.nodes += 1
        if covered | suffix_possible[group_index] != full_mask:
            stats.potential_prunes += 1
            return
        if group_index == len(groups):
            stats.leaves += 1
            lifted = tuple(sorted(partial))
            if model.satisfies_gcd_clause(lifted, new_level):
                stats.gcd_prunes += 1
                return
            stats.survivors_before_deduplication += 1
            survivors.add(lifted)
            return

        for values, mask in groups[group_index]:
            start = len(partial)
            partial.extend(values)
            visit(group_index + 1, covered | mask)
            del partial[start:]

    visit(0, guaranteed)
    return survivors


def lift_filter_with_stats(
    model: GateModel,
    rows: set[Row],
    level: int,
    multiplier: int,
) -> tuple[set[Row], LiftStats]:
    stats = LiftStats()
    survivors: set[Row] = set()
    for row in sorted(rows):
        survivors.update(
            lift_improper_rows_for_one_parent(
                model,
                row,
                level,
                multiplier,
                stats,
            )
        )
    return survivors, stats


def lift_filter(
    model: GateModel,
    rows: set[Row],
    level: int,
    multiplier: int,
) -> set[Row]:
    return lift_filter_with_stats(model, rows, level, multiplier)[0]
