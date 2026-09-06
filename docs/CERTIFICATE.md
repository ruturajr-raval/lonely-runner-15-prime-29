# Certificate And Replay Guide

Status date: 2026-09-06

## Certificate layout

The selected release evidence is stored under
`results/p29-level15-certificate-v1/`. Its top-level manifest binds every
included artifact by SHA-256.

All three original production runs are bound to source commit
`f2f933bf16ab8eb5b081ddca59b18bf6b1b92e9d`. The top-level
`certificate.json` has SHA-256
`23d07c574e83270cb765502344dfc697f602667a35a7b1cddd1cab3f11098d0a`.

The certificate also contains a complete Git bundle for that commit. The
verifier checks out the declared object, compares every packaged solver and
generator source with the committed bytes, and runs the original
reconstruction verifier from that checkout.

The package contains three logically separate checks:

1. The level-one generator returns exactly the orbit represented by
   `(1,2,...,14)`.
2. Two independent exact programs reject all thirteen mandatory-zero cases
   in the coprime branch.
3. A DRAT proof, checked by two independent proof checkers, rejects the
   noncoprime branch.

## Fast integrity check

The fast check validates the manifest, all artifact hashes, all recorded
case outputs, the level-one orbit, the CRT identities, and the exact
noncoprime CNF:

```console
python3 tools/verify_p29_certificate.py \
  --certificate-dir results/p29-level15-certificate-v1
```

This does not replay the DRAT proof or rerun the long coprime searches.

## Full noncoprime proof replay

Build DRAT-trim at commit
`2e3b2dc0ecf938addbd779d42877b6ed69d9a985` and `rate` at commit
`93bf524435455ddc0b370669c17b1eb8741a026c`, then run:

```console
python3 tools/verify_p29_certificate.py \
  --certificate-dir results/p29-level15-certificate-v1 \
  --drat-trim /path/to/drat-trim \
  --rate /path/to/rate
```

Both checkers must print the exact line `s VERIFIED` and exit successfully.

## Full source replay

The strongest replay recompiles the exact C++ and Rust source snapshots
stored inside the selected certificate, checks the noncoprime DRAT proof,
and reruns all twenty-six coprime cases:

```console
python3 tools/verify_p29_certificate.py \
  --certificate-dir results/p29-level15-certificate-v1 \
  --drat-trim /path/to/drat-trim \
  --rate /path/to/rate \
  --full-replay \
  --jobs 4
```

This path does not substitute current working-tree sources for the archived
production sources.

## New working-tree reruns

The current working tree can also produce a new C++ run:

```console
make terminal-solver
python3 tools/run_p29_zero_cases.py \
  --solver build/solve_p29_level15 \
  --source tools/solve_p29_level15.cpp \
  --implementation cpp-direct-1.1.0 \
  --log-dir results/replay-cpp/logs \
  --summary results/replay-cpp/summary.json \
  --jobs 4
```

Produce a new Rust run with:

```console
make rust-verifier
python3 tools/run_p29_zero_cases.py \
  --solver build/verify_p29_level15 \
  --source tools/verify_p29_level15.rs \
  --implementation rust-crt-1.0.0 \
  --log-dir results/replay-rust/logs \
  --summary results/replay-rust/summary.json \
  --jobs 4
```

The two implementations use different arithmetic representations and
different branching units. Their node counts need not agree. Each run is
accepted only if all thirteen cases are `UNSAT`, every expected log field is
present exactly once, and all bound provenance files remain unchanged during
the run.

These commands create new provenance records for the checked-out commit.
They do not recreate the original summary bytes unless the original source
commit and toolchain are also reproduced.

## Rebuilding the noncoprime query

The exact query can be regenerated with:

```console
python3 tools/build_fiber_cnf.py \
  --k 14 \
  --prime 29 \
  --multiplier 15 \
  --symmetry-case noncoprime \
  --output results/rebuilt-noncoprime.cnf
```

The certificate verifier compares the parsed variables and clauses against a
fresh in-memory construction, so comments and filenames do not carry any
mathematical meaning.

## Trust boundary

The release includes source, exact inputs, exact outputs, compact logs, and
the standard proof object for the noncoprime branch. It does not require
trust in a hosted service or in an unpublished binary.

The coprime branch is certified by two independently written exhaustive
programs rather than by a compact standard proof object. Full assurance for
that branch therefore comes from source review and independent reruns.

The release archive for the selected certificate is built deterministically:

```console
make certificate-bundle
```
