from __future__ import annotations


P29_LEVEL15_MODULUS = 29 * 15
P29_LEVEL15_TIMES = P29_LEVEL15_MODULUS // 2


def p29_level15_residue_from_choice(
    coordinate: int,
    choice: int,
) -> int:
    if not 1 <= coordinate <= 14:
        raise ValueError("coordinate must be between 1 and 14")
    if not 0 <= choice < 15:
        raise ValueError("choice must be between 0 and 14")
    return (coordinate - choice) % 15


def p29_level15_choice_for_residue(
    coordinate: int,
    residue: int,
) -> int:
    if not 1 <= coordinate <= 14:
        raise ValueError("coordinate must be between 1 and 14")
    if not 0 <= residue < 15:
        raise ValueError("residue must be between 0 and 14")
    return (coordinate - residue) % 15


def p29_level15_bad_by_crt(
    time: int,
    coordinate: int,
    residue: int,
) -> bool:
    if not 1 <= time <= P29_LEVEL15_TIMES:
        raise ValueError("time must be a folded nonzero time class")
    if not 1 <= coordinate <= 14:
        raise ValueError("coordinate must be between 1 and 14")
    if not 0 <= residue < 15:
        raise ValueError("residue must be between 0 and 14")

    x = time % 29
    y = time % 15
    product_mod_29 = x * coordinate % 29
    product_mod_15 = y * residue % 15
    if product_mod_29 == 0:
        return product_mod_15 == 0
    return product_mod_15 in {
        product_mod_29 % 15,
        (product_mod_29 + 1) % 15,
    }


def p29_level15_zero_choice(coordinate: int) -> int:
    return p29_level15_choice_for_residue(coordinate, 0)


def p29_level15_nontrivial_times() -> tuple[int, ...]:
    return tuple(
        time
        for time in range(1, P29_LEVEL15_TIMES + 1)
        if time % 15 != 0 and time % 29 != 0
    )
