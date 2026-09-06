from __future__ import annotations

from dataclasses import dataclass

from .lift import lift_filter_with_stats
from .model import GateModel, Row


@dataclass(frozen=True)
class Stage:
    operation: str
    argument: int | None
    input_level: int
    output_level: int
    input_rows: int
    output_rows: int
    search_nodes: int
    search_leaves: int
    potential_prunes: int
    gcd_prunes: int


def apply_pipeline(
    model: GateModel,
    rows: set[Row],
    operations: list[int | str],
) -> tuple[set[Row], int, list[Stage]]:
    level = 1
    stages: list[Stage] = []
    current = set(rows)

    for operation in operations:
        before = len(current)
        input_level = level
        if operation == "p":
            current = {
                model.project_level_one(row)
                for row in current
            }
            level = 1
            name = "project"
            argument = None
            search_nodes = 0
            search_leaves = 0
            potential_prunes = 0
            gcd_prunes = 0
        elif isinstance(operation, int):
            current, stats = lift_filter_with_stats(
                model, current, level, operation
            )
            level *= operation
            name = "lift"
            argument = operation
            search_nodes = stats.nodes
            search_leaves = stats.leaves
            potential_prunes = stats.potential_prunes
            gcd_prunes = stats.gcd_prunes
        else:
            raise ValueError(f"unknown pipeline operation: {operation}")

        stages.append(
            Stage(
                operation=name,
                argument=argument,
                input_level=input_level,
                output_level=level,
                input_rows=before,
                output_rows=len(current),
                search_nodes=search_nodes,
                search_leaves=search_leaves,
                potential_prunes=potential_prunes,
                gcd_prunes=gcd_prunes,
            )
        )
        if not current:
            break

    return current, level, stages
