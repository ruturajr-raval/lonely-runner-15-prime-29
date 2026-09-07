from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER_BUNDLER = ROOT / "tools" / "build_paper_bundle.py"
EXPECTED_PAPER_MEMBERS = (
    "LICENSE",
    "paper/ARXIV_METADATA.md",
    "paper/README.md",
    "paper/RIGHTS.md",
    "paper/main.tex",
)
sys.path.insert(0, str(ROOT / "tools"))

from verify_release_assets import EXPECTED_ASSETS, verify_release


class PaperBundleTests(unittest.TestCase):
    def test_paper_bundle_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.tar.gz"
            second = Path(directory) / "second.tar.gz"
            for output in (first, second):
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(PAPER_BUNDLER),
                        "--output",
                        str(output),
                    ],
                    cwd=ROOT,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with tarfile.open(first, mode="r:gz") as archive:
                members = archive.getmembers()
                self.assertEqual(
                    tuple(member.name for member in members),
                    EXPECTED_PAPER_MEMBERS,
                )
                for member in members:
                    self.assertTrue(member.isfile())
                    self.assertEqual(member.mode, 0o644)
                    self.assertEqual(member.mtime, 0)
                    self.assertEqual(member.uid, 0)
                    self.assertEqual(member.gid, 0)
                    self.assertEqual(member.uname, "")
                    self.assertEqual(member.gname, "")
                    extracted = archive.extractfile(member)
                    self.assertIsNotNone(extracted)
                    assert extracted is not None
                    self.assertEqual(
                        extracted.read(),
                        (ROOT / member.name).read_bytes(),
                    )


class ReleaseAssetTests(unittest.TestCase):
    def build_fixture(self, root: Path) -> None:
        release_dir = root / "dist" / "release"
        release_dir.mkdir(parents=True)
        payloads = {
            EXPECTED_ASSETS[0]: b"paper\n",
            EXPECTED_ASSETS[1]: b"source\n",
            EXPECTED_ASSETS[2]: b"certificate\n",
        }
        for name, payload in payloads.items():
            (release_dir / name).write_bytes(payload)
        checksum_lines = [
            f"{hashlib.sha256(payload).hexdigest()}  {name}\n"
            for name, payload in payloads.items()
        ]
        (release_dir / "SHA256SUMS").write_text(
            "".join(checksum_lines),
            encoding="ascii",
        )
        assets = {
            name: hashlib.sha256((release_dir / name).read_bytes()).hexdigest()
            for name in EXPECTED_ASSETS
        }
        (root / ".release-record.json").write_text(
            json.dumps({"assets": assets}, indent=2) + "\n",
            encoding="ascii",
        )

    def test_release_set_is_closed_and_verified(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.build_fixture(root)
            self.assertEqual(verify_release(root), ())
            (root / "dist" / "release" / "extra.bin").write_bytes(b"extra\n")
            errors = verify_release(root)
            self.assertTrue(
                any("release directory entry mismatch" in item for item in errors)
            )

    def test_release_set_rejects_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.build_fixture(root)
            (root / "dist" / "release" / EXPECTED_ASSETS[0]).write_bytes(
                b"tampered\n"
            )
            errors = verify_release(root)
            self.assertTrue(
                any("release record hash mismatch" in item for item in errors)
            )
            self.assertTrue(any("checksum mismatch" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
