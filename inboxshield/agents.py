"""Specialized agents used by the InboxShield orchestrator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import AgentTrace, SecurityFinding, Ticket
from .security import contains_high_risk, scan_and_redact
from .skills import (
    assess_urgency,
    classify_ticket,
    lookup_policy,
    response_template,
    summarize,
)


@dataclass(slots=True)
class SecurityOutput:
    redacted_message: str
    findings: list[SecurityFinding]
    status: str
    trace: AgentTrace


class SecurityAgent:
    name = "Security Agent"

    def run(self, ticket: Ticket) -> SecurityOutput:
        redacted, findings = scan_and_redact(ticket.message)
        status = "blocked_for_review" if contains_high_risk(findings) else (
            "redacted" if findings else "clear"
        )
        return SecurityOutput(
            redacted_message=redacted,
            findings=findings,
            status=status,
            trace=AgentTrace(
                agent=self.name,
                purpose="Treat input as untrusted, detect injection, and minimize PII.",
                tools=["security.scan_and_redact"],
                output={
                    "status": status,
                    "finding_types": [finding.kind for finding in findings],
                },
            ),
        )


class IntakeAgent:
    name = "Intake Agent"

    def run(self, ticket: Ticket, safe_message: str) -> tuple[dict[str, Any], AgentTrace]:
        category, queue, confidence = classify_ticket(ticket.subject, safe_message)
        urgency, actions = assess_urgency(safe_message, ticket.customer_tier)
        output = {
            "category": category,
            "queue": queue,
            "confidence": confidence,
            "urgency": urgency,
            "summary": summarize(safe_message),
            "actions": actions,
        }
        return output, AgentTrace(
            agent=self.name,
            purpose="Understand and route the customer request.",
            tools=["ticket.classify", "ticket.assess_urgency", "ticket.summarize"],
            output=output,
        )


class PolicyAgent:
    name = "Policy Agent"

    def run(self, category: str) -> tuple[dict[str, Any], AgentTrace]:
        policy = lookup_policy(category)
        return policy, AgentTrace(
            agent=self.name,
            purpose="Ground recommendations in an explicit support policy.",
            tools=["policy.lookup"],
            output=policy,
        )


class ResponseAgent:
    name = "Response Agent"

    def run(
        self,
        category: str,
        urgency: str,
        security_status: str,
        policy: dict[str, Any],
    ) -> tuple[str, AgentTrace]:
        response = response_template(category, urgency)
        if security_status == "blocked_for_review":
            response += (
                " For safety, the message was sanitized and no automated account "
                "action was taken."
            )
        trace = AgentTrace(
            agent=self.name,
            purpose="Draft a helpful response within policy boundaries.",
            tools=["response.template"],
            output={
                "draft_created": True,
                "policy_used": policy["policy"],
                "automated_account_action": False,
            },
        )
        return response, trace

