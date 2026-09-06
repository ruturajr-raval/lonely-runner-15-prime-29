from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ShardToolTests(unittest.TestCase):
    def setUp(self) -> None:
        build = ROOT / "build"
        build.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(
            prefix="shard-tools-",
            dir=build,
        )
        self.root = Path(self.temporary.name)
        self.corpus = self.root / "corpus"
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "build_p29_shards.py"),
                "--coordinates",
                "2",
                "--output-dir",
                str(self.corpus),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def runner_command(
        self,
        solver: Path,
        drat_trim: Path,
        rate: Path,
        suffix: str,
    ) -> list[str]:
        return [
            sys.executable,
            str(ROOT / "tools" / "run_cnf_shards.py"),
            "--solver",
            str(solver),
            "--drat-trim",
            str(drat_trim),
            "--rate",
            str(rate),
            "--input-dir",
            str(self.corpus),
            "--log-dir",
            str(self.root / f"logs-{suffix}"),
            "--proof-dir",
            str(self.root / f"proofs-{suffix}"),
            "--checker-log-dir",
            str(self.root / f"checker-logs-{suffix}"),
            "--summary",
            str(self.root / f"summary-{suffix}.json"),
            "--jobs",
            "4",
        ]

    def make_executable(self, name: str, body: str) -> Path:
        path = self.root / name
        path.write_text(body, encoding="ascii")
        path.chmod(path.stat().st_mode | 0o111)
        return path

    def test_builder_writes_canonical_complete_manifest(self) -> None:
        manifest = json.loads(
            (self.corpus / "manifest.json").read_text(encoding="ascii")
        )
        self.assertEqual(manifest["expected_shards"], 15)
        self.assertEqual(
            [entry["file"] for entry in manifest["shards"]],
            [f"c02a{choice:02d}.cnf" for choice in range(15)],
        )

    def test_runner_rejects_self_consistent_incomplete_manifest(self) -> None:
        manifest_path = self.corpus / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="ascii"))
        manifest["expected_shards"] = 14
        manifest["shards"] = manifest["shards"][:14]
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="ascii",
        )
        completed = subprocess.run(
            self.runner_command(
                Path("/usr/bin/true"),
                Path("/usr/bin/true"),
                Path("/usr/bin/true"),
                "incomplete",
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("invalid expected count", completed.stderr)

    def test_runner_rejects_manifest_path_escape(self) -> None:
        manifest_path = self.corpus / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="ascii"))
        manifest["shards"][0]["file"] = "../outside.cnf"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="ascii",
        )
        completed = subprocess.run(
            self.runner_command(
                Path("/usr/bin/true"),
                Path("/usr/bin/true"),
                Path("/usr/bin/true"),
                "escape",
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("manifest entry is incomplete", completed.stderr)

    def test_runner_requires_exact_verified_line(self) -> None:
        solver = self.make_executable(
            "solver",
            "#!/bin/sh\n"
            "if [ \"$1\" = \"--version\" ]; then\n"
            "  echo fake-solver-1\n"
            "  exit 0\n"
            "fi\n"
            "printf proof > \"$2\"\n"
            "echo 's UNSATISFIABLE'\n"
            "exit 20\n",
        )
        good_checker = self.make_executable(
            "good-checker",
            "#!/bin/sh\n"
            "echo 's VERIFIED'\n"
            "exit 0\n",
        )
        bad_checker = self.make_executable(
            "bad-checker",
            "#!/bin/sh\n"
            "echo 'prefix s VERIFIED suffix'\n"
            "exit 0\n",
        )
        completed = subprocess.run(
            self.runner_command(
                solver,
                good_checker,
                bad_checker,
                "exact-line",
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            env={**os.environ, "LC_ALL": "C"},
        )
        self.assertEqual(completed.returncode, 1)
        summary = json.loads(
            (self.root / "summary-exact-line.json").read_text(
                encoding="ascii"
            )
        )
        self.assertEqual(
            {shard["status"] for shard in summary["shards"]},
            {"UNVERIFIED_UNSAT"},
        )

    def test_runner_records_complete_verified_corpus(self) -> None:
        solver = self.make_executable(
            "solver",
            "#!/bin/sh\n"
            "if [ \"$1\" = \"--version\" ]; then\n"
            "  echo fake-solver-1\n"
            "  exit 0\n"
            "fi\n"
            "printf proof > \"$2\"\n"
            "echo 's UNSATISFIABLE'\n"
            "exit 20\n",
        )
        checker = self.make_executable(
            "checker",
            "#!/bin/sh\n"
            "echo 's VERIFIED'\n"
            "exit 0\n",
        )
        completed = subprocess.run(
            self.runner_command(
                solver,
                checker,
                checker,
                "verified",
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            env={**os.environ, "LC_ALL": "C"},
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        summary = json.loads(
            (self.root / "summary-verified.json").read_text(
                encoding="ascii"
            )
        )
        self.assertTrue(summary["tools_unchanged_during_run"])
        self.assertEqual(len(summary["shards"]), 15)
        self.assertEqual(
            {shard["status"] for shard in summary["shards"]},
            {"VERIFIED_UNSAT"},
        )


if __name__ == "__main__":
    unittest.main()
