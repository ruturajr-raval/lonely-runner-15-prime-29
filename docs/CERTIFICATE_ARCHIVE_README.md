# Prime-29 Gate Certificate

This archive is a standalone fast verifier for the selected certificate
proving `J(14,29) = empty`.

Fast verification requires Python 3.9 or later and Git.

From the archive root, run:

```bash
python3 tools/verify_p29_certificate.py \
  --certificate-dir results/p29-level15-certificate-v1
```

The fast command checks the complete artifact manifest, the bundled Git
source commit, all packaged source bindings and transcripts, the level-one
orbit, CRT identities, and the reconstructed noncoprime CNF.

It does not execute the long coprime searches or replay the DRAT proof.
For complete replay, provide DRAT-trim and `rate`, a C++17 compiler, and a
Rust compiler:

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

The archive includes the repository MIT License. The mathematical claim,
limits, and detailed replay instructions are in the accompanying repository
and technical report.
