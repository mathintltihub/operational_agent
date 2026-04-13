"""
Skill-based ticket analysis helpers used by the FastAPI backend.

These helpers provide deterministic classification and a stable fallback
whenever Ollama is unavailable or returns an unusable response.
"""
from __future__ import annotations

from datetime import datetime

from backend.services.analyzer import analyzer


SECURITY_KEYWORDS = (
    "security",
    "breach",
    "malware",
    "phishing",
    "ransomware",
    "suspicious",
    "unauthorized",
    "attack",
    "intrusion",
    "failed login",
    "failed logins",
    "brute force",
    "vpn gateway",
)


def classify_issue(text: str) -> str:
    """Classify the ticket into a supported issue type."""
    normalized = text.lower()

    if any(keyword in normalized for keyword in SECURITY_KEYWORDS):
        return "security"

    return analyzer._detect_issue_type(normalized)


def detect_priority(text: str) -> str:
    """Determine ticket priority from the issue description."""
    return analyzer._detect_priority(text.lower())


def get_impacted_area(issue_type: str) -> str:
    """Return a user-facing impacted area string."""
    if issue_type == "security":
        return "Security posture and access integrity"
    return analyzer._get_impacted_area(issue_type)


def route_to_team(issue_type: str) -> str:
    """Return the team that should handle the issue."""
    if issue_type == "security":
        return "Security Team"
    return analyzer._get_team(issue_type)


def suggest_solution(issue_type: str) -> list[str]:
    """Return troubleshooting or next-step guidance."""
    if issue_type == "security":
        return [
            "Validate whether the activity is still in progress",
            "Review authentication and VPN logs for source IPs and affected accounts",
            "Temporarily block or rate-limit suspicious IP addresses if policy allows",
            "Force password resets or MFA checks for impacted accounts",
            "Escalate to the Security Team for investigation and containment",
        ]
    return analyzer._get_troubleshooting_steps(issue_type)


def calculate_confidence(text: str, issue_type: str) -> float:
    """Calculate a normalized confidence score."""
    if issue_type == "security":
        normalized = text.lower()
        matches = sum(1 for keyword in SECURITY_KEYWORDS if keyword in normalized)
        return min(0.7 + (matches * 0.04), 0.95)

    return analyzer._calculate_confidence(text.lower(), issue_type)


def confidence_to_level(score: float) -> str:
    """Convert numeric confidence to a simple label."""
    if score >= 0.8:
        return "high"
    if score >= 0.55:
        return "medium"
    return "low"


def execute_skills(text: str) -> dict:
    """Run the local analysis pipeline and return the backend contract."""
    issue_type = classify_issue(text)
    priority = detect_priority(text)
    confidence_score = calculate_confidence(text, issue_type)

    return {
        "issue_type": issue_type,
        "priority": priority,
        "assigned_team": route_to_team(issue_type),
        "impacted_area": get_impacted_area(issue_type),
        "analysis": analyzer._generate_reasoning(issue_type, priority, confidence_score),
        "solution_steps": suggest_solution(issue_type),
        "confidence": confidence_to_level(confidence_score),
        "confidence_score": confidence_score,
        "timestamp": datetime.utcnow().isoformat(),
    }
