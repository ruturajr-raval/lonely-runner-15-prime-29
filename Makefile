LATEXMK ?= latexmk
SOURCE_DATE_EPOCH ?= 1788652800
TECTONIC ?= tectonic

.PHONY: certificate-bundle certificate-fast paper-build paper-bundle release-assets release-checksums release-metadata rust-verifier smoke terminal-solver test

test:
	python3 -m unittest discover -s tests -v

certificate-fast:
	python3 tools/verify_p29_certificate.py \
		--certificate-dir results/p29-level15-certificate-v1

certificate-bundle:
	python3 tools/build_certificate_bundle.py \
		--output dist/certificate/lonely-runner-15-prime-29-certificate-v1.tar.gz

paper-build:
	mkdir -p build/paper
	if command -v "$(TECTONIC)" >/dev/null 2>&1; then \
		SOURCE_DATE_EPOCH="$(SOURCE_DATE_EPOCH)" \
			"$(TECTONIC)" -X compile paper/main.tex \
			--outdir build/paper --keep-logs; \
	elif command -v "$(LATEXMK)" >/dev/null 2>&1; then \
		SOURCE_DATE_EPOCH="$(SOURCE_DATE_EPOCH)" \
			"$(LATEXMK)" -pdf -interaction=nonstopmode -halt-on-error \
			-file-line-error -output-directory=build/paper paper/main.tex; \
	else \
		echo "paper-build requires latexmk or tectonic" >&2; \
		exit 127; \
	fi

paper-bundle:
	python3 tools/build_paper_bundle.py \
		--output dist/paper/lonely-runner-15-prime-29-source.tar.gz

release-metadata:
	python3 tools/check_release_metadata.py \
		$(if $(VERSION_TAG),--tag "$(VERSION_TAG)",) \
		$(if $(REPOSITORY),--repository "$(REPOSITORY)",)

release-assets: test certificate-fast release-metadata paper-build paper-bundle certificate-bundle
	mkdir -p dist/release
	cp build/paper/main.pdf \
		dist/paper/lonely-runner-15-prime-29-paper.pdf
	cp dist/paper/lonely-runner-15-prime-29-paper.pdf \
		dist/paper/lonely-runner-15-prime-29-source.tar.gz \
		dist/certificate/lonely-runner-15-prime-29-certificate-v1.tar.gz \
		dist/release/
	cd dist/release && shasum -a 256 \
		lonely-runner-15-prime-29-paper.pdf \
		lonely-runner-15-prime-29-source.tar.gz \
		lonely-runner-15-prime-29-certificate-v1.tar.gz \
		> SHA256SUMS

release-checksums:
	test -s dist/release/SHA256SUMS
	cd dist/release && shasum -a 256 -c SHA256SUMS

smoke:
	python3 tools/run_gate.py --k 2 --prime 5 --pipeline 3

terminal-solver:
	mkdir -p build
	c++ -std=c++17 -O3 -DNDEBUG -Wall -Wextra -pedantic \
		tools/solve_p29_level15.cpp -o build/solve_p29_level15

rust-verifier:
	mkdir -p build
	RUSTC_VERSION="$$(rustc --version)" \
		rustc --edition 2024 -O -C overflow-checks=yes -D warnings \
		tools/verify_p29_level15.rs -o build/verify_p29_level15
