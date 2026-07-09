from app.connectors.repository.allowlist import RepositoryAllowlist
from app.connectors.repository.archive_repository_ingestor import (
    ArchiveRepositoryIngestionResult,
    ArchiveRepositoryIngestor,
    REPOSITORY_DOCUMENT_JOB_TYPE,
)
from app.connectors.repository.change_detector import (
    RepositoryChangeDetector,
    RepositoryChangeSet,
)
from app.connectors.repository.closeout import (
    RepositoryObjectiveCloseout,
    RepositoryObjectiveCloseoutBuilder,
)
from app.connectors.repository.config import (
    REPOSITORY_ALLOWED_ROOTS_ENV,
    get_repository_allowed_roots,
)
from app.connectors.repository.discovery_report import (
    DEFAULT_REPOSITORY_EXCLUDED_DIRS,
    DEFAULT_REPOSITORY_INCLUDED_SUFFIXES,
    RepositoryDiscoveryReport,
    RepositorySkippedPath,
    RepositoryUnsupportedFile,
)
from app.connectors.repository.duplicate_detector import (
    RepositoryDuplicateDetector,
    RepositoryDuplicateFile,
)
from app.connectors.repository.file_copier import RepositoryFileCopier
from app.connectors.repository.file_fingerprint import RepositoryFileFingerprinter
from app.connectors.repository.filesystem_repository_connector import (
    RepositoryFile,
    RepositoryFilesystemConnector,
)
from app.connectors.repository.git_branches import GitBranch, GitBranchReader

from app.connectors.repository.git_branch_analysis import (
    GitBranchAnalysis,
    GitBranchAnalysisBuilder,
)
from app.connectors.repository.git_branch_analysis_summary import (
    GitBranchAnalysisOperatorSummary,
    GitBranchAnalysisSummaryBuilder,
)

from app.connectors.repository.git_authorship import (
    GitAuthorSummary,
    GitAuthorshipPreview,
    GitAuthorshipPreviewBuilder,
)
from app.connectors.repository.git_authorship_summary import (
    GitAuthorshipOperatorSummary,
    GitAuthorshipSummaryBuilder,
)
from app.connectors.repository.git_command import GitCommandResult, GitCommandRunner
from app.connectors.repository.git_commit import GitCommit, GitCommitParser

from app.connectors.repository.git_file_change import (
    GitCommitFileChangeSet,
    GitFileChange,
    GitFileChangeParser,
    GitFileChangePreview,
    GitFileChangePreviewBuilder,
)
from app.connectors.repository.git_file_change_summary import (
    GitFileChangeOperatorSummary,
    GitFileChangeSummaryBuilder,
)
from app.connectors.repository.git_history import GitHistoryReader

from app.connectors.repository.git_intelligence_closeout import (
    GitIntelligenceCloseout,
    GitIntelligenceCloseoutBuilder,
)
from app.connectors.repository.git_intelligence_readiness import (
    GitIntelligenceReadinessCheck,
    GitIntelligenceReadinessEvaluator,
    GitIntelligenceReadinessReport,
)
from app.connectors.repository.git_intelligence_report import (
    GitIntelligenceReport,
    GitIntelligenceReportBuilder,
)
from app.connectors.repository.git_intelligence_summary import (
    GitIntelligenceOperatorSummary,
    GitIntelligenceSummaryBuilder,
)
from app.connectors.repository.git_operator_summary import (
    GitRepositoryOperatorSummary,
    GitRepositoryOperatorSummaryBuilder,
)
from app.connectors.repository.git_preview import (
    GitAuthorContribution,
    GitCommitPreview,
    GitCommitPreviewBuilder,
)
from app.connectors.repository.git_preview_summary import (
    GitCommitPreviewOperatorSummary,
    GitCommitPreviewSummaryBuilder,
)
from app.connectors.repository.git_repository import GitRepositoryDetector
from app.connectors.repository.git_status import GitStatusEntry, GitStatusReader, GitStatusReport
from app.connectors.repository.git_summary import GitRepositorySummary, GitRepositorySummaryBuilder
from app.connectors.repository.incremental_ingestion import RepositoryIncrementalIngestor
from app.connectors.repository.incremental_report import RepositoryIncrementalIngestionReport
from app.connectors.repository.ingestion_report import (
    RepositoryIngestionFailure,
    RepositoryIngestionReport,
)
from app.connectors.repository.job_statistics import (
    ProcessingJobStatusCounts,
    RepositoryProcessingJobStatistics,
)
from app.connectors.repository.manifest import (
    RepositoryManifest,
    RepositoryManifestEntry,
    RepositoryManifestStore,
)
from app.connectors.repository.objective_summary import (
    RepositoryObjectiveSummary,
    RepositoryObjectiveSummaryBuilder,
)
from app.connectors.repository.operator_summary import (
    RepositoryIncrementalOperatorSummary,
    RepositoryIncrementalSummaryBuilder,
    RepositoryIngestionOperatorSummary,
    RepositoryIngestionSummaryBuilder,
)
from app.connectors.repository.path_validator import RepositoryPathValidator
from app.connectors.repository.readiness import (
    RepositoryObjectiveReadinessEvaluator,
    RepositoryReadinessCheck,
    RepositoryReadinessReport,
)
from app.connectors.repository.repository_ingestion_service import (
    RepositoryDocumentIngestor,
    RepositoryIngestionResult,
    RepositoryIngestionService,
    RepositoryProcessingJobCreator,
)
from app.connectors.repository.snapshot import RepositorySnapshotter

