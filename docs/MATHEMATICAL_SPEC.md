# Mathematical Specification

Fix `k >= 2`, let `q = k + 1`, and let `p` be prime. At level `l`, set
`m = l p` and consider tuples whose coordinates are nonzero modulo `p`.

## Properness

A tuple `v = (v_1, ..., v_k)` at level `l` is proper if either:

1. for some coordinate index `i`,
   `gcd(l, v_1, ..., v_(i-1), v_(i+1), ..., v_k) > 1`; or
2. some integer time class `t modulo m` satisfies
   `q dist_m(t v_i) >= m` for every `i`, where
   `dist_m(x) = min(x mod m, -x mod m)`.

Otherwise the tuple is improper. The set of improper tuples is `I(k,p,l)`.

## Eventual improperness

A level-one tuple is eventually proper if some level excludes every lift of
that tuple from the corresponding improper family. The set of tuples that
are not eventually proper is `J(k,p)`.

To certify `J(k,p) = empty`, the implementation maintains a finite set `S`
whose projection contains `J(k,p)` and repeatedly applies exact operations:

- **Lift by `c`:** enumerate every coordinate-wise preimage modulo `c l p`
  and retain exactly the improper lifts.
- **Project:** reduce retained rows modulo `p`.

Both operations preserve the invariant that the projected set contains
`J(k,p)`. Reaching an empty set closes the prime gate.

## Symmetries

Eventual properness is preserved by:

- coordinate permutation;
- independent coordinate sign changes; and
- multiplication by a unit modulo `p`.

At level one, one representative of each orbit is the lexicographically
least sorted folded tuple under multiplication by all nonzero residues.

## Level-one cover formulation

At level one, define the bad-time mask of speed class `v` by

`B_v = {t : q dist_p(t v) < p}`.

A tuple is improper exactly when the union of its selected bad-time masks
covers every nonzero time class up to sign. Multiplicity does not change the
union but remains part of the tuple because it affects later lifts.

## Certificate requirements

A gate certificate must record:

- the exact parameters and pipeline;
- level-by-level row counts;
- a canonical sorted encoding of every retained row, or hashes of
  independently regenerable shards;
- deterministic SHA-256 digests;
- the final empty-set check; and
- an independent replay using separately written code.

