from pathlib import Path

from app.connectors.repository import RepositoryIngestionService


def test_repository_ingestion_service_wires_discovery_to_document_ingestion_and_processing_jobs(
    tmp_path: Path,
):
    repo = tmp_path / "knowledge-repo"
    repo.mkdir()

    (repo / "README.md").write_text("# Knowledge Repo\n", encoding="utf-8")
    (repo / "OPERATING-PLAN.md").write_text("Execute the Operating Plan.\n", encoding="utf-8")

    ingested_files = []
    processing_jobs = []

    def document_ingestor(repository_file):
        document = {
            "source_type": "repository_file",
            "source_path": repository_file.relative_path,
            "size_bytes": repository_file.size_bytes,
        }
        ingested_files.append(document)
        return document

    def processing_job_creator(ingested_document, repository_file):
        job = {
            "document": ingested_document,
            "source_path": repository_file.relative_path,
            "pipeline": "archive_processing",
        }
        processing_jobs.append(job)
        return job

    service = RepositoryIngestionService.from_path(
        repository_path=repo,
        document_ingestor=document_ingestor,
        processing_job_creator=processing_job_creator,
    )

    result = service.ingest()

    assert result.discovered_count == 2
    assert result.ingested_count == 2
    assert result.processing_job_count == 2

    assert {item["source_path"] for item in ingested_files} == {
        "README.md",
        "OPERATING-PLAN.md",
    }

    assert {item["source_path"] for item in (job["document"] for job in processing_jobs)} == {
        "README.md",
        "OPERATING-PLAN.md",
    }

    assert all(job["pipeline"] == "archive_processing" for job in processing_jobs)


def test_repository_ingestion_service_uses_connector_filtering_before_ingestion(
    tmp_path: Path,
):
    repo = tmp_path / "knowledge-repo"
    repo.mkdir()

    (repo / "README.md").write_text("# Knowledge Repo\n", encoding="utf-8")
    (repo / "image.png").write_bytes(b"skip")

    git_dir = repo / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("[core]\n", encoding="utf-8")

    ingested_files = []

    def document_ingestor(repository_file):
        ingested_files.append(repository_file.relative_path)
        return {"source_path": repository_file.relative_path}

    def processing_job_creator(ingested_document, repository_file):
        return {"document": ingested_document}

    service = RepositoryIngestionService.from_path(
        repository_path=repo,
        document_ingestor=document_ingestor,
        processing_job_creator=processing_job_creator,
    )

    result = service.ingest()

    assert result.discovered_count == 1
    assert result.ingested_count == 1
    assert result.processing_job_count == 1
    assert ingested_files == ["README.md"]
