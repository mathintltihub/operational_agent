"""
Policy utilities for scope control and chat prompt shaping.
"""
from __future__ import annotations

import re


ALLOWED_CONVERSATION_PATTERNS = (
    r"\bhello\b",
    r"\bhi\b",
    r"\bhey\b",
    r"\bthanks?\b",
    r"\bthank you\b",
    r"\bwhat is your name\b",
    r"\bwho are you\b",
    r"\bwhat can you do\b",
    r"\bhelp\b",
    r"\bhow does this work\b",
    r"\bhow do i use you\b",
    r"\bstatus\b",
    r"\bare you online\b",
    r"\bare you working\b",
)

OPERATIONS_KEYWORDS = (
    "ticket", "incident", "outage", "production", "server", "network",
    "database", "application", "access", "permission", "login", "password",
    "vpn", "dns", "latency", "firewall", "cpu", "memory", "disk",
    "error", "http 500", "500", "503", "timeout", "ssh", "api",
    "deployment", "service", "alert", "replication", "security",
    "breach", "support", "troubleshoot", "triage", "team", "assign",
    "degraded", "down", "slow", "unreachable", "reset", "iam", "auth",
)


CHAT_SYSTEM_PROMPT = """You are Operations Agent, an IT operations triage copilot running on a local Ollama model.

You must respond with ONLY valid JSON and choose exactly one mode:

1) For in-scope assistant conversation (greetings, capabilities, how-to-use, status):
{
  "mode": "conversation",
  "reply": "short natural response"
}

2) For IT support incidents, requests, or triage tasks:
{
  "mode": "ticket",
  "issue_type": "server|network|database|application|access/request|security|unknown",
  "priority": "critical|high|medium|low",
  "assigned_team": "...",
  "impacted_area": "...",
  "analysis": "...",
  "solution_steps": ["step1", "step2"],
  "confidence": "high|medium|low"
}

3) For out-of-scope requests:
{
  "mode": "out_of_scope",
  "reply": "short refusal plus IT-operations redirect"
}

Rules:
- Never produce markdown fences.
- Never produce extra text outside JSON.
- Use "ticket" only for IT operations matters.
- For unsafe requests, avoid dangerous actions and recommend verification/escalation.
"""


def is_operations_related_message(message: str) -> bool:
    """Heuristic guardrail to keep the assistant scoped to IT operations."""
    normalized = message.lower()
    if any(re.search(pattern, normalized) for pattern in ALLOWED_CONVERSATION_PATTERNS):
        return True
    return any(keyword in normalized for keyword in OPERATIONS_KEYWORDS)


def build_out_of_scope_reply() -> str:
    """Short domain restriction response for non-operations prompts."""
    return (
        "I'm Operations Agent, focused on IT operations triage only. "
        "I can help with incidents, outages, access requests, priority detection, team routing, "
        "and safe troubleshooting guidance. Share an IT issue and I will assist."
    )
