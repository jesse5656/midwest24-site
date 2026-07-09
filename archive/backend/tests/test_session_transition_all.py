import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.session_transition import serialize_session_transition_prompt
from app.connectors.repository.session_transition import (
    SessionTransitionCommandSet,
    SessionTransitionPrompt,
    SessionTransitionPromptBuilder,
)
from app.connectors.repository.session_transition_summary import SessionTransitionSummaryBuilder
from app.main import app
from app.schemas.session_transition import (
    SessionTransitionCommandSetResponse,
    SessionTransitionPromptResponse,
    SessionTransitionRequest,
)

client = TestClient(app)


def make_prompt():
    return SessionTransitionPrompt(
        repository_path="~/Documents/Projects/midwest24-site",
        source_of_truth="repository",
        current_objective="Archive Backend Health and Closeout",
        completed=["773 passing tests", "Backend milestone"],
        next_steps=["Prepare transition"],
        deferred=["Full AST parsing"],
    )


def test_session_transition_001_command_set_repository_cd():
    assert SessionTransitionCommandSet("~/repo").commands[0] == "cd ~/repo"


def test_session_transition_002_command_set_pwd():
    assert "pwd" in SessionTransitionCommandSet("~/repo").commands


def test_session_transition_003_command_set_branch():
    assert "git branch --show-current" in SessionTransitionCommandSet("~/repo").commands


def test_session_transition_004_command_set_status():
    assert "git status --short" in SessionTransitionCommandSet("~/repo").commands


def test_session_transition_005_command_set_log():
    assert "git log --oneline --decorate -5" in SessionTransitionCommandSet("~/repo").commands


def test_session_transition_006_command_set_tree():
    assert "tree -L 3" in SessionTransitionCommandSet("~/repo").commands


def test_session_transition_007_command_set_start_here():
    assert "sed -n '1,220p' START-HERE.md" in SessionTransitionCommandSet("~/repo").commands


def test_session_transition_008_command_set_operating_plan():
    assert "sed -n '1,420p' OPERATING-PLAN.md" in SessionTransitionCommandSet("~/repo").commands


def test_session_transition_009_command_set_archive_cd():
    assert "cd archive" in SessionTransitionCommandSet("~/repo").commands


def test_session_transition_010_command_set_make_test():
    assert "make test" in SessionTransitionCommandSet("~/repo").commands


def test_session_transition_011_prompt_completed_count():
    assert make_prompt().completed_count == 2


def test_session_transition_012_prompt_next_step_count():
    assert make_prompt().next_step_count == 1


def test_session_transition_013_prompt_deferred_count():
    assert make_prompt().deferred_count == 1


def test_session_transition_014_prompt_command_set_path():
    assert make_prompt().command_set.repository_path == "~/Documents/Projects/midwest24-site"


def test_session_transition_015_render_title():
    assert "Session Transition Prompt" in make_prompt().render()


def test_session_transition_016_render_source_of_truth():
    assert "source of truth" in make_prompt().render()


def test_session_transition_017_render_required_verification():
    assert "Required Verification" in make_prompt().render()


def test_session_transition_018_render_current_objective():
    assert "Archive Backend Health and Closeout" in make_prompt().render()


def test_session_transition_019_render_completed_item():
    assert "Backend milestone" in make_prompt().render()


def test_session_transition_020_render_next_step():
    assert "Prepare transition" in make_prompt().render()


def test_session_transition_021_render_deferred():
    assert "Full AST parsing" in make_prompt().render()


def test_session_transition_022_render_operating_rule():
    assert "Execute one coherent objective" in make_prompt().render()


def test_session_transition_023_builder_repository_path():
    assert SessionTransitionPromptBuilder().build(773).repository_path == "~/Documents/Projects/midwest24-site"


def test_session_transition_024_builder_source_of_truth():
    assert SessionTransitionPromptBuilder().build(773).source_of_truth == "repository"


def test_session_transition_025_builder_objective():
    assert SessionTransitionPromptBuilder().build(773).current_objective == "Archive Backend Health and Closeout"


def test_session_transition_026_builder_test_count():
    assert "773 passing tests" in SessionTransitionPromptBuilder().build(773).completed


def test_session_transition_027_builder_git_completed():
    assert "Git Repository Intelligence" in SessionTransitionPromptBuilder().build(773).completed


