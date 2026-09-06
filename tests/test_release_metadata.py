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
    ".release-record.json",
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
            "v0.1.1",
            "ruturajr-raval/lonely-runner-15-prime-29",
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "release metadata consistent for v0.1.1",
            completed.stdout,
        )

    def test_wrong_tag_is_rejected(self) -> None:
        completed = self.run_checker(ROOT, "v0.1.0")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("does not match metadata tag", completed.stderr)

    def test_wrong_repository_is_rejected(self) -> None:
        completed = self.run_checker(
            ROOT,
            "v0.1.1",
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
            metadata["version"] = "0.1.0"
            path.write_text(
                json.dumps(metadata, indent=2) + "\n",
                encoding="utf-8",
            )
            completed = self.run_checker(root)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn(".zenodo.json: version", completed.stderr)

    def test_missing_concept_doi_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_metadata(root)
            path = root / "README.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(
                text.replace(
                    "10.5281/zenodo.22539841",
                    "10.5281/zenodo.00000000",
                ),
                encoding="utf-8",
            )
            completed = self.run_checker(root)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("README.md: expected at least", completed.stderr)

    def test_unrecognized_version_doi_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_metadata(root)
            path = root / "README.md"
            path.write_text(
                path.read_text(encoding="utf-8")
                + "\n10.5281/zenodo.22539842\n",
                encoding="utf-8",
            )
            completed = self.run_checker(root)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("contains unrecognized Zenodo DOI", completed.stderr)

    def test_unrecognized_zenodo_description_doi_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_metadata(root)
            path = root / ".zenodo.json"
            metadata = json.loads(path.read_text(encoding="utf-8"))
            metadata["description"] += " 10.5281/zenodo.22539842"
            path.write_text(
                json.dumps(metadata, indent=2) + "\n",
                encoding="utf-8",
            )
            completed = self.run_checker(root)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn(
            ".zenodo.json: contains unrecognized Zenodo DOI",
            completed.stderr,
        )

    def test_incomplete_archival_record_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_metadata(root)
            path = root / ".release-record.json"
            metadata = json.loads(path.read_text(encoding="utf-8"))
            metadata["version_doi"] = "10.5281/zenodo.99999999"
            metadata["release_commit"] = None
            path.write_text(
                json.dumps(metadata, indent=2) + "\n",
                encoding="utf-8",
            )
            completed = self.run_checker(root)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("invalid release_commit", completed.stderr)

    def test_missing_version_doi_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_metadata(root)
            path = root / "CITATION.cff"
            text = path.read_text(encoding="utf-8")
            path.write_text(
                text.replace(
                    "10.5281/zenodo.22541517",
                    "10.5281/zenodo.00000000",
                    1,
                ),
                encoding="utf-8",
            )
            completed = self.run_checker(root)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("CITATION.cff: expected at least", completed.stderr)

    def test_archival_file_count_requires_exact_labeled_line(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_metadata(root)
            version_doi = "10.5281/zenodo.99999999"
            release_commit = "a" * 40
            asset_hashes = {
                name: f"{index + 1:064x}"
                for index, name in enumerate(
                    (
                        "lonely-runner-15-prime-29-paper.pdf",
                        "lonely-runner-15-prime-29-source.tar.gz",
                        "lonely-runner-15-prime-29-certificate-v1.tar.gz",
                        "SHA256SUMS",
                    )
                )
            }
            archive_name = "test-v0.1.1.zip"
            archive_sha256 = "f" * 64
            record_path = root / ".release-record.json"
            record = json.loads(record_path.read_text(encoding="utf-8"))
            record.update(
                {
                    "version_doi": version_doi,
                    "release_commit": release_commit,
                    "assets": asset_hashes,
                    "zenodo_archive": {
                        "filename": archive_name,
                        "sha256": archive_sha256,
                        "file_count": 1,
                    },
                }
            )
            record_path.write_text(
                json.dumps(record, indent=2) + "\n",
                encoding="utf-8",
            )
            citation = root / "CITATION.cff"
            citation.write_text(
                citation.read_text(encoding="utf-8").replace(
                    "10.5281/zenodo.22541517",
                    version_doi,
                ),
                encoding="utf-8",
            )
            for relative in (
                "README.md",
                "PUBLICATION.md",
                "paper/ARXIV_METADATA.md",
            ):
                path = root / relative
                path.write_text(
                    path.read_text(encoding="utf-8").replace(
                        "10.5281/zenodo.22541517",
                        version_doi,
                    ),
                    encoding="utf-8",
                )
            publication = root / "PUBLICATION.md"
            lines = [
                f"- Version DOI: `{version_doi}`",
                f"- Release commit: `{release_commit}`",
                *(
                    f"- `{name}`: `{digest}`"
                    for name, digest in asset_hashes.items()
                ),
                f"- Zenodo archive: `{archive_name}`",
                f"- Zenodo archive SHA-256: `{archive_sha256}`",
                "- Archived file count: `10`",
            ]
            publication.write_text(
                publication.read_text(encoding="utf-8")
                + "\n"
                + "\n".join(lines)
                + "\n",
                encoding="utf-8",
            )
            completed = self.run_checker(root)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn(
            "missing archival record line: - Archived file count: `1`",
            completed.stderr,
        )


if __name__ == "__main__":
    unittest.main()
