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

Replay the selected certificate with:

```bash
make certificate-fast
```

`ARXIV_METADATA.md` records optional preprint metadata. `RIGHTS.md` records
authorship and licensing boundaries.
