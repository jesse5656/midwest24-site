from pathlib import Path

from app.connectors.repository import RepositoryFileFingerprinter


def test_repository_file_fingerprint_is_sha256_hex(tmp_path: Path):
    file = tmp_path / "README.md"
    file.write_text("hello\n", encoding="utf-8")

    fingerprint = RepositoryFileFingerprinter().fingerprint(file)

    assert len(fingerprint) == 64
    assert all(char in "0123456789abcdef" for char in fingerprint)


def test_repository_file_fingerprint_changes_when_content_changes(tmp_path: Path):
    file = tmp_path / "README.md"
    file.write_text("first\n", encoding="utf-8")

    first = RepositoryFileFingerprinter().fingerprint(file)

    file.write_text("second\n", encoding="utf-8")

    second = RepositoryFileFingerprinter().fingerprint(file)

    assert first != second


def test_repository_file_fingerprint_same_for_same_content(tmp_path: Path):
    first_file = tmp_path / "one.md"
    second_file = tmp_path / "two.md"

    first_file.write_text("same\n", encoding="utf-8")
    second_file.write_text("same\n", encoding="utf-8")

    fingerprinter = RepositoryFileFingerprinter()

    assert fingerprinter.fingerprint(first_file) == fingerprinter.fingerprint(second_file)
