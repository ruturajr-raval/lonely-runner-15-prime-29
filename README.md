# Prime-29 Gate for Fifteen Lonely Runners

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22539841.svg)](https://doi.org/10.5281/zenodo.22539841)

## Project Overview

### Project Metadata

| Field | Value |
| --- | --- |
| Author | Ruturaj R Raval |
| Affiliation | Independent Researcher |
| ORCID | [0000-0003-4930-8981](https://orcid.org/0000-0003-4930-8981) |
| Field | Diophantine approximation, computational number theory, and SAT |
| Problem | Close finite-checking prime gates toward `LRC(14)` for fifteen total runners |
| Current result | Exact theorem `J(14,29) = empty` |
| Result type | Complete prime-29 finite-checking gate theorem |
| Release | `v0.1.1` |
| Version DOI | `10.5281/zenodo.22541517` |
| Concept DOI | `10.5281/zenodo.22539841` |
| License | MIT for project-original material |

### Problem And Context

The Lonely Runner Conjecture asks whether, for distinct nonzero integer
speeds, there exists one time at which every moving runner is simultaneously
at distance at least `1/(k+1)` from the origin after one runner is fixed. The
underlying problem dates to Wills's 1967 work and Cusick's 1973
view-obstruction formulation, so the general conjecture has remained open for
nearly six decades. The case of fifteen total runners is the next
finite-checking target after the published 2026 fourteen-runner work. A
complete proof through this framework requires closed prime gates whose
logarithmic mass exceeds `log B_14 = 810.0739811140556`; that full case
remains open.

### Work And Verified Outcome

At prime 29, the project proves that the unique level-one improper orbit is
represented by `(1,2,...,14)`. Every improper level-15 lift enters one of two
exhaustive symmetry branches. A factor-15 CRT reduction and independently
written C++ and Rust exact solvers reject all thirteen coprime cases. A
210-variable CNF and a checked DRAT proof reject the noncoprime branch.
Therefore `J(14,29) = empty`.

### Claim Boundary

The prime-29 gate is closed. The project does not prove the full
fifteen-runner conjecture, close another prime gate, reach the finite-checking
threshold, or claim completed external mathematical review. Release `v0.1.1`
corrects wording only; its theorem, proof, certificate, data, and
computational results are unchanged from `v0.1.0`.

### Verification And Reproduction

The selected certificate contains exact source snapshots, a Git bundle,
twenty-six coprime transcripts, the noncoprime CNF and DRAT proof, two
independent DRAT-checker logs, manifests, and mutation-tested replay tools.
Fast integrity checks and a complete local replay are available through the
commands documented below, with a separate hosted workflow as a public replay
record. Fast checks require Python 3 and ordinary workstation resources. The
recorded `v0.1.1` complete-certificate step took about 34 minutes on a standard
public `ubuntu-latest` runner with 4 vCPUs and 16 GB of RAM. This is a capacity
reference rather than a measured peak-memory requirement; local runtime scales
with hardware and the requested worker count.

### Significance, Limitations, And Future Work

Prime 29 contributes `log(29) = 3.367295829986474`, about 0.41568 percent of
the required threshold. The result supplies a complete reusable gate
certificate, but much more prime mass remains. The strongest next route is to
apply the factor-15 CRT method to additional primes and accumulate
independently checked closed-gate mass.

### Release, Citation, And Author

The public repository is
[`ruturajr-raval/lonely-runner-15-prime-29`](https://github.com/ruturajr-raval/lonely-runner-15-prime-29).
The immutable tagged release is
[`v0.1.1`](https://github.com/ruturajr-raval/lonely-runner-15-prime-29/releases/tag/v0.1.1)
at audited release commit
`bfc58364d975a862153307766386b51fe8289e57`.
It is archived at version DOI `10.5281/zenodo.22541517`; the stable
all-versions DOI is `10.5281/zenodo.22539841`. The Zenodo snapshot contains
110 files, all checked byte for byte against the release tag tree. GitHub and
Zenodo are the current dissemination baseline; no preprint-server deposit or
external mathematical review is claimed.

The next result gate is a second exact prime-gate theorem, or a theorem that
closes a stated family of gates, with source-bound evidence and independent
replay. Project-original material is MIT-licensed. The finite-checking
framework is attributed to the cited papers and independently implemented
here; external SAT and proof-checking tools retain their own licenses.
Citation metadata is in `CITATION.cff`, and release history is in
`RELEASE_NOTES.md`. The author is Ruturaj R Raval, Independent Researcher,
ORCID `0000-0003-4930-8981`.

This repository proves

```text
J(14,29) = empty.
```

Equivalently, it closes the prime-29 finite-checking gate for the Lonely
Runner Conjecture with fifteen total runners, after one runner is fixed to be
stationary.

The result is a rigorous component of the finite-checking program for the
next open case. It does not prove the full fifteen-runner conjecture.

Release `v0.1.1` corrects the scope wording in the overview and report
abstract without changing the theorem, proof, certificate, data, or
computational results. It is archived at version DOI
`10.5281/zenodo.22541517`. All archived versions are collected under the
stable concept DOI `10.5281/zenodo.22539841`.

## Origin And History

The underlying Diophantine approximation problem appeared in J. M. Wills's
1967 work and was independently formulated through T. W. Cusick's 1973
view-obstruction problem. The runner interpretation and the name "Lonely
Runner Conjecture" came later. The general problem has therefore remained
open for nearly six decades.

The modern finite-checking framework was developed by Sungkawichai and
Trakulthongchai for eleven, twelve, and thirteen total runners. Allikvere
subsequently reported a computer-assisted proof for fourteen total runners
with a public verification archive. This leaves fifteen total runners,
written `LRC(14)` after fixing one runner to be stationary, as the next full
finite-checking case. The dated frontier and novelty audit are recorded in
[`docs/PRIOR_ART.md`](docs/PRIOR_ART.md).

## Background

For a prime `p`, a level-one tuple belongs to the eventual-improper set
`J(k,p)` when every finite lifting level contains at least one improper lift,
where `k` is the number of moving runners. Proving `J(k,p) = empty` closes one
prime gate.

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

Every improper level-15 lift of this tuple is equivalent to a lift in one of
two exhaustive symmetry branches.

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
DRAT_TRIM_BIN="${DRAT_TRIM_BIN:-drat-trim}"
RATE_BIN="${RATE_BIN:-rate}"
python3 tools/verify_p29_certificate.py \
  --certificate-dir results/p29-level15-certificate-v1 \
  --drat-trim "$DRAT_TRIM_BIN" \
  --rate "$RATE_BIN"
```

Recompile the source snapshots stored inside the certificate and rerun all
twenty-six coprime searches:

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

## Evidence And Repository Map

| Path | Purpose and trust boundary |
| --- | --- |
| [`docs/P29_LEVEL15_THEOREM.md`](docs/P29_LEVEL15_THEOREM.md) | Complete mathematical reduction and prime-29 gate theorem |
| [`docs/MATHEMATICAL_SPEC.md`](docs/MATHEMATICAL_SPEC.md) | Exact definitions of properness, lifting, projection, symmetry, and certificate requirements |
| [`results/p29-level15-certificate-v1`](results/p29-level15-certificate-v1) | Selected source-bound certificate, transcripts, CNF, DRAT proof, checker logs, and manifests |
| [`docs/CERTIFICATE.md`](docs/CERTIFICATE.md) | Fast verification, proof replay, full source replay, and trust boundary |
| [`tools/verify_p29_certificate.py`](tools/verify_p29_certificate.py) | Standalone fail-closed certificate verifier |
| [`docs/CLAIMS.md`](docs/CLAIMS.md) | Human-readable claims, nonclaims, and quantitative significance |
| [`research/claim.yaml`](research/claim.yaml) | Machine-readable supported theorem and limitations |
| [`research/release-gate.json`](research/release-gate.json) | Publication-gate decisions for the scoped theorem |
| [`docs/PRIOR_ART.md`](docs/PRIOR_ART.md) | Dated frontier, novelty search, and implementation boundary |
| [`docs/RESEARCH_PLAN.md`](docs/RESEARCH_PLAN.md) | Ranked next routes and acceptance standard for further gates |
| [`paper/main.tex`](paper/main.tex) | Technical report source |
| [`PUBLICATION.md`](PUBLICATION.md) | Release result, correction scope, assets, archive, and nonclaims |
| [`.release-record.json`](.release-record.json) | Immutable release identity, asset hashes, and Zenodo archive record |

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

## Future Acceptance Gates

1. **Additional prime gate.** A further prime may be announced only after an
   exact gate theorem, complete source-bound artifacts, deterministic
   integrity checks, a compact checked proof or two independently implemented
   exhaustive replays, mutation tests, and a refreshed prior-art audit.
2. **Prime-family theorem.** A result closing a family of primes must state
   the exact arithmetic hypotheses, prove that every covered prime satisfies
   them, and provide independently checkable evidence for any finite
   computation used by the reduction.
3. **Full finite-checking gate.** A proof of `LRC(14)` may be claimed only
   after the independently verified closed-gate mass exceeds
   `log B_14 = 810.0739811140556`, or after a separate theorem replaces that
   threshold requirement.
4. **Rejected evidence.** Timeouts, unchecked SAT statuses, faster
   implementations, and larger but incomplete searches do not pass a
   mathematical result gate.

## Dissemination Status

Release `v0.1.1`, the technical report, source archive, complete selected
certificate, and checksum manifest are public through GitHub. Zenodo supplies
the immutable version archive and DOI. Version `v0.1.1` changes wording only
and supersedes `v0.1.0` for scope accuracy. No arXiv or HAL deposit is
currently part of the publication record, and no external peer review is
claimed. Any public summary must state both `J(14,29) = empty` and the
nonclaim that the full `LRC(14)` problem remains open.
The machine-readable files under `research/` are maintained-main
documentation added after the protected release; they summarize the released
claim but are not part of the immutable 110-file `v0.1.1` archive.

## License And Provenance

Project-original source, documentation, certificate assembly, and report
material are released under the MIT License. The finite-checking definitions
and earlier runner results are taken from the cited mathematical literature
with attribution; their implementation here is independent. No source code
from the cited unlicensed research repositories is copied.

Kissat generated the noncoprime proof, while DRAT-trim and `rate` checked it.
Those external tools are not project-original and remain under their
respective upstream terms. Their exact revisions are recorded in the
certificate provenance. The mathematical claim depends on the archived CNF,
DRAT proof, accepted checker logs, exact source snapshots, and replayable
certificate rather than on a hosted service or an unpublished binary.

## Primary References

- J. M. Wills, [Zwei Satze uber inhomogene diophantische Approximation von
  Irrationalzahlen](https://doi.org/10.1007/BF01298332),
  *Monatshefte fur Mathematik* 71 (1967), 263-269.
- T. W. Cusick, [View-obstruction problems](https://doi.org/10.1007/BF01832623),
  *Aequationes Mathematicae* 9 (1973), 165-170.
- T. Sungkawichai and T. Trakulthongchai,
  [Eleven, twelve, and thirteen lonely runners](https://arxiv.org/abs/2604.23906),
  arXiv:2604.23906v1, 2026.
- J. Allikvere,
  [Fourteen lonely runners](https://arxiv.org/abs/2609.02604),
  arXiv:2609.02604v1, 2026.
- J. Allikvere,
  [Verification archive for Fourteen lonely runners](https://zenodo.org/records/22066772),
  Zenodo, 2026.

## Citation

Citation metadata is in `CITATION.cff`. Cite release `v0.1.1` using version
DOI `10.5281/zenodo.22541517`. The stable all-versions DOI is
`10.5281/zenodo.22539841`. The technical report source is under `paper/`.

## Author

Ruturaj R Raval  
Independent Researcher  
ORCID: 0000-0003-4930-8981