__all__ = [
    "GitBranchAnalysisSummaryBuilder",
    "GitBranchAnalysisOperatorSummary",
    "GitBranchAnalysisBuilder",
    "GitBranchAnalysis",
    "GitIntelligenceSummaryBuilder",
    "GitIntelligenceReportBuilder",
    "GitIntelligenceReport",
    "GitIntelligenceReadinessReport",
    "GitIntelligenceReadinessEvaluator",
    "GitIntelligenceReadinessCheck",
    "GitIntelligenceOperatorSummary",
    "GitIntelligenceCloseoutBuilder",
    "GitIntelligenceCloseout",
    "GitAuthorshipSummaryBuilder",
    "GitAuthorshipOperatorSummary",
    "GitAuthorshipPreviewBuilder",
    "GitAuthorshipPreview",
    "GitAuthorSummary",
    "GitFileChangeSummaryBuilder",
    "GitFileChangeOperatorSummary",
    "GitFileChangePreviewBuilder",
    "GitFileChangePreview",
    "GitFileChangeParser",
    "GitFileChange",
    "GitCommitFileChangeSet",
    "ArchiveRepositoryIngestionResult",
    "ArchiveRepositoryIngestor",
    "DEFAULT_REPOSITORY_EXCLUDED_DIRS",
    "DEFAULT_REPOSITORY_INCLUDED_SUFFIXES",
    "GitAuthorContribution",
    "GitBranch",
    "GitBranchReader",
    "GitCommandResult",
    "GitCommandRunner",
    "GitCommit",
    "GitCommitParser",
    "GitCommitPreview",
    "GitCommitPreviewBuilder",
    "GitCommitPreviewOperatorSummary",
    "GitCommitPreviewSummaryBuilder",
    "GitHistoryReader",
    "GitRepositoryDetector",
    "GitRepositoryOperatorSummary",
    "GitRepositoryOperatorSummaryBuilder",
    "GitRepositorySummary",
    "GitRepositorySummaryBuilder",
    "GitStatusEntry",
    "GitStatusReader",
    "GitStatusReport",
    "ProcessingJobStatusCounts",
    "REPOSITORY_ALLOWED_ROOTS_ENV",
    "REPOSITORY_DOCUMENT_JOB_TYPE",
    "RepositoryAllowlist",
    "RepositoryChangeDetector",
    "RepositoryChangeSet",
    "RepositoryDiscoveryReport",
    "RepositoryDocumentIngestor",
    "RepositoryDuplicateDetector",
    "RepositoryDuplicateFile",
    "RepositoryFile",
    "RepositoryFileCopier",
    "RepositoryFileFingerprinter",
    "RepositoryFilesystemConnector",
    "RepositoryIncrementalIngestionReport",
    "RepositoryIncrementalIngestor",
    "RepositoryIncrementalOperatorSummary",
    "RepositoryIncrementalSummaryBuilder",
    "RepositoryIngestionFailure",
    "RepositoryIngestionOperatorSummary",
    "RepositoryIngestionReport",
    "RepositoryIngestionResult",
    "RepositoryIngestionService",
    "RepositoryIngestionSummaryBuilder",
    "RepositoryManifest",
    "RepositoryManifestEntry",
    "RepositoryManifestStore",
    "RepositoryObjectiveCloseout",
    "RepositoryObjectiveCloseoutBuilder",
    "RepositoryObjectiveReadinessEvaluator",
    "RepositoryObjectiveSummary",
    "RepositoryObjectiveSummaryBuilder",
    "RepositoryPathValidator",
    "RepositoryProcessingJobCreator",
    "RepositoryProcessingJobStatistics",
    "RepositoryReadinessCheck",
    "RepositoryReadinessReport",
    "RepositorySkippedPath",
    "RepositorySnapshotter",
    "RepositoryUnsupportedFile",
    "get_repository_allowed_roots",
]