def test_session_transition_028_builder_code_completed():
    assert "Code Intelligence Preview" in SessionTransitionPromptBuilder().build(773).completed


def test_session_transition_029_builder_health_completed():
    assert "Archive backend health reporting" in SessionTransitionPromptBuilder().build(773).completed


def test_session_transition_030_builder_milestone_completed():
    assert "Archive backend milestone scorecard" in SessionTransitionPromptBuilder().build(773).completed


def test_session_transition_031_builder_next_steps():
    assert "Prepare final transition prompt" in SessionTransitionPromptBuilder().build(773).next_steps


def test_session_transition_032_builder_deferred_ast():
    assert "Full AST parsing" in SessionTransitionPromptBuilder().build(773).deferred


def test_session_transition_033_summary_ready():
    summary = SessionTransitionSummaryBuilder().build(make_prompt())
    assert summary.outcome == "ready"


def test_session_transition_034_summary_ready_no_action():
    summary = SessionTransitionSummaryBuilder().build(make_prompt())
    assert summary.action_required is False


def test_session_transition_035_summary_incomplete_without_completed():
    prompt = SessionTransitionPrompt("~/repo", "repository", "Objective", [], ["Next"], [])
    summary = SessionTransitionSummaryBuilder().build(prompt)
    assert summary.outcome == "incomplete_transition"


def test_session_transition_036_summary_missing_next_steps():
    prompt = SessionTransitionPrompt("~/repo", "repository", "Objective", ["Done"], [], [])
    summary = SessionTransitionSummaryBuilder().build(prompt)
    assert summary.outcome == "missing_next_steps"


def test_session_transition_037_summary_message_counts():
    summary = SessionTransitionSummaryBuilder().build(make_prompt())
    assert "completed item" in summary.message


def test_session_transition_038_request_accepts_count():
    assert SessionTransitionRequest(test_count=773).test_count == 773


def test_session_transition_039_request_rejects_negative():
    with pytest.raises(ValidationError):
        SessionTransitionRequest(test_count=-1)


def test_session_transition_040_command_response_accepts_payload():
    response = SessionTransitionCommandSetResponse(repository_path="~/repo", commands=["pwd"])
    assert response.commands == ["pwd"]


def test_session_transition_041_prompt_response_serializes():
    prompt = serialize_session_transition_prompt(make_prompt())
    payload = prompt.model_dump()
    assert payload["repository_path"] == "~/Documents/Projects/midwest24-site"


def test_session_transition_042_serialize_counts():
    response = serialize_session_transition_prompt(make_prompt())
    assert response.completed_count == 2


def test_session_transition_043_serialize_command_set():
    response = serialize_session_transition_prompt(make_prompt())
    assert "make test" in response.command_set.commands


def test_session_transition_044_serialize_rendered_prompt():
    response = serialize_session_transition_prompt(make_prompt())
    assert "Session Transition Prompt" in response.rendered_prompt


def test_session_transition_045_serialize_summary():
    response = serialize_session_transition_prompt(make_prompt())
    assert response.summary.outcome == "ready"


def test_session_transition_046_api_returns_prompt():
    response = client.post("/api/v1/session-transition-prompt", json={"test_count": 773})
    assert response.status_code == 200


def test_session_transition_047_api_repository_path():
    response = client.post("/api/v1/session-transition-prompt", json={"test_count": 773})
    assert response.json()["repository_path"] == "~/Documents/Projects/midwest24-site"


def test_session_transition_048_api_rendered_prompt():
    response = client.post("/api/v1/session-transition-prompt", json={"test_count": 773})
    assert "Session Transition Prompt" in response.json()["rendered_prompt"]


def test_session_transition_049_api_commands():
    response = client.post("/api/v1/session-transition-prompt", json={"test_count": 773})
    assert "make test" in response.json()["command_set"]["commands"]


def test_session_transition_050_api_rejects_negative():
    response = client.post("/api/v1/session-transition-prompt", json={"test_count": -1})
    assert response.status_code == 422


def test_session_transition_051_api_requires_test_count():
    response = client.post("/api/v1/session-transition-prompt", json={})
    assert response.status_code == 422


def test_session_transition_052_route_registered():
    paths = {route.path for route in app.routes}
    assert "/api/v1/session-transition-prompt" in paths
