# Prime-29 Gate for Fifteen Lonely Runners

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22539841.svg)](https://doi.org/10.5281/zenodo.22539841)

This repository proves

```text
J(14,29) = empty.
```

Equivalently, it closes the prime-29 finite-checking gate for the Lonely
Runner Conjecture with fifteen total runners, after one runner is fixed to be
stationary.

The result is a rigorous component of the finite-checking program for the
next open case. It does not prove the full fifteen-runner conjecture.

The exact `v0.1.0` release is archived at version DOI
`10.5281/zenodo.22539842`. All repository versions are collected under the
stable concept DOI `10.5281/zenodo.22539841`.

## Background

For a prime `p`, the finite-checking method studies level-one tuples that
remain improper through every modular lift. Their eventual-improper set is
denoted by `J(k,p)`, where `k` is the number of moving runners. Proving
`J(k,p) = empty` closes one prime gate.

The published 2026 finite-checking reports cover the conjecture through
fourteen total runners. The next case has `k = 14`, and a complete
finite-checking proof requires enough closed prime gates that their
logarithmic mass exceeds the threshold

```text
log B_14 = 810.0739811140556.
```

The prime-29 gate contributes

```text
log(29) = 3.367295829986474,
```

or about 0.41568 percent of that threshold.

## Main Result

At level one modulo 29, every folded speed class is bad at exactly one folded
time class. An improper 14-tuple must therefore contain every folded class
once. Up to permutation and signs, the unique level-one improper tuple is

```text
(1, 2, 3, ..., 14).
```

Every level-15 lift of this tuple is then divided into two exhaustive
symmetry branches.

- In the coprime branch, a CRT reduction forces one of coordinates 2 through
  14 to have residue zero modulo 15. Two separately written exact solvers,
  one in C++ and one in Rust, reject all thirteen coordinate-zero cases.
- In the noncoprime branch, a 210-variable, 1,842-clause CNF is unsatisfiable.
  Kissat produced a 368,542-byte DRAT proof accepted independently by
  DRAT-trim and `rate`.

The two branches contain no improper level-15 lift, so the unique level-one
orbit is eventually proper and `J(14,29)` is empty.

The complete theorem and reduction are in
[`docs/P29_LEVEL15_THEOREM.md`](docs/P29_LEVEL15_THEOREM.md).

## Reproduction

Run the test suite and the fast certificate verifier:

```bash
make test
make certificate-fast
```

Build both exact coprime solvers:

```bash
make terminal-solver rust-verifier
build/verify_p29_level15 --self-test
```

Replay the noncoprime DRAT proof with locally built copies of DRAT-trim and
`rate`:

```bash
python3 tools/verify_p29_certificate.py \
  --certificate-dir results/p29-level15-certificate-v1 \
  --drat-trim /path/to/drat-trim \
  --rate /path/to/rate
```

Recompile the source snapshots stored inside the certificate and rerun all
twenty-six coprime searches:

```bash
python3 tools/verify_p29_certificate.py \
  --certificate-dir results/p29-level15-certificate-v1 \
  --drat-trim /path/to/drat-trim \
  --rate /path/to/rate \
  --full-replay \
  --jobs 4
```

The fast mode verifies integrity, exact claims, level-one generation, CRT
identities, all logs, and the reconstructed noncoprime CNF. It does not
replace the DRAT replay or the long coprime reruns.

GitHub release downloads include `SHA256SUMS`. Place the PDF, source archive,
certificate archive, and checksum file in one directory, then run:

```bash
shasum -a 256 -c SHA256SUMS
```

## Evidence

The selected certificate is
[`results/p29-level15-certificate-v1`](results/p29-level15-certificate-v1).
Its top-level manifest binds every included artifact by SHA-256 and records
the source commit used for all original runs.

The evidence includes:

- exact source snapshots for both coprime solvers;
- a Git object bundle binding those snapshots to the declared source commit;
- thirteen C++ and thirteen Rust UNSAT transcripts;
- the exact noncoprime CNF and DRAT proof;
- logs from two independent DRAT checkers;
- source snapshots for the noncoprime generator;
- a standalone verifier with fail-closed mutation tests.

See [`docs/CERTIFICATE.md`](docs/CERTIFICATE.md) for the trust boundary and
replay procedure.

## Claim Boundary

This project claims:

- the unique level-one improper orbit for `k = 14`, `p = 29`;
- the exhaustive coprime and noncoprime symmetry split at level 15;
- exact exclusion of all thirteen coprime coordinate-zero cases by both
  implementations;
- a checked DRAT exclusion of the noncoprime branch;
- the theorem `J(14,29) = empty`.

It does not claim:

- a proof of `LRC(14)`;
- closure of any prime gate other than 29;
- that the current gate mass reaches the finite-checking threshold;
- an independent external mathematical review;
- priority over unpublished or unindexed work.

The dated public-source audit is in
[`docs/PRIOR_ART.md`](docs/PRIOR_ART.md).

## Citation

Citation metadata is in `CITATION.cff`. Cite the exact `v0.1.0` result using
version DOI `10.5281/zenodo.22539842`. The stable all-versions DOI is
`10.5281/zenodo.22539841`. The technical report source is under `paper/`.

## Author

Ruturaj R Raval  
Independent Researcher  
ORCID: 0000-0003-4930-8981
