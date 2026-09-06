from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import package_p29_certificate


CERTIFICATE = ROOT / "results" / "p29-level15-certificate-v1"
PACKAGER = ROOT / "tools" / "package_p29_certificate.py"
VERIFIER = ROOT / "tools" / "verify_p29_certificate.py"


class PackageSourceBundleTests(unittest.TestCase):
    def test_complete_packaging_uses_sealed_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "certificate"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(PACKAGER),
                    "--cpp-summary",
                    str(CERTIFICATE / "coprime" / "cpp" / "summary.json"),
                    "--rust-summary",
                    str(CERTIFICATE / "coprime" / "rust" / "summary.json"),
                    "--noncoprime-summary",
                    str(CERTIFICATE / "noncoprime" / "summary.json"),
                    "--output-dir",
                    str(output),
                ],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            verified = subprocess.run(
                [
                    sys.executable,
                    str(VERIFIER),
                    "--certificate-dir",
                    str(output),
                ],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            self.assertEqual(verified.returncode, 0, verified.stderr)
            self.assertIn(
                "source-bound integrity and mathematical reconstruction "
                "PASSED",
                verified.stdout,
            )

    def test_tracked_bundle_is_reused_without_commit_object(self) -> None:
        manifest = json.loads(
            (CERTIFICATE / "certificate.json").read_text(encoding="ascii")
        )
        source_commit = str(manifest["source_commit"])
        with tempfile.TemporaryDirectory() as directory:
            output_root = Path(directory) / "certificate"
            with mock.patch.object(
                package_p29_certificate,
                "git_has_commit",
                return_value=False,
            ):
                output = package_p29_certificate.create_source_bundle(
                    output_root,
                    source_commit,
                )
            self.assertEqual(
                output.read_bytes(),
                package_p29_certificate.SELECTED_SOURCE_BUNDLE.read_bytes(),
            )


if __name__ == "__main__":
    unittest.main()
