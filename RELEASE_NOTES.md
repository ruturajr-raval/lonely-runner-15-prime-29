# v0.1.0

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
