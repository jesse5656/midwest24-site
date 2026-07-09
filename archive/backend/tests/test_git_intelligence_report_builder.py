from app.connectors.repository import (
    GitAuthorshipPreview,
    GitCommitPreview,
    GitFileChangePreview,
    GitIntelligenceReportBuilder,
    GitRepositorySummary,
)


class FakeRepositorySummaryBuilder:
    def __init__(self, summary):
        self.summary = summary
        self.repository_path = None
        self.commit_limit = None

    def build(self, repository_path, commit_limit=25):
        self.repository_path = repository_path
        self.commit_limit = commit_limit
        return self.summary


class FakePreviewBuilder:
    def __init__(self, preview):
        self.preview = preview
        self.repository_path = None
        self.limit = None

    def build(self, repository_path, limit=25):
        self.repository_path = repository_path
        self.limit = limit
        return self.preview


def test_git_intelligence_report_builder_skips_previews_for_non_repository():
    repo_builder = FakeRepositorySummaryBuilder(
        GitRepositorySummary(
            is_repository=False,
            root=None,
            current_branch=None,
            recent_commit_count=0,
            is_clean=None,
        )
    )

    report = GitIntelligenceReportBuilder(
        repository_summary_builder=repo_builder,
        commit_preview_builder=FakePreviewBuilder(GitCommitPreview()),
        file_change_preview_builder=FakePreviewBuilder(GitFileChangePreview()),
        authorship_preview_builder=FakePreviewBuilder(GitAuthorshipPreview()),
    ).build("/repo", limit=10)

    assert report.is_repository is False
    assert report.commit_count == 0
    assert report.file_change_count == 0
    assert report.author_count == 0


def test_git_intelligence_report_builder_builds_all_previews_for_repository():
    repo_builder = FakeRepositorySummaryBuilder(
        GitRepositorySummary(
            is_repository=True,
            root="/repo",
            current_branch="main",
            recent_commit_count=1,
            is_clean=True,
        )
    )
    commit_builder = FakePreviewBuilder(GitCommitPreview())
    file_builder = FakePreviewBuilder(GitFileChangePreview())
    author_builder = FakePreviewBuilder(GitAuthorshipPreview())

    GitIntelligenceReportBuilder(
        repository_summary_builder=repo_builder,
        commit_preview_builder=commit_builder,
        file_change_preview_builder=file_builder,
        authorship_preview_builder=author_builder,
    ).build("/repo", limit=12)

    assert repo_builder.repository_path == "/repo"
    assert repo_builder.commit_limit == 12
    assert commit_builder.repository_path == "/repo"
    assert commit_builder.limit == 12
    assert file_builder.repository_path == "/repo"
    assert file_builder.limit == 12
    assert author_builder.repository_path == "/repo"
    assert author_builder.limit == 12
