from __future__ import annotations

from dataclasses import dataclass

from app.connectors.repository.session_transition import SessionTransitionPrompt


@dataclass(frozen=True)
class SessionTransitionOperatorSummary:
    outcome: str
    message: str
    action_required: bool


class SessionTransitionSummaryBuilder:
    def build(self, prompt: SessionTransitionPrompt) -> SessionTransitionOperatorSummary:
        if prompt.completed_count == 0:
            return SessionTransitionOperatorSummary(
                outcome="incomplete_transition",
                message="Session transition prompt has no completed work recorded.",
                action_required=True,
            )

        if prompt.next_step_count == 0:
            return SessionTransitionOperatorSummary(
                outcome="missing_next_steps",
                message="Session transition prompt has no next steps recorded.",
                action_required=True,
            )

        return SessionTransitionOperatorSummary(
            outcome="ready",
            message=(
                f"Session transition prompt is ready with "
                f"{prompt.completed_count} completed item(s), "
                f"{prompt.next_step_count} next step(s), and "
                f"{prompt.deferred_count} deferred item(s)."
            ),
            action_required=False,
        )
