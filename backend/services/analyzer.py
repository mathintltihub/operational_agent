"""
Local ticket analyzer - uses keyword matching only, no Gemini API calls.
Fast, free, and works offline.
"""
import uuid
from datetime import datetime


class LocalTicketAnalyzer:
    """Analyzes IT support tickets using keyword-based rules only."""

    def analyze(self, title: str, description: str) -> dict:
        """Analyze ticket using local keyword matching."""
        combined = (title + " " + description).lower()
        
        # Detect issue type
        issue_type = self._detect_issue_type(combined)
        
        # Detect priority
        priority = self._detect_priority(combined)
        
        # Get impacted area
        impacted_area = self._get_impacted_area(issue_type)
        
        # Get recommended team
        recommended_team = self._get_team(issue_type)
        
        # Get troubleshooting steps
        troubleshooting_steps = self._get_troubleshooting_steps(issue_type)
        
        # Calculate confidence
        confidence_score = self._calculate_confidence(combined, issue_type)
        
        # Generate reasoning
        reasoning_summary = self._generate_reasoning(issue_type, priority, confidence_score)
        
        return {
            "ticket_id": f"ticket-{uuid.uuid4().hex[:8]}",
            "issue_type": issue_type,
            "priority": priority,
            "impacted_area": impacted_area,
            "recommended_team": recommended_team,
            "troubleshooting_steps": troubleshooting_steps,
            "confidence_score": confidence_score,
            "reasoning_summary": reasoning_summary,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _detect_issue_type(self, text: str) -> str:
        """Detect issue type from keywords."""
        
        # Database keywords
        if any(kw in text for kw in [
            "database", "db ", "postgres", "mysql", "sql", "oracle",
            "timeout", "connection refused", "replication", "query",
            "table", "index", "deadlock", "transaction"
        ]):
            return "database"
        
        # Network keywords
        if any(kw in text for kw in [
            "network", "vpn", "connectivity", "latency", "dns",
            "firewall", "packet", "ip", "ping", "traceroute",
            "router", "switch", "gateway", "subnet", "port"
        ]):
            return "network"
        
        # Server keywords
        if any(kw in text for kw in [
            "server", "cpu", "memory", "disk", "unreachable",
            "vm", "host", "ssh", "linux", "windows", "reboot",
            "hardware", "ram", "storage", "filesystem"
        ]):
            return "server"
        
        # Application keywords
        if any(kw in text for kw in [
            "app", "application", "http 500", "crash", "error",
            "deployment", "service unavailable", "api", "endpoint",
            "web", "website", "page", "load", "response"
        ]):
            return "application"
        
        # Access/request keywords
        if any(kw in text for kw in [
            "password", "access", "permission", "login", "sudo",
            "admin", "role", "user", "account", "reset", "unlock"
        ]):
            return "access/request"
        
        return "unknown"

    def _detect_priority(self, text: str) -> str:
        """Detect priority level from keywords."""
        
        # Critical indicators
        if any(kw in text for kw in [
            "critical", "outage", "production down", "all users",
            "core service", "unreachable", "complete failure",
            "emergency", "urgent", "immediately"
        ]):
            return "critical"
        
        # High priority indicators
        if any(kw in text for kw in [
            "high", "major", "urgent", "many users", "500 error",
            "crash", "broken", "not working", "failed", "down"
        ]):
            return "high"
        
        # Low priority indicators
        if any(kw in text for kw in [
            "low", "minor", "informational", "request", "question",
            "enhancement", "feature", "nice to have"
        ]):
            return "low"
        
        # Default to medium
        return "medium"

    def _get_impacted_area(self, issue_type: str) -> str:
        """Get impacted area based on issue type."""
        mapping = {
            "database": "Database connectivity and performance",
            "network": "Network connectivity and infrastructure",
            "server": "Server infrastructure and resources",
            "application": "Application services and functionality",
            "access/request": "User access and permissions",
            "unknown": "Unclear - requires manual review"
        }
        return mapping.get(issue_type, "Unknown")

    def _get_team(self, issue_type: str) -> str:
        """Get recommended team based on issue type."""
        mapping = {
            "database": "Database Team",
            "network": "Network Team",
            "server": "Server Team",
            "application": "Application Support",
            "access/request": "Service Desk",
            "unknown": "Manual Review"
        }
        return mapping.get(issue_type, "Manual Review")

    def _get_troubleshooting_steps(self, issue_type: str) -> list:
        """Get troubleshooting steps based on issue type."""
        
        steps = {
            "database": [
                "Check database server status and availability",
                "Verify network connectivity to database host",
                "Review database connection pool settings",
                "Check database logs for errors or warnings",
                "Verify database credentials and permissions"
            ],
            "network": [
                "Test network connectivity with ping/traceroute",
                "Verify VPN connection status",
                "Check firewall rules and security groups",
                "Test DNS resolution",
                "Review network logs for anomalies"
            ],
            "server": [
                "Check server availability and ping response",
                "Review CPU, memory, and disk usage metrics",
                "Check system logs for errors",
                "Verify SSH/RDP access",
                "Review recent system changes or updates"
            ],
            "application": [
                "Check application logs for error messages",
                "Verify application service status",
                "Test application endpoints manually",
                "Review recent deployments or code changes",
                "Check application dependencies and integrations"
            ],
            "access/request": [
                "Verify user identity and employee status",
                "Check existing access permissions",
                "Confirm manager approval if required",
                "Process request through proper channels",
                "Document access grant in audit log"
            ],
            "unknown": [
                "Request more detailed information from user",
                "Ask for specific error messages or screenshots",
                "Clarify the scope and impact of the issue",
                "Escalate to team lead for manual review"
            ]
        }
        
        return steps.get(issue_type, steps["unknown"])

    def _calculate_confidence(self, text: str, issue_type: str) -> float:
        """Calculate confidence score based on keyword strength."""
        
        if issue_type == "unknown":
            return 0.35
        
        # Count strong indicators
        strong_keywords = 0
        if "error" in text or "failed" in text or "cannot" in text:
            strong_keywords += 1
        if "timeout" in text or "refused" in text or "unavailable" in text:
            strong_keywords += 1
        if any(num in text for num in ["500", "404", "503", "502"]):
            strong_keywords += 1
        
        # Base confidence
        confidence = 0.75
        
        # Boost for strong keywords
        confidence += strong_keywords * 0.05
        
        # Cap at 0.95
        return min(confidence, 0.95)

    def _generate_reasoning(self, issue_type: str, priority: str, confidence: float) -> str:
        """Generate reasoning summary."""
        
        if issue_type == "unknown":
            return "The ticket lacks specific technical details, making accurate classification difficult. Routed to Manual Review for human assessment."
        
        return f"Classified as {issue_type} issue with {priority} priority based on keyword analysis. Confidence: {int(confidence * 100)}%."


# Singleton instance
analyzer = LocalTicketAnalyzer()
