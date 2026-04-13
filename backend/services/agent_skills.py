"""
Operations triage skill engine.

This module provides deterministic triage behavior that is used as:
1) fallback when Ollama is unavailable, and
2) baseline that safe LLM fields can refine.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Tuple

from backend.services.analyzer import analyzer


ISSUE_KEYWORDS = {
    "security": [
        "security", "breach", "malware", "phishing", "ransomware", "suspicious",
        "unauthorized", "attack", "intrusion", "failed login", "brute force",
        "credential stuffing", "siem", "soc alert",
    ],
    "database": [
        "database", "db ", "postgres", "mysql", "sql", "oracle", "connection refused",
        "replication", "deadlock", "transaction", "query", "latency", "timeout",
    ],
    "network": [
        "network", "vpn", "connectivity", "latency", "dns", "firewall",
        "packet loss", "gateway", "router", "switch", "subnet", "port",
    ],
    "server": [
        "server", "host", "vm", "node", "instance", "cpu", "memory", "disk",
        "filesystem", "ssh", "rdp", "unreachable", "kernel", "reboot",
    ],
    "application": [
        "application", "app", "http 500", "500", "503", "service unavailable",
        "api", "endpoint", "crash", "exception", "deployment", "rollback",
    ],
    "access/request": [
        "access", "permission", "login", "password", "reset", "unlock", "account",
        "role", "admin", "mfa", "sudo",
    ],
}

TEAM_BY_ISSUE = {
    "security": "Security Operations",
    "database": "Database Reliability Team",
    "network": "Network Operations Team",
    "server": "Server Operations Team",
    "application": "Application Support Team",
    "access/request": "Service Desk",
    "unknown": "Manual Review Queue",
}

AREA_BY_ISSUE = {
    "security": "Identity and security controls",
    "database": "Database availability and performance",
    "network": "Connectivity and network infrastructure",
    "server": "Compute infrastructure and host resources",
    "application": "Application service health",
    "access/request": "User identity and access management",
    "unknown": "Unclear impact, needs clarification",
}

SAFE_STEPS_BY_ISSUE = {
    "security": [
        "Confirm whether suspicious activity is still active before taking action.",
        "Collect auth, VPN, and endpoint logs with timestamps for investigation.",
        "Contain affected identities or sessions based on incident response policy.",
        "Escalate immediately to Security Operations with evidence and impact scope.",
    ],
    "database": [
        "Verify database instance health and replication status.",
        "Check connection pool pressure and query latency metrics.",
        "Review recent schema, config, and deployment changes.",
        "Escalate with slow query samples and error logs if impact is broad.",
    ],
    "network": [
        "Validate DNS, routing, and VPN status from multiple vantage points.",
        "Check firewall and security group changes within the incident window.",
        "Measure packet loss and latency to isolate affected segments.",
        "Escalate with traceroute, ping, and impacted-user counts.",
    ],
    "server": [
        "Confirm host availability and infrastructure health from monitoring tools.",
        "Check CPU, memory, and disk saturation before performing restart actions.",
        "Review recent OS, kernel, or configuration changes.",
        "Escalate with host logs and impact scope if service remains unstable.",
    ],
    "application": [
        "Check service health checks and error-rate dashboards.",
        "Review application logs for stack traces and dependency failures.",
        "Correlate with recent deploys, config changes, or feature flags.",
        "Escalate with request IDs, error signatures, and user impact details.",
    ],
    "access/request": [
        "Validate requester identity and approval path before privilege changes.",
        "Verify current role mappings and least-privilege requirements.",
        "Apply access change via approved IAM workflow with audit trail.",
        "Confirm user access after change and document the ticket outcome.",
    ],
    "unknown": [
        "Collect error message, timeline, and affected systems before routing.",
        "Ask for impact scope: number of users, environments, and services.",
        "Request logs or screenshots to reduce ambiguity.",
        "Route to Manual Review if classification remains unclear.",
    ],
}

CRITICAL_SIGNALS = (
    "all users", "entire team", "production down", "sev1", "outage", "widespread",
    "payment failure", "data loss", "cannot access", "critical",
)
HIGH_SIGNALS = (
    "many users", "major", "urgent", "high priority", "degraded", "slow",
    "500", "503", "timeout", "service unavailable",
)
LOW_SIGNALS = (
    "question", "minor", "low priority", "feature request", "nice to have",
)

RISKY_ACTION_HINTS = (
    "delete", "drop", "truncate", "disable security", "turn off firewall", "force reboot",
)


def _keyword_hits(text: str, keywords: List[str]) -> int:
    return sum(1 for keyword in keywords if keyword in text)


def classify_issue(text: str) -> str:
    """Classify issue type with weighted keyword scoring."""
    normalized = text.lower()
    scores = {issue: _keyword_hits(normalized, kws) for issue, kws in ISSUE_KEYWORDS.items()}

    top_issue = max(scores, key=scores.get)
    if scores[top_issue] == 0:
        return analyzer._detect_issue_type(normalized)
    return top_issue


def detect_priority(text: str) -> str:
    """Detect priority with impact-sensitive heuristics."""
    normalized = text.lower()
    critical_hits = _keyword_hits(normalized, list(CRITICAL_SIGNALS))
    high_hits = _keyword_hits(normalized, list(HIGH_SIGNALS))
    low_hits = _keyword_hits(normalized, list(LOW_SIGNALS))

    if critical_hits >= 1:
        return "critical"
    if high_hits >= 2:
        return "high"
    if high_hits == 1 and "production" in normalized:
        return "high"
    if low_hits >= 1 and high_hits == 0:
        return "low"
    return analyzer._detect_priority(normalized)


def get_impacted_area(issue_type: str) -> str:
    return AREA_BY_ISSUE.get(issue_type, AREA_BY_ISSUE["unknown"])


def route_to_team(issue_type: str) -> str:
    return TEAM_BY_ISSUE.get(issue_type, TEAM_BY_ISSUE["unknown"])


def suggest_solution(issue_type: str) -> list[str]:
    return SAFE_STEPS_BY_ISSUE.get(issue_type, SAFE_STEPS_BY_ISSUE["unknown"])


def _safety_notice(text: str) -> str:
    normalized = text.lower()
    if any(hint in normalized for hint in RISKY_ACTION_HINTS):
        return (
            "Potentially destructive action detected in request context. "
            "Perform change approval and backup validation before execution."
        )
    return "Use change-control and verification steps before making production-impacting changes."


def calculate_confidence(text: str, issue_type: str) -> float:
    """Confidence score from signal strength and context quality."""
    normalized = text.lower()
    if issue_type == "unknown":
        return 0.35

    issue_signal_hits = _keyword_hits(normalized, ISSUE_KEYWORDS.get(issue_type, []))
    detail_hits = 0
    if any(token in normalized for token in ["error", "code", "exception", "timeout", "failed"]):
        detail_hits += 1
    if any(token in normalized for token in ["users", "production", "environment", "service"]):
        detail_hits += 1
    if any(token in normalized for token in ["since", "started", "after", "recent"]):
        detail_hits += 1

    base = 0.55 + min(issue_signal_hits * 0.07, 0.21) + (detail_hits * 0.05)
    return min(max(base, 0.35), 0.95)


def confidence_to_level(score: float) -> str:
    if score >= 0.8:
        return "high"
    if score >= 0.55:
        return "medium"
    return "low"


def _build_reasoning(issue_type: str, priority: str, score: float, text: str) -> str:
    normalized = text.lower()
    signals: List[str] = []
    for keyword in ISSUE_KEYWORDS.get(issue_type, []):
        if keyword in normalized:
            signals.append(keyword)
        if len(signals) >= 3:
            break

    signal_text = ", ".join(signals) if signals else "general incident indicators"
    return (
        f"Classified as {issue_type} with {priority} priority from signals: {signal_text}. "
        f"Confidence is {int(score * 100)}%."
    )


def _classification_signals(text: str, issue_type: str) -> List[str]:
    normalized = text.lower()
    return [kw for kw in ISSUE_KEYWORDS.get(issue_type, []) if kw in normalized][:6]


def _priority_signals(text: str, priority: str) -> List[str]:
    normalized = text.lower()
    source = CRITICAL_SIGNALS if priority == "critical" else HIGH_SIGNALS if priority == "high" else LOW_SIGNALS
    return [kw for kw in source if kw in normalized][:6]


def execute_skills(text: str) -> dict:
    """Run deterministic triage and return backend contract with audit data."""
    issue_type = classify_issue(text)
    priority = detect_priority(text)
    confidence_score = calculate_confidence(text, issue_type)
    confidence_level = confidence_to_level(confidence_score)

    return {
        "issue_type": issue_type,
        "priority": priority,
        "assigned_team": route_to_team(issue_type),
        "impacted_area": get_impacted_area(issue_type),
        "analysis": _build_reasoning(issue_type, priority, confidence_score, text),
        "solution_steps": suggest_solution(issue_type),
        "confidence": confidence_level,
        "confidence_score": confidence_score,
        "timestamp": datetime.utcnow().isoformat(),
        "audit": {
            "inference_source": "deterministic_skills",
            "confidence_level": confidence_level,
            "classification_signals": _classification_signals(text, issue_type),
            "priority_signals": _priority_signals(text, priority),
            "safety_notice": _safety_notice(text),
        },
    }
