# Release v0.1.1

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
python3 tools/verify_p29_certificate.py \
  --certificate-dir results/p29-level15-certificate-v1 \
  --drat-trim /path/to/drat-trim \
  --rate /path/to/rate \
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
- Stable concept DOI: `10.5281/zenodo.22539841`

Release assets:

```text
lonely-runner-15-prime-29-paper.pdf
lonely-runner-15-prime-29-source.tar.gz
lonely-runner-15-prime-29-certificate-v1.tar.gz
SHA256SUMS
```

The release manifest records exact asset hashes. Zenodo assigns the version
DOI after the GitHub release is archived. The maintained `main` branch records
the DOI, release commit, asset hashes, archive filename, archive hash, and
archive file count after deposit verification.

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

## Citation

Citation metadata is in `CITATION.cff`. Cite release `v0.1.1`; its version DOI
is recorded on `main` after archival.
