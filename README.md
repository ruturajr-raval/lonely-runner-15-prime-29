# Prime-29 Gate for Fifteen Lonely Runners

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22539841.svg)](https://doi.org/10.5281/zenodo.22539841)

## Project Overview

| Field | Value |
| --- | --- |
| Author | Ruturaj R Raval |
| Affiliation | Independent Researcher |
| ORCID | [0000-0003-4930-8981](https://orcid.org/0000-0003-4930-8981) |
| Field | Diophantine approximation, computational number theory, and SAT |
| Problem | Close finite-checking prime gates toward `LRC(14)` for fifteen total runners |
| Current result | Exact theorem `J(14,29) = empty` |
| Result type | Complete prime-29 finite-checking gate theorem |
| Release | `v0.1.2` |
| Version DOI | [10.5281/zenodo.22647790](https://doi.org/10.5281/zenodo.22647790) |
| Concept DOI | [10.5281/zenodo.22539841](https://doi.org/10.5281/zenodo.22539841) |
| License | MIT for project-original material |

This repository proves

```text
J(14,29) = empty.
```

Equivalently, it closes the prime-29 finite-checking gate for the Lonely
Runner Conjecture with fifteen total runners after one runner is fixed to be
stationary. The result is a rigorous component of the finite-checking program
for the next open case. It does not prove the full fifteen-runner conjecture.

## Problem And Background

The Lonely Runner Conjecture asks whether, for distinct nonzero integer
speeds, there exists a time at which every moving runner is simultaneously at
distance at least `1/(k+1)` from the origin after one runner is fixed.

For a prime `p`, a level-one tuple belongs to the eventual-improper set
`J(k,p)` when every finite lifting level contains at least one improper lift,
where `k` is the number of moving runners. Proving `J(k,p) = empty` closes one
prime gate in the modern finite-checking framework.

For fifteen total runners, fixing one runner as stationary leaves `k = 14`
moving runners. A complete finite-checking proof requires enough closed prime
gates that their logarithmic mass exceeds

```text
log B_14 = 810.0739811140556.
```

## Starting Frontier And Longstanding Gap

The underlying Diophantine approximation problem appeared in J. M. Wills's
1967 work and was independently formulated through T. W. Cusick's 1973
view-obstruction problem. The runner interpretation and the name "Lonely
Runner Conjecture" came later. The general problem has remained open for
nearly six decades.

Sungkawichai and Trakulthongchai developed the modern finite-checking
framework for eleven, twelve, and thirteen total runners. Allikvere
subsequently reported a computer-assisted proof for fourteen total runners
with a public verification archive. This leaves fifteen total runners,
written `LRC(14)` after fixing one runner to be stationary, as the next full
finite-checking case.

At the start of this project, the prime-29 gate for `k = 14` had not been
closed in the audited public literature. The dated frontier and novelty audit
are recorded in [`docs/PRIOR_ART.md`](docs/PRIOR_ART.md).

## Main Result

At level one modulo 29, every folded speed class is bad at exactly one folded
time class. An improper 14-tuple must therefore contain every folded class
once. Up to permutation and signs, the unique level-one improper tuple is

```text
(1, 2, 3, ..., 14).
```

Every improper level-15 lift of this tuple is equivalent to a lift in one of
two exhaustive symmetry branches:

- In the coprime branch, a factor-15 CRT reduction forces one of coordinates
  2 through 14 to have residue zero modulo 15. Two separately written exact
  solvers, one in C++ and one in Rust, reject all thirteen coordinate-zero
  cases.
- In the noncoprime branch, a 210-variable, 1,842-clause CNF is
  unsatisfiable. Kissat produced a 368,542-byte DRAT proof accepted
  independently by DRAT-trim and `rate`.

The two branches contain no improper level-15 lift. The unique level-one
orbit is therefore eventually proper, proving

```text
J(14,29) = empty.
```

The project-original theorem is this prime-29 gate closure and its checked
level-15 reduction. The finite-checking framework and earlier closed gates
are prior work and are used only as the surrounding program.

The complete reduction and theorem are in
[`docs/P29_LEVEL15_THEOREM.md`](docs/P29_LEVEL15_THEOREM.md).

## Method And Proof Architecture

The proof separates the finite mathematical reduction from independent
computational checks:

- Folded speed and time classes identify the unique level-one improper orbit.
- Permutation and sign symmetries reduce all level-15 lifts to two exhaustive
  branches.
- A factor-15 Chinese remainder theorem reduction converts the coprime branch
  into thirteen exact coordinate-zero cases.
- Independent C++ and Rust implementations exhaust all thirteen cases.
- A deterministic generator produces the noncoprime 210-variable,
  1,842-clause CNF.
- Kissat supplies a DRAT proof, and two independent proof checkers validate
  it.
- A source-bound certificate links source snapshots, transcripts, CNF,
  proof, checker logs, and manifests to the declared source commit.

The mathematical claim depends on the archived finite reduction and checked
certificate. It does not depend on an unchecked SAT status, a hosted service,
or an unpublished binary.

## Verification And Evidence

The selected certificate is
[`results/p29-level15-certificate-v1`](results/p29-level15-certificate-v1).
Its top-level manifest binds every included artifact by SHA-256 and records
the source commit used for all original runs.

The certificate contains:

- exact source snapshots for both coprime solvers;
- a Git object bundle binding those snapshots to the declared source commit;
- thirteen C++ and thirteen Rust UNSAT transcripts;
- the exact noncoprime CNF and DRAT proof;
- logs from DRAT-trim and `rate`;
- source snapshots for the noncoprime generator;
- manifests and a standalone verifier with fail-closed mutation tests.

Fast integrity checks and a complete local replay are available, with a
separate hosted workflow serving as a public replay record. Fast checks
require Python 3 and ordinary workstation resources. Independent C++ and
Rust implementations reject all thirteen coprime cases, while DRAT-trim and
`rate` independently check the noncoprime proof.

The recorded `v0.1.1` complete-certificate step took about 34 minutes on a
standard public `ubuntu-latest` runner with 4 vCPUs and 16 GB of RAM. This is
a capacity reference rather than a measured peak-memory requirement. Local
runtime scales with hardware and the requested worker count.

The trust boundary and replay procedure are documented in
[`docs/CERTIFICATE.md`](docs/CERTIFICATE.md).

## Reproduction

Run the test suite and fast certificate verifier:

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

Fast mode verifies integrity, exact claims, level-one generation, CRT
identities, all logs, and the reconstructed noncoprime CNF. It does not
replace DRAT replay or the long coprime reruns.

Fast verification is CPU-bound, uses no GPU, and fits an ordinary
workstation. The complete replay is substantially longer: the recorded
hosted run used 4 vCPUs and 16 GB of RAM and completed its certificate stage
in about 34 minutes.

GitHub release downloads include `SHA256SUMS`. Place the PDF, source archive,
certificate archive, and checksum file in one directory, then run:

```bash
shasum -a 256 -c SHA256SUMS
```

## Claims

This project claims:

- the unique level-one improper orbit for `k = 14`, `p = 29`;
- the exhaustive coprime and noncoprime symmetry split at level 15;
- exact exclusion of all thirteen coprime coordinate-zero cases by both
  independent implementations;
- a checked DRAT exclusion of the noncoprime branch;
- the theorem `J(14,29) = empty`.

The complete human-readable claim boundary is maintained in
[`docs/CLAIMS.md`](docs/CLAIMS.md), with machine-readable claims in
[`research/claim.yaml`](research/claim.yaml).

## Limitations And Nonclaims

This project does not claim:

- a proof of the full fifteen-runner conjecture or `LRC(14)`;
- closure of any prime gate other than 29;
- that the current gate mass reaches the finite-checking threshold;
- completed external mathematical review;
- priority over unpublished or unindexed work.

Release `v0.1.1` corrects scope wording in the overview and report abstract.
Its theorem, proof, certificate, data, and computational results are
unchanged from `v0.1.0`.

Release `v0.1.2` is an archival and documentation patch. It adds an
explicitly named compiled PDF, a deterministic report-source archive, and a
checksum manifest. The theorem, proof, certificate, data, computations, and
claim boundary are unchanged from `v0.1.1`.

No arXiv or HAL deposit is currently part of the publication record. Any
public summary must state both `J(14,29) = empty` and the nonclaim that the
full `LRC(14)` problem remains open.

## Significance And Use

Prime 29 contributes

```text
log(29) = 3.367295829986474,
```

which is about 0.41568 percent of the required finite-checking threshold.
This is a complete, reusable, independently checkable prime-gate theorem for
the next full runner case.

The repository can be used to:

- reproduce the prime-29 finite reduction and exact gate theorem;
- replay both independent coprime implementations;
- regenerate and verify the noncoprime CNF and DRAT proof;
- test certificate integrity and provenance mutations;
- reuse the factor-15 CRT method for additional prime gates;
- accumulate independently checked closed-gate mass toward `LRC(14)`.

## Remaining Work And Future Directions

The strongest next route is to apply the factor-15 CRT method to additional
primes and accumulate enough independently checked closed-gate mass to exceed
`log B_14 = 810.0739811140556`. A theorem closing a family of prime gates
could accelerate that program.

Future results must pass these acceptance gates:

1. **Additional prime gate.** A further prime may be announced only after an
   exact gate theorem, complete source-bound artifacts, deterministic
   integrity checks, a compact checked proof or two independently implemented
   exhaustive replays, mutation tests, and a refreshed prior-art audit.
2. **Prime-family theorem.** A result closing a family of primes must state
   the exact arithmetic hypotheses, prove that every covered prime satisfies
   them, and provide independently checkable evidence for every finite
   computation used by the reduction.
3. **Full finite-checking gate.** A proof of `LRC(14)` may be claimed only
   after the independently verified closed-gate mass exceeds
   `log B_14 = 810.0739811140556`, or after a separate theorem replaces that
   threshold requirement.
4. **Rejected evidence.** Timeouts, unchecked SAT statuses, faster
   implementations, and larger but incomplete searches do not pass a
   mathematical result gate.

Ranked next routes and acceptance standards are maintained in
[`docs/RESEARCH_PLAN.md`](docs/RESEARCH_PLAN.md).

## Repository Layout

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
| [`.release-record.json`](.release-record.json) | Current release identity, local asset hashes, prior release history, and publication state |

## Publication Citation And Archive

The public repository is
[`ruturajr-raval/lonely-runner-15-prime-29`](https://github.com/ruturajr-raval/lonely-runner-15-prime-29).
The paper-inclusive archival patch is identified as
[`v0.1.2`](https://github.com/ruturajr-raval/lonely-runner-15-prime-29/releases/tag/v0.1.2).
Its release set contains the compiled report PDF, deterministic report-source
archive, a regenerated archive of the unchanged selected certificate, and
`SHA256SUMS`. The
[technical report source](paper/main.tex) is maintained in the repository.

Release `v0.1.2` uses version DOI
[10.5281/zenodo.22647790](https://doi.org/10.5281/zenodo.22647790), while
[10.5281/zenodo.22539841](https://doi.org/10.5281/zenodo.22539841) is the
stable concept DOI for all versions.

The audited release commit is
`d968c40b55c885b66aca73861553cf5ffdd43bd3`. GitHub release `384395612`
and the Zenodo record were downloaded after publication and checked against
the four local release assets. Zenodo's generated four-file aggregate archive
has SHA-256
`292c64ce55fb8c432c862c621d992c7b203dc5eecb27df84cc541c3555e117e5`.

The prior `v0.1.1` archive remains the historical scope-correction release.
Version `v0.1.2` changes archival packaging and documentation only.

GitHub and Zenodo are the current dissemination baseline. No preprint-server
deposit or external peer review is claimed. The post-publication revisions to
the machine-readable files under `research/` summarize the released claim but
are not part of the immutable `v0.1.2` tag.

Citation metadata is in [`CITATION.cff`](CITATION.cff), release history is in
[`RELEASE_NOTES.md`](RELEASE_NOTES.md), and the complete release record is in
[`PUBLICATION.md`](PUBLICATION.md). Cite the paper-inclusive `v0.1.2`
archival patch using version DOI `10.5281/zenodo.22647790`.

## Authorship

Ruturaj R Raval, Independent Researcher

ORCID: [0000-0003-4930-8981](https://orcid.org/0000-0003-4930-8981)

## Licensing And Provenance

Project-original source, documentation, certificate assembly, and report
material are released under the MIT License. The finite-checking definitions
and earlier runner results are taken from the cited mathematical literature
with attribution and independently implemented here. No source code from the
cited unlicensed research repositories is copied.

Kissat generated the noncoprime proof, while DRAT-trim and `rate` checked it.
These external tools are not project-original and remain under their
respective upstream terms. Their exact revisions are recorded in the
certificate provenance.

The mathematical claim depends on the archived CNF, DRAT proof, accepted
checker logs, exact source snapshots, and replayable certificate rather than
on a hosted service or an unpublished binary.

## References

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
