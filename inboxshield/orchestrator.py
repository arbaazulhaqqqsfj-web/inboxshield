"""Multi-agent orchestration and audit trail."""

from __future__ import annotations

from .agents import IntakeAgent, PolicyAgent, ResponseAgent, SecurityAgent
from .models import Ticket, TriageResult


class InboxShield:
    """Coordinate specialized agents with security checks before reasoning."""

    def __init__(self) -> None:
        self.security_agent = SecurityAgent()
        self.intake_agent = IntakeAgent()
        self.policy_agent = PolicyAgent()
        self.response_agent = ResponseAgent()

    def triage(self, ticket: Ticket) -> TriageResult:
        security = self.security_agent.run(ticket)
        intake, intake_trace = self.intake_agent.run(ticket, security.redacted_message)
        policy, policy_trace = self.policy_agent.run(intake["category"])
        response, response_trace = self.response_agent.run(
            intake["category"],
            intake["urgency"],
            security.status,
            policy,
        )

        human_review = (
            security.status == "blocked_for_review"
            or intake["urgency"] in {"high", "critical"}
        )
        actions = list(intake["actions"])
        if human_review:
            actions.insert(0, "Require human approval before executing any action.")
        actions.append(f"Follow policy: {policy['policy']}")

        return TriageResult(
            category=intake["category"],
            urgency=intake["urgency"],
            confidence=intake["confidence"],
            summary=intake["summary"],
            recommended_queue=intake["queue"],
            required_actions=actions,
            draft_response=response,
            redacted_message=security.redacted_message,
            security_status=security.status,
            security_findings=security.findings,
            human_review_required=human_review,
            traces=[
                security.trace,
                intake_trace,
                policy_trace,
                response_trace,
            ],
        )

