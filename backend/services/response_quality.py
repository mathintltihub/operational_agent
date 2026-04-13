"""
Validation and normalization helpers for LLM ticket payloads.
"""
from __future__ import annotations

import re
from typing import Optional


VALID_ISSUE_TYPES = {"server", "network", "database", "application", "access/request", "security", "unknown"}
VALID_PRIORITIES = {"critical", "high", "medium", "low"}
VALID_CONFIDENCE = {"high", "medium", "low"}
ISSUE_TYPE_ALIASES = {
    "access": "access/request",
    "access request": "access/request",
    "access-request": "access/request",
}


def is_weak_text(value: str) -> bool:
    """Detect placeholder-style or unusable LLM text."""
    if not isinstance(value, str):
        return True
    normalized = value.strip().lower()
    if not normalized:
        return True
    if normalized in {"...", "..", ".", "n/a", "na", "none", "null", "tbd", "unknown"}:
        return True
    if re.fullmatch(r"step\s*\d+", normalized):
        return True
    return False


def normalize_issue_type(value: str) -> Optional[str]:
    """Normalize and validate issue type values from the LLM."""
    if is_weak_text(value):
        return None
    normalized = value.strip().lower().replace("_", " ").replace("-", " ")
    if "|" in normalized:
        normalized = normalized.split("|", 1)[0].strip()
    normalized = ISSUE_TYPE_ALIASES.get(normalized, normalized)
    normalized = normalized.replace(" ", "/") if normalized == "access request" else normalized
    return normalized if normalized in VALID_ISSUE_TYPES else None


def normalize_priority(value: str) -> Optional[str]:
    """Normalize and validate priority values from the LLM."""
    if is_weak_text(value):
        return None
    normalized = value.strip().lower()
    return normalized if normalized in VALID_PRIORITIES else None


def normalize_confidence(value: str) -> Optional[str]:
    """Normalize confidence labels from the LLM."""
    if is_weak_text(value):
        return None
    normalized = value.strip().lower()
    return normalized if normalized in VALID_CONFIDENCE else None


def clean_solution_steps(steps) -> list[str]:
    """Keep only meaningful troubleshooting steps."""
    if not isinstance(steps, list):
        return []
    cleaned = []
    for item in steps:
        if not isinstance(item, str):
            continue
        step = re.sub(r"^\s*\d+[\).\-\s]*", "", item).strip()
        if is_weak_text(step):
            continue
        if len(step) < 8:
            continue
        cleaned.append(step)
    return cleaned


def merge_llm_ticket_into_result(llm_result: dict, result: dict) -> dict:
    """Merge safe LLM fields into a skill-based ticket result."""
    merged = dict(result)

    llm_issue_type = normalize_issue_type(llm_result.get("issue_type", ""))
    if llm_issue_type and llm_issue_type != "unknown":
        merged["issue_type"] = llm_issue_type

    llm_priority = normalize_priority(llm_result.get("priority", ""))
    if llm_priority:
        merged["priority"] = llm_priority

    team = llm_result.get("assigned_team", "")
    if not is_weak_text(team):
        merged["assigned_team"] = team.strip()

    impacted_area = llm_result.get("impacted_area", "")
    if not is_weak_text(impacted_area):
        merged["impacted_area"] = impacted_area.strip()

    analysis = llm_result.get("analysis", "")
    if not is_weak_text(analysis):
        merged["analysis"] = analysis.strip()

    cleaned_steps = clean_solution_steps(llm_result.get("solution_steps"))
    if cleaned_steps:
        merged["solution_steps"] = cleaned_steps

    conf_level = normalize_confidence(llm_result.get("confidence", ""))
    if conf_level:
        merged["confidence"] = conf_level
        merged["confidence_score"] = 0.85 if conf_level == "high" else 0.6 if conf_level == "medium" else 0.4

    return merged
