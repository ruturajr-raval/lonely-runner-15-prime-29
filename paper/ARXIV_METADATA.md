# Preprint Submission Metadata

## Title

A Level-15 Certificate for the Prime-29 Gate in the Fifteen-Runner Lonely
Runner Problem

## Author

Ruturaj R Raval

Affiliation: Independent Researcher

ORCID: 0000-0003-4930-8981

## Abstract

The finite-checking approach to the Lonely Runner Conjecture associates an
eventual-improper set J(k,p) with each prime p. This report proves
J(14,29) is empty, closing the prime-29 gate for fifteen total runners. At
level one modulo 29, every folded speed class is bad at exactly one folded
time class, so the unique improper orbit is represented by
(1,2,...,14). Every level-15 lift is divided into two exhaustive symmetry
branches. In the branch containing a coordinate coprime to 15, a
Chinese-remainder reduction forces a zero residue modulo 15 in one of
coordinates 2 through 14. Separately written C++ and Rust exact solvers
reject all thirteen cases. In the branch with no coordinate coprime to 15,
a 210-variable, 1,842-clause CNF is unsatisfiable. A 368,542-byte DRAT proof
is accepted by DRAT-trim and rate. The source-bound release certificate
supports complete integrity verification, dual proof checking, and full
recompilation and replay. The closed gate contributes log(29) to the
finite-checking prime mass but does not prove the complete fifteen-runner
conjecture.

## Categories

Primary: math.NT

Cross-list: math.CO, cs.DM

## Comments

Contains an analytic level-one reduction, an exhaustive level-15 symmetry
split, a factor-15 CRT reduction, two independently written exact solvers,
a checked DRAT certificate, mutation tests, and complete replay commands.
The result closes only the prime-29 gate and does not prove LRC(14).

## Keywords

lonely runner conjecture; Diophantine approximation; finite checking;
Chinese remainder theorem; SAT solving; DRAT; computer-assisted proof

## License

arXiv.org perpetual, non-exclusive license

## Source Package

Upload the LaTeX source and only the files required to compile it. The paper
uses no external bibliography, figures, or generated tables.

## Claim Boundary

- Claimed: the unique level-one improper orbit for k=14, p=29.
- Claimed: an exhaustive coprime and noncoprime level-15 symmetry split.
- Claimed: exact exclusion of every coprime mandatory-zero case.
- Claimed: a checked DRAT exclusion of the noncoprime branch.
- Claimed: J(14,29) is empty.
- Not claimed: a proof of LRC(14).
- Not claimed: closure of another prime gate.
- Not claimed: a sufficient total prime mass.
- Not claimed: external peer review.

## Data And Code

The accompanying repository contains the selected certificate, exact source
snapshots, two coprime implementations, the noncoprime CNF and DRAT proof,
two checker logs, mutation tests, and complete replay commands.
