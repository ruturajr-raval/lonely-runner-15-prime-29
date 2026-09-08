# Release v0.1.2

## Release Identity

| Field | Value |
| --- | --- |
| Title | A Level-15 Certificate for the Prime-29 Gate in the Fifteen-Runner Lonely Runner Problem |
| Author | Ruturaj R Raval |
| Affiliation | Independent Researcher |
| ORCID | [0000-0003-4930-8981](https://orcid.org/0000-0003-4930-8981) |
| Tagged release | [`v0.1.2`](https://github.com/ruturajr-raval/lonely-runner-15-prime-29/releases/tag/v0.1.2) |
| Release date | 2026-09-08 |
| Release commit | Pending - no commit or tag was created while preparing this patch |
| Version DOI | [`10.5281/zenodo.22647790`](https://doi.org/10.5281/zenodo.22647790) |
| Concept DOI | [`10.5281/zenodo.22539841`](https://doi.org/10.5281/zenodo.22539841) |
| Archive status | Paper-inclusive Zenodo successor draft uploaded and verified; GitHub and Zenodo publication pending |
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

## Patch Scope

Version `v0.1.2` is an archival and documentation patch. It adds an
explicitly named compiled report PDF, a deterministic report-source archive,
and `SHA256SUMS` to the archival release set. The selected certificate,
proof objects, data, and computations are unchanged. The certificate archive
is regenerated with the current replay README, so its packaging documentation
is refreshed without changing the certificate payload.

The theorem, proof, certificate, data, computations, exact solver outputs,
CNF, DRAT proof, and claim boundary are unchanged from `v0.1.1`.

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

From a repository checkout, `make release-verify` additionally checks that
the release directory is closed and that every asset matches
`.release-record.json`.

## Release And Archive

- Public repository:
  `https://github.com/ruturajr-raval/lonely-runner-15-prime-29`
- Release identity:
  `https://github.com/ruturajr-raval/lonely-runner-15-prime-29/releases/tag/v0.1.2`
- Version DOI: `10.5281/zenodo.22647790`
- Release status: `prepared`
- Stable concept DOI: `10.5281/zenodo.22539841`
- Release commit: `pending`
- Tagged CI stages and verifies a draft GitHub release. Publication remains
  an explicit post-verification action.

Release assets:

- `lonely-runner-15-prime-29-paper.pdf`: `b49620aa4c530b67fa95b94b114cd99d5b1f97969fecafc4567eab0c5cb93e9c`
- `lonely-runner-15-prime-29-source.tar.gz`: `e234baed75493fefce83600b01e0b2da758b4dfd2b6cfeff855d170a9bcb0cec`
- `lonely-runner-15-prime-29-certificate-v1.tar.gz`: `70bb4a809015e348cefdf7cb252f4aa929865af40fac665d78fb4016664dafcf`
- `SHA256SUMS`: `f60ba896a637dcd9b568fa5abaefee8c2e277b6c29ed6a99c4ee27b3ccc09bd1`

- Zenodo archive: `pending`

The prior `v0.1.1` archive remains available at version DOI
`10.5281/zenodo.22541517`; its 110 files matched release commit
`bfc58364d975a862153307766386b51fe8289e57` byte for byte. The new `v0.1.2`
Zenodo draft `10.5281/zenodo.22647790` contains the compiled paper,
deterministic source archive, certificate archive, and checksum manifest
listed above. All four files were verified against the local release set.
The draft has not been published.

## Provenance Boundary

Project-original source, certificate assembly, documentation, and report
material are MIT licensed. The finite-checking framework is attributed to the
cited literature and implemented independently. Kissat, DRAT-trim, and
`rate` remain external tools under their upstream terms; their exact source
revisions are bound in the certificate provenance.

## Review Status

The mathematical release passed theorem-scope, exact-solver, CNF, dual
proof-checker, source-binding, mutation, manuscript, and release-metadata
review. The `v0.1.2` local paper and release assets are verified separately
before publication. No external mathematical or peer review is claimed.

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

Release `v0.1.2` is a paper-inclusive archival and documentation patch for
the theorem `J(14,29) = empty`. It adds an explicit compiled PDF,
deterministic source archive, and checksums while leaving the theorem, proof,
certificate, data, and computations unchanged. The result closes one prime
gate and does not prove the full fifteen-runner Lonely Runner Conjecture.

## Citation

Citation metadata is in `CITATION.cff`. Cite the paper-inclusive `v0.1.2`
archival patch using version DOI `10.5281/zenodo.22647790`.
Historical release scope is summarized in `RELEASE_NOTES.md`.
