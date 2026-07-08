from pathlib import Path

from app.connectors.repository.cli.ingest_repository import main


def test_repository_ingestion_cli_reports_repository_ingestion_counts(
    tmp_path: Path,
    capsys,
    monkeypatch,
):
    repo = tmp_path / "knowledge-repo"
    repo.mkdir()

    (repo / "README.md").write_text("# Knowledge Repo\n", encoding="utf-8")
    (repo / "OPERATING-PLAN.md").write_text("Execute the Operating Plan.\n", encoding="utf-8")
    (repo / "image.png").write_bytes(b"skip")

    monkeypatch.setattr(
        "sys.argv",
        ["ingest_repository", str(repo)],
    )

    exit_code = main()
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Discovered files: 2" in output
    assert "Ingested documents: 2" in output
    assert "Processing jobs created: 2" in output
