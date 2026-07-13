from fastapi import FastAPI
from app.api.repository_release_certification import router as repository_release_certification_router
from app.api.repository_release_readiness import router as repository_release_readiness_router
from app.api.repository_snapshot_gate import router as repository_snapshot_gate_router
from app.api.repository_snapshot_policy import router as repository_snapshot_policy_router
from app.api.repository_snapshot_baseline import router as repository_snapshot_baseline_router
from app.api.repository_snapshot_comparison import router as repository_snapshot_comparison_router
from app.api.repository_intelligence_snapshot import router as repository_intelligence_snapshot_router
from app.api.repository_intelligence_report import router as repository_intelligence_report_router
from app.api.repository_intelligence_dashboard import router as repository_intelligence_dashboard_router
from app.api.repository_drift_detection import router as repository_drift_detection_router
from app.api.repository_search_index import router as repository_search_index_router
from app.api.repository_semantic_search import router as repository_semantic_search_router
from app.api.repository_architecture_report import router as repository_architecture_report_router
from app.api.repository_summary import router as repository_summary_router
from app.api.repository_knowledge_graph import router as repository_knowledge_graph_router
from app.api.engineering_progress import router as engineering_progress_router
from app.api.repository_cross_reference_graph import router as repository_cross_reference_graph_router
from app.api.repository_symbol_index import router as repository_symbol_index_router
from app.api.repository_import_graph import router as repository_import_graph_router
from app.api.repository_dependency_map import router as repository_dependency_map_router
from sqlalchemy import text

from app.db.session import engine
from app.api.entities import router as entities_router
from app.api.relationships import router as relationships_router
from app.api.tags import router as tags_router
from app.api.entity_tags import router as entity_tags_router
from app.api.search import router as search_router
from app.api.context import router as context_router
from app.api.documents import router as documents_router
from app.api.processing_jobs import router as processing_jobs_router
from app.api.repository_ingestion import router as repository_ingestion_router
from app.api.repository_incremental_ingestion import router as repository_incremental_ingestion_router
from app.api.git_repository_intelligence import router as git_repository_intelligence_router
from app.api.git_commit_preview import router as git_commit_preview_router
from app.api.git_file_change_preview import router as git_file_change_preview_router
from app.api.git_authorship_preview import router as git_authorship_preview_router
from app.api.git_intelligence_report import router as git_intelligence_report_router
from app.api.git_branch_analysis import router as git_branch_analysis_router
from app.api.git_objective_scorecard import router as git_objective_scorecard_router
from app.api.code_inventory import router as code_inventory_router
from app.api.source_outline import router as source_outline_router
from app.api.code_intelligence_report import router as code_intelligence_report_router
from app.api.code_objective_scorecard import router as code_objective_scorecard_router
from app.api.repository_health import router as repository_health_router
from app.api.backend_milestone import router as backend_milestone_router
from app.api.session_transition import router as session_transition_router
from app.api.operator_execution_rule import router as operator_execution_rule_router
from app.api.operator_execution_checklist import router as operator_execution_checklist_router
from app.api.operator_session_guard import router as operator_session_guard_router
from app.api.operator_progress_target import router as operator_progress_target_router
from app.api.milestone_closeout_package import router as milestone_closeout_package_router
from app.api.semantic_search import router as semantic_search_router
from app.api.repository_structure import router as repository_structure_router
from app.api.repository_package_map import router as repository_package_map_router

app = FastAPI(
    title="Midwest24 Archive API",
    version="0.1.0",
    description="Institutional memory infrastructure for Midwest24 Archive.",
)

app.include_router(entities_router)
app.include_router(relationships_router)
app.include_router(tags_router)
app.include_router(entity_tags_router)
app.include_router(search_router)
app.include_router(context_router)
app.include_router(documents_router)
app.include_router(processing_jobs_router)
app.include_router(repository_ingestion_router)
app.include_router(repository_incremental_ingestion_router)
app.include_router(git_repository_intelligence_router)
app.include_router(git_commit_preview_router)
app.include_router(git_file_change_preview_router)
app.include_router(git_authorship_preview_router)
app.include_router(git_intelligence_report_router)
app.include_router(git_branch_analysis_router)
app.include_router(git_objective_scorecard_router)
app.include_router(code_inventory_router)
app.include_router(source_outline_router)
app.include_router(code_intelligence_report_router)
app.include_router(code_objective_scorecard_router)
app.include_router(repository_health_router)
app.include_router(backend_milestone_router)
app.include_router(session_transition_router)
app.include_router(operator_execution_rule_router)
app.include_router(operator_execution_checklist_router)
app.include_router(operator_session_guard_router)
app.include_router(operator_progress_target_router)
app.include_router(milestone_closeout_package_router)
app.include_router(semantic_search_router)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "midwest24-archive-api"}


@app.get("/health/db", tags=["Health"])
def database_health_check() -> dict[str, str]:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {"status": "ok", "database": "connected"}

app.include_router(repository_structure_router)

app.include_router(repository_package_map_router)

app.include_router(repository_dependency_map_router)

app.include_router(repository_import_graph_router)

app.include_router(repository_symbol_index_router)

app.include_router(repository_cross_reference_graph_router)

app.include_router(engineering_progress_router)

app.include_router(repository_knowledge_graph_router)

app.include_router(repository_summary_router)

app.include_router(repository_architecture_report_router)

app.include_router(repository_semantic_search_router)

app.include_router(repository_search_index_router)

app.include_router(repository_drift_detection_router)

app.include_router(repository_intelligence_dashboard_router)

app.include_router(repository_intelligence_report_router)

app.include_router(repository_intelligence_snapshot_router)

app.include_router(repository_snapshot_comparison_router)

app.include_router(repository_snapshot_baseline_router)

app.include_router(repository_snapshot_policy_router)

app.include_router(repository_snapshot_gate_router)

app.include_router(repository_release_readiness_router)

app.include_router(repository_release_certification_router)
