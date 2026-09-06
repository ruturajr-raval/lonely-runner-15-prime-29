# Research Plan

Status date: 2026-09-06

## Completed Milestone

The first publishable milestone is complete:

```text
J(14,29) = empty.
```

The result has a source-bound certificate, two exact coprime
implementations, a checked DRAT proof for the noncoprime branch, mutation
tests, and a complete replay path.

## Ultimate Target

Prove `LRC(14)`, the Lonely Runner Conjecture for fifteen total runners.
Within the current finite-checking framework, this requires closed prime
gates whose logarithmic mass exceeds

```text
log B_14 = 810.0739811140556.
```

Prime 29 contributes `3.367295829986474`, so substantially more gates or a
stronger structural theorem are still required.

## Next Mathematical Work

1. Generalize the factor-15 CRT reduction to additional primes whose
   level-one orbit structure is manageable.
2. Rank candidate primes by orbit count, forced-residue structure, and
   expected proof cost.
3. Prefer proof-producing SAT for branches that admit compact CNF encodings.
4. Retain dual exact implementations for branches solved by bespoke search.
5. Search for structural lemmas that close a family of primes rather than
   one gate at a time.
6. Track the cumulative certified prime mass against the finite-checking
   threshold.

## Publication Standard

A further gate is publishable only when it has:

- an exact theorem statement and explicit claim boundary;
- complete source-bound artifacts;
- deterministic integrity verification;
- a compact proof object or an independently implemented exhaustive replay;
- adversarial mutation tests;
- a refreshed prior-art audit;
- a technical report that explains the reduction without relying on code.

Timeouts, unchecked solver statuses, performance-only changes, and
unreproducible computations are not mathematical results.
