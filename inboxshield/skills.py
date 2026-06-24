"""Reusable agent skills.

Each skill has one narrow responsibility and can be called by an agent or
exposed as a tool through the MCP-compatible JSON-RPC server.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CategoryRule:
    name: str
    queue: str
    keywords: tuple[str, ...]


CATEGORY_RULES = (
    CategoryRule(
        "billing",
        "Billing Operations",
        ("charged", "charge", "invoice", "refund", "payment", "billing", "card"),
    ),
    CategoryRule(
        "account_access",
        "Identity & Access",
        ("login", "password", "locked", "account", "sign in", "2fa", "hacked"),
    ),
    CategoryRule(
        "technical",
        "Technical Support",
        ("error", "bug", "broken", "crash", "failed", "not working", "outage"),
    ),
    CategoryRule(
        "cancellation",
        "Retention",
        ("cancel", "close my account", "unsubscribe", "terminate"),
    ),
    CategoryRule(
        "feedback",
        "Customer Experience",
        ("suggestion", "feedback", "feature request", "love", "improve"),
    ),
)

URGENT_WORDS = (
    "fraud",
    "stolen",
    "hacked",
    "security breach",
    "charged twice",
    "double charged",
    "outage",
    "cannot access",
    "locked out",
)

EMERGENCY_WORDS = ("suicide", "kill myself", "immediate danger", "medical emergency")


def classify_ticket(subject: str, message: str) -> tuple[str, str, float]:
    text = f"{subject} {message}".lower()
    scores = {
        rule.name: sum(1 for keyword in rule.keywords if keyword in text)
        for rule in CATEGORY_RULES
    }
    category = max(scores, key=scores.get)
    score = scores[category]
    if score == 0:
        return "general", "General Support", 0.55
    rule = next(item for item in CATEGORY_RULES if item.name == category)
    confidence = min(0.97, 0.62 + score * 0.09)
    return category, rule.queue, confidence


def assess_urgency(message: str, customer_tier: str) -> tuple[str, list[str]]:
    text = message.lower()
    actions: list[str] = []
    if any(word in text for word in EMERGENCY_WORDS):
        return "critical", [
            "Immediately escalate to a trained human responder.",
            "Do not attempt to resolve a safety emergency automatically.",
        ]
    matched = [word for word in URGENT_WORDS if word in text]
    if matched:
        actions.append(f"Prioritize due to risk signal: {matched[0]}.")
        actions.append("Request human review before any account-changing action.")
        return "high", actions
    if customer_tier.lower() in {"enterprise", "priority"}:
        return "medium", ["Apply priority-customer response target."]
    return "normal", ["Process through the standard support workflow."]


def summarize(message: str, max_length: int = 170) -> str:
    clean = re.sub(r"\s+", " ", message).strip()
    if len(clean) <= max_length:
        return clean
    return clean[: max_length - 1].rstrip() + "…"


def lookup_policy(category: str) -> dict[str, object]:
    policies: dict[str, dict[str, object]] = {
        "billing": {
            "policy": "Verify the transaction and account owner before refunding.",
            "allowed": ["explain charges", "open billing investigation"],
            "requires_human": ["issue refund", "change payment method"],
        },
        "account_access": {
            "policy": "Never request passwords or authentication codes.",
            "allowed": ["send official recovery guidance", "open identity review"],
            "requires_human": ["disable security controls", "change account owner"],
        },
        "technical": {
            "policy": "Collect minimum reproducible details without collecting secrets.",
            "allowed": ["share troubleshooting steps", "open engineering ticket"],
            "requires_human": ["access customer environment"],
        },
        "cancellation": {
            "policy": "Explain consequences and require explicit confirmation.",
            "allowed": ["share cancellation steps", "offer plan comparison"],
            "requires_human": ["cancel account", "delete retained data"],
        },
        "feedback": {
            "policy": "Thank the customer and avoid promising delivery dates.",
            "allowed": ["record feedback", "link existing roadmap item"],
            "requires_human": ["make contractual commitment"],
        },
        "general": {
            "policy": "Clarify the request and collect only necessary information.",
            "allowed": ["ask a clarifying question", "route to general support"],
            "requires_human": ["perform irreversible action"],
        },
    }
    return policies.get(category, policies["general"])


def response_template(category: str, urgency: str) -> str:
    openings = {
        "billing": "Thanks for flagging this billing issue.",
        "account_access": "I’m sorry you’re having trouble accessing your account.",
        "technical": "Thanks for reporting this technical problem.",
        "cancellation": "I understand you’d like help with your account or subscription.",
        "feedback": "Thank you for taking the time to share this feedback.",
        "general": "Thanks for contacting our support team.",
    }
    next_steps = {
        "billing": "We’ve opened a billing review. Please do not send full card details.",
        "account_access": (
            "Please use the official account-recovery page. We will never ask for "
            "your password or one-time authentication code."
        ),
        "technical": (
            "We’ve routed this to technical support. If possible, reply with the "
            "time of the issue and the steps that produced it—without including secrets."
        ),
        "cancellation": (
            "A support specialist will confirm the available options and any effects "
            "on your stored data before changes are made."
        ),
        "feedback": "We’ve recorded your suggestion for the product team to review.",
        "general": "A support specialist will review your request and follow up.",
    }
    urgency_note = (
        " We’ve marked this as high priority for human review."
        if urgency in {"high", "critical"}
        else ""
    )
    return f"{openings.get(category, openings['general'])} {next_steps.get(category, next_steps['general'])}{urgency_note}"

