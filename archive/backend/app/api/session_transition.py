from fastapi import APIRouter, status

from app.connectors.repository.session_transition import (
    SessionTransitionPrompt,
    SessionTransitionPromptBuilder,
)
from app.connectors.repository.session_transition_summary import SessionTransitionSummaryBuilder
from app.schemas.session_transition import (
    SessionTransitionCommandSetResponse,
    SessionTransitionOperatorSummaryResponse,
    SessionTransitionPromptResponse,
    SessionTransitionRequest,
)

router = APIRouter()


def serialize_session_transition_prompt(prompt: SessionTransitionPrompt) -> SessionTransitionPromptResponse:
    summary = SessionTransitionSummaryBuilder().build(prompt)

    return SessionTransitionPromptResponse(
        repository_path=prompt.repository_path,
        source_of_truth=prompt.source_of_truth,
        current_objective=prompt.current_objective,
        completed=prompt.completed,
        next_steps=prompt.next_steps,
        deferred=prompt.deferred,
        completed_count=prompt.completed_count,
        next_step_count=prompt.next_step_count,
        deferred_count=prompt.deferred_count,
        command_set=SessionTransitionCommandSetResponse(
            repository_path=prompt.command_set.repository_path,
            commands=prompt.command_set.commands,
        ),
        rendered_prompt=prompt.render(),
        summary=SessionTransitionOperatorSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/session-transition-prompt",
    response_model=SessionTransitionPromptResponse,
    status_code=status.HTTP_200_OK,
)
def get_session_transition_prompt(data: SessionTransitionRequest):
    prompt = SessionTransitionPromptBuilder().build(test_count=data.test_count)
    return serialize_session_transition_prompt(prompt)
