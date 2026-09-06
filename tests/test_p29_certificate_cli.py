from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CERTIFICATE = ROOT / "results" / "p29-level15-certificate-v1"
VERIFIER = ROOT / "tools" / "verify_p29_certificate.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class P29CertificateCliTests(unittest.TestCase):
    def copy_certificate(self, root: Path) -> Path:
        destination = root / "certificate"
        shutil.copytree(CERTIFICATE, destination)
        return destination

    def run_verifier(self, certificate: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(VERIFIER),
                "--certificate-dir",
                str(certificate),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

    def write_json(self, path: Path, value: object) -> None:
        path.write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n",
            encoding="ascii",
        )

    def refresh_artifact(self, certificate: Path, relative: str) -> None:
        manifest_path = certificate / "certificate.json"
        manifest = json.loads(manifest_path.read_text(encoding="ascii"))
        artifact = certificate / relative
        manifest["artifacts"][relative] = {
            "bytes": artifact.stat().st_size,
            "sha256": sha256(artifact),
        }
        self.write_json(manifest_path, manifest)

    def assert_rejected_cleanly(
        self,
        completed: subprocess.CompletedProcess[str],
        expected: str,
    ) -> None:
        self.assertEqual(completed.returncode, 1)
        self.assertIn("verification failed:", completed.stderr)
        self.assertIn(expected, completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)

    def test_selected_certificate_passes_fast_verification(self) -> None:
        completed = self.run_verifier(CERTIFICATE)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "source-bound integrity and mathematical reconstruction PASSED",
            completed.stdout,
        )

    def test_rejects_changed_theorem_field(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            certificate = self.copy_certificate(Path(directory))
            manifest_path = certificate / "certificate.json"
            manifest = json.loads(manifest_path.read_text(encoding="ascii"))
            manifest["theorem"] = "different theorem"
            self.write_json(manifest_path, manifest)
            completed = self.run_verifier(certificate)
        self.assert_rejected_cleanly(
            completed,
            "certificate theorem field mismatch",
        )

    def test_rejects_unlisted_nested_certificate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            certificate = self.copy_certificate(Path(directory))
            nested = certificate / "coprime" / "cpp" / "certificate.json"
            nested.write_text("{}\n", encoding="ascii")
            completed = self.run_verifier(certificate)
        self.assert_rejected_cleanly(
            completed,
            "artifact manifest does not match the directory",
        )

    def test_rejects_source_tamper_even_after_manifest_refresh(self) -> None:
        relative = "coprime/cpp/provenance/solve_p29_level15.cpp"
        with tempfile.TemporaryDirectory() as directory:
            certificate = self.copy_certificate(Path(directory))
            source = certificate / relative
            source.write_text(
                source.read_text(encoding="ascii") + "\n",
                encoding="ascii",
            )
            self.refresh_artifact(certificate, relative)
            completed = self.run_verifier(certificate)
        self.assert_rejected_cleanly(
            completed,
            "packaged source does not match the declared commit",
        )

    def test_rejects_coordinated_source_commit_substitution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            certificate = self.copy_certificate(Path(directory))
            manifest_path = certificate / "certificate.json"
            manifest = json.loads(manifest_path.read_text(encoding="ascii"))
            manifest["source_commit"] = "2" * 40
            self.write_json(manifest_path, manifest)
            completed = self.run_verifier(certificate)
        self.assert_rejected_cleanly(
            completed,
            "source bundle head does not match the declared commit",
        )

    def test_rejects_source_bundle_tamper_after_manifest_refresh(self) -> None:
        relative = "provenance/source-commit.bundle"
        with tempfile.TemporaryDirectory() as directory:
            certificate = self.copy_certificate(Path(directory))
            bundle = certificate / relative
            data = bytearray(bundle.read_bytes())
            data[len(data) // 2] ^= 1
            bundle.write_bytes(data)
            self.refresh_artifact(certificate, relative)
            completed = self.run_verifier(certificate)
        self.assert_rejected_cleanly(
            completed,
            "source bundle",
        )

    def test_rejects_malformed_summary_without_traceback(self) -> None:
        relative = "coprime/cpp/summary.json"
        with tempfile.TemporaryDirectory() as directory:
            certificate = self.copy_certificate(Path(directory))
            summary_path = certificate / relative
            summary = json.loads(summary_path.read_text(encoding="ascii"))
            summary["results"][0] = "not an object"
            self.write_json(summary_path, summary)
            self.refresh_artifact(certificate, relative)
            completed = self.run_verifier(certificate)
        self.assert_rejected_cleanly(
            completed,
            "incomplete coordinate coverage",
        )


if __name__ == "__main__":
    unittest.main()
