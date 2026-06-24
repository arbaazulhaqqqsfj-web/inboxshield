# InboxShield — 4:30 video script and shot list

Target length: **4 minutes 30 seconds**. Do not exceed five minutes.

## 0:00–0:25 — Hook

**On screen:** Title card, then the InboxShield home page.

**Say:**

“Customer-support inboxes contain more than questions. They contain urgent
incidents, personal data, and sometimes malicious instructions aimed at AI
systems. InboxShield is a privacy-first multi-agent system that helps support
teams move quickly without giving untrusted messages control.”

## 0:25–0:55 — Problem and value

**On screen:** Slowly pan across the four-step workflow.

**Say:**

“A single all-powerful support bot creates unnecessary risk. InboxShield splits
the workflow into four narrow agents: Security, Intake, Policy, and Response.
It protects sensitive data, prioritizes the ticket, grounds recommendations in
policy, and keeps irreversible actions behind human approval.”

## 0:55–1:35 — Architecture

**On screen:** Show the architecture diagram from the README.

**Say:**

“The sequence is the main security feature. The Security Agent is the only
component that receives raw customer text. It redacts personal data and detects
prompt injection. Only the sanitized message reaches the Intake Agent. The
Policy Agent calls a bounded MCP tool, and the Response Agent drafts within
that policy. The orchestrator combines the evidence and decides whether a human
must review the case.”

## 1:35–2:50 — Live adversarial demo

**On screen:** Click **Load risky example**, then **Run secure triage**.

**Say while the example is visible:**

“This ticket includes three hazards: an instruction to ignore previous rules, a
payment-card number, and an email address. I’ll submit it exactly as received.”

**After results appear:**

“InboxShield flags prompt injection as high risk. The card and email are
removed before downstream processing. It still recognizes the legitimate
billing intent, marks the case for human review, chooses Billing Operations,
and drafts a response that explicitly says no automated account action was
taken.”

**On screen:** Scroll through Security Gate, Safe Message, Suggested Response,
and Required Actions.

## 2:50–3:30 — Auditability and tools

**On screen:** Expand **View agent audit trail**.

**Say:**

“Every decision is inspectable. The trace shows each agent’s purpose, the skill
or tool it used, and its structured output. The project also includes an
MCP-compatible JSON-RPC server exposing security scan, ticket classification,
and policy lookup tools. This keeps business capabilities narrow and
discoverable.”

## 3:30–4:05 — Engineering quality

**On screen:** Show the repository tree, tests, Dockerfile, and README.

**Say:**

“InboxShield runs with the Python standard library, has no paid API dependency,
ships with Docker deployment, a health endpoint, secure HTTP headers, and
automated tests for redaction, injection defense, routing, escalation, policy
boundaries, and MCP calls. This makes the judging experience reproducible.”

## 4:05–4:30 — Close

**On screen:** Return to the top of the app.

**Say:**

“InboxShield’s principle is simple: no secrets, no silent actions, and full
traceability. It does not replace support people. It gives them a safer,
prioritized, policy-grounded place to start. Every ticket understood; every
action controlled.”

## Recording checklist

- Record at 1080p.
- Increase browser zoom to make text readable.
- Hide bookmarks, notifications, usernames, and unrelated tabs.
- Never show API keys or private repository information.
- Speak slightly slower than normal.
- Export at 1080p H.264.
- Upload to YouTube as **Public** or **Unlisted**, not Private.
- Confirm the final duration is under five minutes.

