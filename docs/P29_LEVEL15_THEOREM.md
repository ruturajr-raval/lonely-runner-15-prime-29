# The Level-15 Closure of the Prime-29 Gate

Status date: 2026-09-06

## Theorem

For `k = 14` and `p = 29`, the eventual-improper set is empty:

`J(14,29) = empty`.

Equivalently, the prime-29 finite-checking gate for fifteen total runners is
closed.

This is one component of the finite-checking program for `LRC(14)`. It is not
a proof of the Lonely Runner Conjecture for fifteen runners.

## Level-one reduction

At level one, both speeds and nonzero times have 14 folded classes modulo
29. For nonzero `t` and `v`, the badness condition is

`15 dist_29(t v) < 29`.

Since `t v` is nonzero modulo 29, this holds exactly when
`t v = plus or minus 1 mod 29`. Thus every folded speed class is bad at
exactly one folded time class.

An improper 14-tuple must cover all 14 folded time classes with its 14
coordinates. It must therefore use every folded speed class exactly once.
Up to permutation and signs, the unique level-one improper tuple is

`(1, 2, 3, ..., 14)`.

The exact level-one generator independently reproduces this conclusion by
enumerating every bad-time covering support, expanding every multiplicity
pattern of total size 14, and quotienting by permutation, independent signs,
and multiplication by units modulo 29. Its complete output is the same
single orbit represented by

`(1, 2, 3, ..., 14)`.

It is therefore enough to show that every level-15 lift of this representative
is proper.

Write a labeled lift as

`v_i = i + 29 a_i`, for `1 <= i <= 14` and `0 <= a_i < 15`,

and define its residue

`c_i = v_i mod 15 = i - a_i mod 15`.

The map from `a_i` to `c_i` is a bijection for each coordinate.

## Symmetry split

Every possible improper lift belongs to one of two cases.

### A coordinate is coprime to 15

Such a coordinate is also coprime to 29, hence it is a unit modulo 435.
Multiplication by its inverse, followed by signs and coordinate permutation,
normalizes that coordinate to the value 1. The full-residue parent is
preserved as an orbit, so the normalized lift has

`v_1 = 1`, and therefore `c_1 = 1`.

This is the coprime branch.

### No coordinate is coprime to 15

Multiplication by a unit preserves each coordinate's gcd with 15. If a lift
in this branch were improper, it would have to fail the gcd properness
clause. In particular, at least two coordinates would be nondivisible by 3
and at least two would be nondivisible by 5.

Since every coordinate is noncoprime to 15, a coordinate that is
nondivisible by 5 has gcd exactly 3 with 15. Such a coordinate can be
normalized to the value 3 by multiplication with a unit modulo 435, followed
by signs and permutation. The normalized lift has

`v_3 = 3`,

and every coordinate remains noncoprime to 15.

This is the noncoprime branch.

The two branches exhaust all lifts that could be improper.

## CRT reduction in the coprime branch

For a folded time `1 <= t <= 217`, set

`x = t mod 29`, `y = t mod 15`, and `r = x i mod 29` in `{0,...,28}`.

The coordinate `i` is bad at time `t` exactly under the following conditions:

- if `r = 0`, then `y c_i = 0 mod 15`;
- if `r != 0`, then `y c_i` equals `r` or `r + 1` modulo 15.

This follows by listing the residues modulo 435 whose distance from zero is
strictly less than 29. For nonzero `r`, the two representatives are `r` and
`r - 29`, whose residues modulo 15 are `r` and `r + 1`.

Three consequences reduce the search:

1. At `t = 29`, a coordinate is bad exactly when `c_i = 0`. Every time cover
   therefore has at least one zero residue.
2. Every folded multiple of 15 is covered automatically. For each such time,
   exactly one of the parent residue classes `1,...,14` is bad for every
   value of its `c_i`.
3. Once some `c_i = 0`, that coordinate covers every folded multiple of 29.

After removing those automatic classes, 196 nontrivial time classes remain.
The normalization `c_1 = 1` means that the mandatory zero must occur in one
of coordinates 2 through 14.

The coprime branch is therefore covered by thirteen exhaustive, overlapping
cases:

`c_j = 0`, for `j = 2,...,14`.

Two separately written exact solvers establish that every one of these cases
is unsatisfiable:

- a C++ solver using direct arithmetic modulo 435 and coordinate-group
  branching;
- a Rust verifier using the CRT predicate and individual clause-literal
  branching.

Both implementations check every folded time class. The search omits the gcd
constraints, so its conclusion is stronger than required: no normalized lift
in the coprime branch even forms a time cover.

## Certified noncoprime branch

The noncoprime branch is encoded as a 210-variable CNF. It contains:

- exactly-one constraints for the 15 choices of each labeled coordinate;
- one bad-coordinate clause for every folded time class;
- the exact failure conditions for the factor-3 and factor-5 gcd properness
  clauses;
- unit clauses excluding every choice coprime to 15; and
- the symmetry anchor `v_3 = 3`.

Kissat reports the formula unsatisfiable and emits a DRAT proof. The proof is
independently accepted by both DRAT-trim and `rate`. The release certificate
records exact hashes for the formula, proof, checker logs, and tools used in
the original run.

## Conclusion

The coprime and noncoprime branches contain no improper level-15 lift of the
unique level-one orbit. Thus that orbit is eventually proper. Since every
level-one improper tuple belongs to the orbit,

`J(14,29) = empty`.

## Significance and limits

Closing this gate contributes

`log(29) = 3.367295829986474`

to the finite-checking prime mass. This is about 0.41568 percent of the
current target `log B_14 = 810.0739811140556`.

The result supplies a certified closure of the prime-29 gate, a reusable
factor-15 CRT reduction, and two independent exact implementations. It does
not close any other prime gate, establish a general family of gates, or prove
`LRC(14)`.
