from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools" / "check_release_metadata.py"
METADATA_FILES = (
    "CITATION.cff",
    "README.md",
    "PUBLICATION.md",
    "RELEASE_NOTES.md",
    "pyproject.toml",
    ".zenodo.json",
    "paper/ARXIV_METADATA.md",
)


class ReleaseMetadataTests(unittest.TestCase):
    def run_checker(
        self,
        root: Path,
        tag: str | None = None,
        repository: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        command = [
            sys.executable,
            str(CHECKER),
            "--root",
            str(root),
        ]
        if tag is not None:
            command.extend(["--tag", tag])
        if repository is not None:
            command.extend(["--repository", repository])
        return subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

    def copy_metadata(self, destination: Path) -> None:
        for relative in METADATA_FILES:
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)

    def test_current_metadata_is_consistent(self) -> None:
        completed = self.run_checker(
            ROOT,
            "v0.1.0",
            "ruturajr-raval/lonely-runner-15-prime-29",
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "release metadata consistent for v0.1.0",
            completed.stdout,
        )

    def test_wrong_tag_is_rejected(self) -> None:
        completed = self.run_checker(ROOT, "v0.1.1")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("does not match metadata tag", completed.stderr)

    def test_wrong_repository_is_rejected(self) -> None:
        completed = self.run_checker(
            ROOT,
            "v0.1.0",
            "ruturajr-raval/lonely-runner-15-research-workbench",
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn(
            "does not match publication repository",
            completed.stderr,
        )

    def test_cross_file_version_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_metadata(root)
            path = root / ".zenodo.json"
            metadata = json.loads(path.read_text(encoding="utf-8"))
            metadata["version"] = "0.1.1"
            path.write_text(
                json.dumps(metadata, indent=2) + "\n",
                encoding="utf-8",
            )
            completed = self.run_checker(root)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn(".zenodo.json: version", completed.stderr)

    def test_missing_version_doi_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_metadata(root)
            path = root / "CITATION.cff"
            text = path.read_text(encoding="utf-8")
            path.write_text(
                text.replace(
                    "10.5281/zenodo.22539842",
                    "10.5281/zenodo.00000000",
                    1,
                ),
                encoding="utf-8",
            )
            completed = self.run_checker(root)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("CITATION.cff: expected at least", completed.stderr)


if __name__ == "__main__":
    unittest.main()
