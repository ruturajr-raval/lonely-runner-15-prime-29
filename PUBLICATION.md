# Release v0.1.1

## Release Identity

| Field | Value |
| --- | --- |
| Title | A Level-15 Certificate for the Prime-29 Gate in the Fifteen-Runner Lonely Runner Problem |
| Author | Ruturaj R Raval |
| Affiliation | Independent Researcher |
| ORCID | [0000-0003-4930-8981](https://orcid.org/0000-0003-4930-8981) |
| Tagged release | [`v0.1.1`](https://github.com/ruturajr-raval/lonely-runner-15-prime-29/releases/tag/v0.1.1) |
| Release date | 2026-09-06 |
| Audited release commit | `bfc58364d975a862153307766386b51fe8289e57` |
| Version DOI | [`10.5281/zenodo.22541517`](https://doi.org/10.5281/zenodo.22541517) |
| Concept DOI | [`10.5281/zenodo.22539841`](https://doi.org/10.5281/zenodo.22539841) |
| Archive status | Published 110-file Zenodo snapshot matching the release tag |
| License | MIT for project-original material |

## Background

The finite-checking approach to the Lonely Runner Conjecture associates an
eventual-improper set `J(k,p)` with each prime `p`. Closing enough prime
gates proves the conjecture for `k` moving runners.

This release treats `k = 14`, corresponding to fifteen total runners, and
the prime `p = 29`.

## Result

The release proves

```text
J(14,29) = empty.
```

At level one, the unique improper orbit is represented by
`(1,2,...,14)`. Every improper level-15 lift is equivalent to a lift in one
of two jointly exhaustive symmetry branches: coprime or noncoprime.

For the coprime branch, a CRT reduction forces a zero residue modulo 15 in
one of coordinates 2 through 14. A C++ direct-arithmetic solver and a Rust
CRT solver independently reject all thirteen cases.

For the noncoprime branch, Kissat reports an exact 210-variable,
1,842-clause CNF as unsatisfiable and emits a 368,542-byte DRAT proof.
DRAT-trim and `rate` both accept the proof.

The combined result closes the prime-29 finite-checking gate.

## Correction Scope

Version `v0.1.1` corrects overview wording from "every level-15 lift" to
"every improper level-15 lift." The formal lemma, proof, certificate, data,
and computational results are unchanged. Version `v0.1.0` remains archived,
but `v0.1.1` supersedes it for wording accuracy.

## Verification

```bash
make test
make certificate-fast
```

The full replay recompiles the exact C++ and Rust source snapshots packaged
with the certificate and reruns all twenty-six coprime cases:

```bash
DRAT_TRIM_BIN="${DRAT_TRIM_BIN:-drat-trim}"
RATE_BIN="${RATE_BIN:-rate}"
python3 tools/verify_p29_certificate.py \
  --certificate-dir results/p29-level15-certificate-v1 \
  --drat-trim "$DRAT_TRIM_BIN" \
  --rate "$RATE_BIN" \
  --full-replay \
  --jobs 4
```

The certificate also contains the noncoprime CNF, proof, checker logs, and
generator source snapshots. A bundled Git object archive binds those source
snapshots to the declared commit. Every artifact is bound by SHA-256.

For downloaded release assets, place all four files in one directory and
verify the release manifest with:

```bash
shasum -a 256 -c SHA256SUMS
```

## Release And Archive

- Public repository:
  `https://github.com/ruturajr-raval/lonely-runner-15-prime-29`
- GitHub release:
  `https://github.com/ruturajr-raval/lonely-runner-15-prime-29/releases/tag/v0.1.1`
- Version DOI: `10.5281/zenodo.22541517`
- Stable concept DOI: `10.5281/zenodo.22539841`
- Release commit: `bfc58364d975a862153307766386b51fe8289e57`

Release assets:

- `lonely-runner-15-prime-29-paper.pdf`: `57e727d9699db7b154591d0e132e0b7cd449241b1381396a98d62ae2025dc37b`
- `lonely-runner-15-prime-29-source.tar.gz`: `df671d1a94d3c22481d8fc103e14b768f84a533c24178925b69e445264b8bda5`
- `lonely-runner-15-prime-29-certificate-v1.tar.gz`: `bc52d11ced8082405fa2a428a0fb605b7c0aefa7cfaa013f104fddaa86777c39`
- `SHA256SUMS`: `1e2343e5b22e22bc404b0e1ffe25563a0cfc81827f2b16790ca70ee0f7582d1d`

- Zenodo archive: `ruturajr-raval/lonely-runner-15-prime-29-v0.1.1.zip`
- Zenodo archive SHA-256: `8e9a463dd95acb8a40f927583230bc8140e6139b479fd59059d98a27adebcd72`
- Archived file count: `110`

All 110 archived files match the immutable `v0.1.1` tag tree byte for byte.

## Provenance Boundary

Project-original source, certificate assembly, documentation, and report
material are MIT licensed. The finite-checking framework is attributed to the
cited literature and implemented independently. Kissat, DRAT-trim, and
`rate` remain external tools under their upstream terms; their exact source
revisions are bound in the certificate provenance.

## Review Status

The release passed theorem-scope, exact-solver, CNF, dual proof-checker,
source-binding, mutation, manuscript, and release-metadata review. The full
tagged replay rebuilds and checks the selected certificate from its recorded
sources. No external mathematical or peer review is claimed.

## What Is Not Claimed

- The full fifteen-runner Lonely Runner Conjecture is not proved.
- No prime gate other than 29 is closed.
- The accumulated prime mass does not reach the finite-checking threshold.
- The coprime searches are not represented by compact standard proof
  objects. Their strongest check is source review and full dual replay.
- No external peer review is claimed.
- No priority claim is made over unpublished or unindexed work.

## Significance

The gate contributes

```text
log(29) = 3.367295829986474
```

to the current target

```text
log B_14 = 810.0739811140556.
```

It also supplies a reusable factor-15 CRT reduction, independently written
exact solvers, and a compact source-bound certificate design for future
fifteen-runner gates.

## Remaining Work And Next Acceptance Gate

The next result gate is a second exact prime-gate theorem, or a theorem that
closes a stated family of gates, with source-bound evidence and independent
replay. A full `LRC(14)` claim additionally requires verified closed-gate
mass above `log B_14 = 810.0739811140556`, unless a separate theorem replaces
that threshold.

## Public Summary

Release `v0.1.1` proves `J(14,29) = empty`, closing the prime-29
finite-checking gate for fifteen total runners. Two independently written
exact solvers reject the coprime branch, and a DRAT proof accepted by
DRAT-trim and `rate` rejects the noncoprime branch. This closes one prime gate
and does not prove the full fifteen-runner Lonely Runner Conjecture.

## Citation

Citation metadata is in `CITATION.cff`. Cite release `v0.1.1` using version
DOI `10.5281/zenodo.22541517`.
Historical release scope is summarized in `RELEASE_NOTES.md`.
