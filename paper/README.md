# Technical Report

The manuscript is `main.tex`.

Build the PDF from the repository root:

```bash
make paper-build
```

Build the deterministic source archive:

```bash
make paper-bundle
```

The outputs are:

```text
build/paper/main.pdf
dist/paper/lonely-runner-15-prime-29-source.tar.gz
```

`make release-assets` also writes the release-named PDF:

```text
dist/paper/lonely-runner-15-prime-29-paper.pdf
```

The complete paper-inclusive release set is written under `dist/release/`.
Verify it with:

```bash
make release-checksums
make release-verify
```

Release `v0.1.2` adds the explicitly named PDF and deterministic source
archive to the archival package. The theorem, proof, certificate, data, and
computations are unchanged from `v0.1.1`.

Replay the selected certificate with:

```bash
make certificate-fast
```

`ARXIV_METADATA.md` records optional preprint metadata. `RIGHTS.md` records
authorship and licensing boundaries.
