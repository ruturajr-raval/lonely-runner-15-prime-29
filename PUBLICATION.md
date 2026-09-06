# Release v0.1.0

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
`(1,2,...,14)`. Every level-15 lift belongs to an exhaustive coprime or
noncoprime symmetry branch.

For the coprime branch, a CRT reduction forces a zero residue modulo 15 in
one of coordinates 2 through 14. A C++ direct-arithmetic solver and a Rust
CRT solver independently reject all thirteen cases.

For the noncoprime branch, Kissat reports an exact 210-variable,
1,842-clause CNF as unsatisfiable and emits a 368,542-byte DRAT proof.
DRAT-trim and `rate` both accept the proof.

The combined result closes the prime-29 finite-checking gate.

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
  `https://github.com/ruturajr-raval/lonely-runner-15-prime-29/releases/tag/v0.1.0`
- Version DOI: `10.5281/zenodo.22539842`
- Stable concept DOI: `10.5281/zenodo.22539841`
- Release commit:
  `229dc21c13faa58d67c3207e4a2b8c277ac27e72`

Release assets:

```text
lonely-runner-15-prime-29-paper.pdf
SHA-256 d5a660078866f6d488dcf2b9506c901b3e47d767f49a249ad7d73668b2552338

lonely-runner-15-prime-29-source.tar.gz
SHA-256 1a363a62bccefcf4af8c3b67c89a69ea2fe79755819df46bcee3e2a084e1f78e

lonely-runner-15-prime-29-certificate-v1.tar.gz
SHA-256 bc52d11ced8082405fa2a428a0fb605b7c0aefa7cfaa013f104fddaa86777c39

SHA256SUMS
SHA-256 17df2e0286ecba31fcc3c99a6a681675df3bcaafec4304cbfcaba1202c149df1
```

The Zenodo repository snapshot is
`ruturajr-raval/lonely-runner-15-prime-29-v0.1.0.zip`, with SHA-256
`2d4aed1444dd95dec231f6638a4dbe4608657e390c3e12317164869e00d6a7f4`.
All 109 archived files match the immutable release tag tree byte for byte.

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

Citation metadata is in `CITATION.cff`. Cite the archived `v0.1.0` result
using version DOI `10.5281/zenodo.22539842`.
