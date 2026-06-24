"""Small MCP-compatible JSON-RPC tool server over standard input/output.

This implements the MCP operations needed for the demo: initialize,
tools/list, and tools/call. It keeps the tool boundary visible and testable
without adding a third-party dependency.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from .security import scan_and_redact
from .skills import classify_ticket, lookup_policy


TOOLS = [
    {
        "name": "policy_lookup",
        "description": "Return the approved support policy for a ticket category.",
        "inputSchema": {
            "type": "object",
            "properties": {"category": {"type": "string"}},
            "required": ["category"],
        },
    },
    {
        "name": "security_scan",
        "description": "Redact PII and detect prompt-injection signals.",
        "inputSchema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
    {
        "name": "ticket_classify",
        "description": "Classify and route a customer-support ticket.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subject": {"type": "string"},
                "message": {"type": "string"},
            },
            "required": ["subject", "message"],
        },
    },
]


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "policy_lookup":
        result = lookup_policy(str(arguments.get("category", "general")))
    elif name == "security_scan":
        redacted, findings = scan_and_redact(str(arguments.get("text", "")))
        result = {
            "redacted": redacted,
            "findings": [
                {
                    "kind": finding.kind,
                    "severity": finding.severity,
                    "explanation": finding.explanation,
                }
                for finding in findings
            ],
        }
    elif name == "ticket_classify":
        category, queue, confidence = classify_ticket(
            str(arguments.get("subject", "")),
            str(arguments.get("message", "")),
        )
        result = {"category": category, "queue": queue, "confidence": confidence}
    else:
        raise ValueError(f"Unknown tool: {name}")
    return {"content": [{"type": "text", "text": json.dumps(result)}]}


def handle(request: dict[str, Any]) -> dict[str, Any] | None:
    method = request.get("method")
    request_id = request.get("id")
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        result = {
            "protocolVersion": "2025-03-26",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "inboxshield-tools", "version": "1.0.0"},
        }
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        params = request.get("params", {})
        result = call_tool(params.get("name", ""), params.get("arguments", {}))
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def main() -> None:
    for line in sys.stdin:
        try:
            request = json.loads(line)
            response = handle(request)
            if response is not None:
                print(json.dumps(response), flush=True)
        except Exception as exc:  # Never leak a stack trace across the tool boundary.
            print(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32000, "message": str(exc)},
                    }
                ),
                flush=True,
            )


if __name__ == "__main__":
    main()

