from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.git_authorship import GitAuthorshipPreview
from app.connectors.repository.git_file_change import GitFileChangePreview
from app.connectors.repository.git_preview import GitCommitPreview
from app.connectors.repository.git_summary import GitRepositorySummary


@dataclass(frozen=True)
class GitIntelligenceReport:
    repository: GitRepositorySummary
    commits: GitCommitPreview
    file_changes: GitFileChangePreview
    authorship: GitAuthorshipPreview

    @property
    def is_repository(self) -> bool:
        return self.repository.is_repository

    @property
    def current_branch(self) -> str | None:
        return self.repository.current_branch

    @property
    def commit_count(self) -> int:
        return self.commits.commit_count

    @property
    def file_change_count(self) -> int:
        return self.file_changes.file_change_count

    @property
    def author_count(self) -> int:
        return self.authorship.author_count

    @property
    def has_uncommitted_changes(self) -> bool:
        return self.repository.is_clean is False

    @property
    def is_ready(self) -> bool:
        return self.is_repository and self.commit_count > 0 and self.author_count > 0


class GitIntelligenceReportBuilder:
    def __init__(
        self,
        repository_summary_builder=None,
        commit_preview_builder=None,
        file_change_preview_builder=None,
        authorship_preview_builder=None,
    ):
        from app.connectors.repository.git_authorship import GitAuthorshipPreviewBuilder
        from app.connectors.repository.git_file_change import GitFileChangePreviewBuilder
        from app.connectors.repository.git_preview import GitCommitPreviewBuilder
        from app.connectors.repository.git_summary import GitRepositorySummaryBuilder

        self.repository_summary_builder = repository_summary_builder or GitRepositorySummaryBuilder()
        self.commit_preview_builder = commit_preview_builder or GitCommitPreviewBuilder()
        self.file_change_preview_builder = file_change_preview_builder or GitFileChangePreviewBuilder()
        self.authorship_preview_builder = authorship_preview_builder or GitAuthorshipPreviewBuilder()

    def build(self, repository_path: str, limit: int = 25) -> GitIntelligenceReport:
        repository = self.repository_summary_builder.build(repository_path, commit_limit=limit)

        if not repository.is_repository:
            return GitIntelligenceReport(
                repository=repository,
                commits=GitCommitPreview(),
                file_changes=GitFileChangePreview(),
                authorship=GitAuthorshipPreview(),
            )

        return GitIntelligenceReport(
            repository=repository,
            commits=self.commit_preview_builder.build(repository_path, limit=limit),
            file_changes=self.file_change_preview_builder.build(repository_path, limit=limit),
            authorship=self.authorship_preview_builder.build(repository_path, limit=limit),
        )
