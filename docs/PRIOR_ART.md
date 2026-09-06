# Prior Art And Frontier Audit

Status date: 2026-09-06

## Historical Origin

The number-theoretic form of the problem appears in J. M. Wills,
"Zwei Satze uber inhomogene diophantische Approximation von
Irrationalzahlen", *Monatshefte fur Mathematik* 71 (1967), 263-269,
DOI `10.1007/BF01298332`.

T. W. Cusick formulated the related view-obstruction problem in
"View-obstruction problems", *Aequationes Mathematicae* 9 (1973), 165-170,
DOI `10.1007/BF01832623`. The runner interpretation and the name "Lonely
Runner Conjecture" came later.

## Finite-Checking Framework

Touch Sungkawichai and Tanupat Trakulthongchai, "Eleven, twelve, and
thirteen lonely runners", arXiv:2604.23906v1, develop improper families,
eventual-improper sets `J(k,p)`, modular lifts, backward projection, and
unit-orbit reduction. Their results establish the conjecture through
thirteen total runners.

Jaan Allikvere, "Fourteen lonely runners", arXiv:2609.02604v1, reports a
computer-assisted proof for fourteen total runners. Its verification archive
is available at DOI `10.5281/zenodo.22066772`.

These works leave fifteen total runners, denoted `LRC(14)` after fixing one
runner to be stationary, as the next full finite-checking case.

Primary sources:

- https://doi.org/10.1007/BF01298332
- https://doi.org/10.1007/BF01832623
- https://arxiv.org/abs/2604.23906
- https://arxiv.org/abs/2609.02604
- https://doi.org/10.5281/zenodo.22066772

## Other Fifteen-Runner Work

The public repository
`Komeiji-Shiki/fifteen-lonely-runners-congruence`, first located during the
2026-09-06 audit, states a theorem for a restricted arithmetic-progression
residue family. It explicitly does not reduce arbitrary fifteen-runner
instances to that family and does not prove the general conjecture.

Repository:

- https://github.com/Komeiji-Shiki/fifteen-lonely-runners-congruence

## Dated Novelty Search

Searches on 2026-09-06 covered:

- arXiv title and abstract results for lonely-runner work;
- GitHub repository and code search for `J(14,29)` and close variants;
- exact web search for `J(14,29)`;
- Zenodo records for the same gate statement.

No indexed public closure of `J(14,29)` was located in that search.

This is a dated public-source finding. It is not proof that unpublished,
privately circulated, newly posted, or unindexed work does not exist.

## Implementation Boundary

The implementation is independent and follows the published mathematical
definitions. No source code from an unlicensed repository is copied. Public
aggregate statements and prior results are used only with attribution.
