# Claim Boundaries

Status date: 2026-09-06

## Established Frontier

- Sungkawichai and Trakulthongchai establish the Lonely Runner Conjecture
  through thirteen total runners and develop the finite-checking framework
  used here.
- Allikvere reports a computer-assisted proof for fourteen total runners,
  equivalent to `LRC(13)` in the convention with thirteen moving runners.
- The next full case is `LRC(14)`, equivalent to fifteen total runners.

## What Is Proved Here

- At `k = 14`, `p = 29`, the unique level-one improper orbit is represented
  by `(1,2,...,14)`.
- Every improper level-15 lift is equivalent to a representative in one of
  two exhaustive normalized branches.
- The coprime branch has no time-covering lift. Two separately written exact
  solvers reject all thirteen mandatory-zero cases.
- The noncoprime branch has no improper lift. Its exact CNF is unsatisfiable,
  with a DRAT proof accepted by DRAT-trim and `rate`.
- Consequently,

  ```text
  J(14,29) = empty.
  ```

## What Is Not Proved

- The full Lonely Runner Conjecture for fifteen total runners is not proved.
- No prime gate other than 29 is closed by this result.
- The finite-checking threshold is not reached.
- The dual coprime runs are exhaustive source computations, not compact
  standard proof objects.
- No claim is made about unpublished or unindexed computations.
- No external peer review is claimed.

## Significance

The closed gate contributes `log(29) = 3.367295829986474` to the required
prime mass `log B_14 = 810.0739811140556`. It also supplies a reusable
factor-15 CRT reduction, a dual-language exact search design, and a
source-bound certificate format for future fifteen-runner gates.
