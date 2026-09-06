.PHONY: rust-verifier smoke terminal-solver test

test:
	python3 -m unittest discover -s tests -v

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
