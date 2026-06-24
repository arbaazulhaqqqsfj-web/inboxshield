"""Security controls for untrusted customer messages."""

from __future__ import annotations

import re

from .models import SecurityFinding


PII_PATTERNS: tuple[tuple[str, str, re.Pattern[str]], ...] = (
    (
        "email",
        "[REDACTED_EMAIL]",
        re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    ),
    (
        "card_number",
        "[REDACTED_CARD]",
        re.compile(r"(?<!\d)(?:\d[ -]*?){13,19}(?!\d)"),
    ),
    (
        "phone",
        "[REDACTED_PHONE]",
        re.compile(r"(?<!\d)(?:\+?\d[\d ()-]{7,}\d)(?!\d)"),
    ),
    (
        "api_key",
        "[REDACTED_SECRET]",
        re.compile(
            r"\b(?:sk-[A-Za-z0-9_-]{16,}|AIza[A-Za-z0-9_-]{20,}|"
            r"(?:api[_-]?key|password|secret)\s*[:=]\s*\S+)",
            re.I,
        ),
    ),
)

INJECTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"ignore (?:all |any )?(?:previous|prior|system) instructions", re.I),
    re.compile(r"reveal (?:the )?(?:system prompt|hidden instructions|secrets)", re.I),
    re.compile(r"(?:act|behave) as (?:a |an )?(?:admin|developer|system)", re.I),
    re.compile(r"do not follow (?:the )?(?:policy|rules|instructions)", re.I),
    re.compile(r"<\s*(?:system|assistant|developer)\s*>", re.I),
)


def scan_and_redact(text: str) -> tuple[str, list[SecurityFinding]]:
    """Redact common sensitive values and identify prompt-injection attempts."""
    redacted = text
    findings: list[SecurityFinding] = []

    for kind, replacement, pattern in PII_PATTERNS:
        redacted, count = pattern.subn(replacement, redacted)
        if count:
            findings.append(
                SecurityFinding(
                    kind=kind,
                    severity="medium" if kind != "api_key" else "high",
                    explanation=f"Removed {count} exposed {kind.replace('_', ' ')} value(s).",
                    count=count,
                )
            )

    injection_hits = sum(len(pattern.findall(text)) for pattern in INJECTION_PATTERNS)
    if injection_hits:
        findings.append(
            SecurityFinding(
                kind="prompt_injection",
                severity="high",
                explanation=(
                    "The message contains instructions aimed at overriding the agent. "
                    "They were treated as untrusted customer content."
                ),
                count=injection_hits,
            )
        )

    return redacted, findings


def contains_high_risk(findings: list[SecurityFinding]) -> bool:
    return any(finding.severity == "high" for finding in findings)
