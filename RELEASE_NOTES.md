# v0.1.1

## [v0.1.1](https://github.com/ruturajr-raval/lonely-runner-15-prime-29/releases/tag/v0.1.1) - 2026-09-06

This patch release corrects overview and abstract wording from "every
level-15 lift" to "every improper level-15 lift." The formal lemma, theorem,
proof, certificate, data, and computational results are unchanged.

Release `v0.1.0` remains archived but is superseded by `v0.1.1` for wording
accuracy.

This release proves `J(14,29) = empty`, closing the prime-29 finite-checking
gate for fifteen total runners.

Included evidence:

- the unique level-one improper orbit;
- a complete factor-15 CRT reduction;
- thirteen C++ and thirteen Rust coprime UNSAT runs;
- a 210-variable noncoprime CNF;
- a 368,542-byte DRAT proof checked by DRAT-trim and `rate`;
- a source-bound SHA-256 certificate;
- a Git object bundle binding the evidence to its declared source commit;
- fast, DRAT, and full source-replay verification modes;
- adversarial certificate mutation tests;
- a technical report and publication metadata.

The release does not prove the full fifteen-runner Lonely Runner Conjecture.
It is archived at version DOI `10.5281/zenodo.22541517`.

## [v0.1.0](https://github.com/ruturajr-raval/lonely-runner-15-prime-29/releases/tag/v0.1.0) - 2026-09-06

- First release of the theorem `J(14,29) = empty`.
- Included the factor-15 CRT reduction, dual exact coprime solvers,
  noncoprime CNF and DRAT proof, source-bound certificate, mutation tests,
  technical report, and release metadata.
- Used imprecise overview wording about level-15 lifts that was corrected in
  `v0.1.1`; the formal theorem and evidence were already scoped correctly.
- Did not prove the full fifteen-runner Lonely Runner Conjecture.
- Archived at version DOI `10.5281/zenodo.22539842`.
