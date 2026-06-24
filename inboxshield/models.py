"""Typed domain models shared by InboxShield agents."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class Ticket:
    subject: str
    message: str
    customer_tier: str = "standard"
    channel: str = "email"


@dataclass(slots=True)
class SecurityFinding:
    kind: str
    severity: str
    explanation: str
    count: int = 1


@dataclass(slots=True)
class AgentTrace:
    agent: str
    purpose: str
    output: dict[str, Any]
    tools: list[str] = field(default_factory=list)


@dataclass(slots=True)
class TriageResult:
    category: str
    urgency: str
    confidence: float
    summary: str
    recommended_queue: str
    required_actions: list[str]
    draft_response: str
    redacted_message: str
    security_status: str
    security_findings: list[SecurityFinding]
    human_review_required: bool
    traces: list[AgentTrace]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

