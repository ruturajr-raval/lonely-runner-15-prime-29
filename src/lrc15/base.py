from __future__ import annotations

from collections.abc import Iterator
from itertools import combinations

from .model import GateModel, Row


def positive_compositions(total: int, parts: int) -> Iterator[tuple[int, ...]]:
    if parts == 1:
        yield (total,)
        return
    for first in range(1, total - parts + 2):
        for tail in positive_compositions(total - first, parts - 1):
            yield (first, *tail)


def covering_supports(model: GateModel) -> Iterator[tuple[int, ...]]:
    full_mask = (1 << model.folded_size) - 1
    classes = range(2, model.folded_size + 1)
    max_support = min(model.k, model.folded_size)
    for support_size in range(1, max_support + 1):
        for tail in combinations(classes, support_size - 1):
            support = (1, *tail)
            covered = 0
            for speed in support:
                covered |= model.bad_mask(speed)
            if covered == full_mask:
                yield support


def expand_support(model: GateModel, support: tuple[int, ...]) -> Iterator[Row]:
    for multiplicities in positive_compositions(model.k, len(support)):
        row = tuple(
            speed
            for speed, multiplicity in zip(
                support, multiplicities
            )
            for _ in range(multiplicity)
        )
        yield row


def generate_level_one(model: GateModel) -> set[Row]:
    rows: set[Row] = set()
    for support in covering_supports(model):
        for row in expand_support(model, support):
            canonical = model.canonical_level_one(row)
            if model.is_improper(canonical, level=1):
                rows.add(canonical)
    return rows
