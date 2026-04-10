"""
Ticket analyzer service using LangChain.
"""
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI


class TicketAnalyzer:
    """Analyzes IT support tickets using LangChain."""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.use_mock = not self.api_key
        self.prompt_template = self._load_prompt_template()

        if not self.use_mock:
            self.llm = ChatOpenAI(
                model="gpt-4",
                temperature=0.1,
                api_key=self.api_key
            )

    def _load_prompt_template(self) -> PromptTemplate:
        """Load the prompt template from file."""
        base_dir = Path(__file__).parent.parent
        prompt_file = base_dir / "prompts" / "operations_agent_prompt.txt"

        with open(prompt_file, 'r') as f:
            template = f.read()

        return PromptTemplate(
            template=template,
            input_variables=["title", "description"]
        )

    def analyze(self, title: str, description: str) -> dict:
        """
        Analyze a ticket and return structured results.

        Returns:
            dict with ticket analysis results
        """
        if self.use_mock:
            return self._mock_analyze(title, description)

        try:
            prompt = self.prompt_template.format(
                title=title,
                description=description
            )

            response = self.llm.invoke(prompt)
            content = response.content

            # Extract JSON from response
            result = self._parse_json_response(content)

            # Add metadata
            result["ticket_id"] = f"ticket-{uuid.uuid4().hex[:8]}"
            result["timestamp"] = datetime.utcnow().isoformat()

            return result

        except Exception as e:
            return self._fallback_analysis(title, description, str(e))

    def _parse_json_response(self, content: str) -> dict:
        """Parse JSON from LLM response."""
        import re

        # Try to find JSON in the response
        content = content.strip()

        # Handle potential markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            parts = content.split("```")
            if len(parts) >= 2:
                content = parts[1]
        elif content.startswith("```"):
            content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

        # Try to extract JSON object using regex
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            content = json_match.group(0)

        content = content.strip()

        # Clean up any remaining whitespace or newlines
        content = re.sub(r'^\s*\n+', '', content)
        content = re.sub(r'\n+\s*$', '', content)

        return json.loads(content)

    def _mock_analyze(self, title: str, description: str) -> dict:
        """
        Mock analysis when no API key is available.
        Uses keyword-based rules for demonstration.
        """
        title_lower = title.lower()
        desc_lower = description.lower()
        combined = title_lower + " " + desc_lower

        # Determine issue type based on keywords
        issue_type = "unknown"
        if any(kw in combined for kw in ["database", "db ", "postgres", "mysql", "sql", "timeout", "connection refused", "replication"]):
            issue_type = "database"
        elif any(kw in combined for kw in ["network", "vpn", "connectivity", "latency", "dns", "firewall", "packet", "ip"]):
            issue_type = "network"
        elif any(kw in combined for kw in ["server", "cpu", "memory", "disk", "unreachable", "vm", "host", "ssh", "ping"]):
            issue_type = "server"
        elif any(kw in combined for kw in ["app", "application", "http 500", "crash", "error", "deployment", "service unavailable"]):
            issue_type = "application"
        elif any(kw in combined for kw in ["password", "access", "permission", "login", "sudo", "admin", "role"]):
            issue_type = "access/request"

        # Determine priority
        priority = "medium"
        if any(kw in combined for kw in ["critical", "outage", "production down", "all users", "core service", "unreachable"]):
            priority = "critical"
        elif any(kw in combined for kw in ["high", "major", "urgent", "many users", "500 errors", "crash"]):
            priority = "high"
        elif any(kw in combined for kw in ["low", "minor", "informational", "request"]):
            priority = "low"

        # Determine impacted area
        area_mapping = {
            "database": "Database connectivity",
            "network": "Network connectivity",
            "server": "Server infrastructure",
            "application": "Application service",
            "access/request": "Access/permissions"
        }
        impacted_area = area_mapping.get(issue_type, "Unknown")

        # Determine team
        team_mapping = {
            "database": "Database Team",
            "network": "Network Team",
            "server": "Server Team",
            "application": "Application Support",
            "access/request": "Service Desk",
            "unknown": "Manual Review"
        }
        recommended_team = team_mapping.get(issue_type, "Manual Review")

        # Generate troubleshooting steps
        steps_mapping = {
            "database": [
                "Check database server availability and status",
                "Verify network connectivity to database server",
                "Review database connection pool settings",
                "Check recent database logs for errors"
            ],
            "network": [
                "Check network connectivity and routing",
                "Verify VPN/firewall configuration",
                "Test DNS resolution",
                "Check for network outages or maintenance"
            ],
            "server": [
                "Check server availability and health metrics",
                "Review system resource usage (CPU, memory, disk)",
                "Check recent system logs",
                "Verify server network connectivity"
            ],
            "application": [
                "Check application logs for errors",
                "Verify deployment status",
                "Review recent code changes",
                "Test application endpoints"
            ],
            "access/request": [
                "Verify user identity and credentials",
                "Check existing access permissions",
                "Process access request through proper channels",
                "Document access grant in audit log"
            ]
        }
        troubleshooting_steps = steps_mapping.get(issue_type, [
            "Request more specific information",
            "Escalate to team lead for review"
        ])

        # Calculate confidence based on keyword strength
        confidence = 0.75
        if issue_type == "unknown":
            confidence = 0.35
        elif any(kw in combined for kw in ["cannot", "unable", "error", "failing", "down"]):
            confidence = 0.85

        # Generate reasoning
        reasoning = f"The ticket mentions keywords related to {issue_type} issues, leading to this classification."

        return {
            "ticket_id": f"ticket-{uuid.uuid4().hex[:8]}",
            "issue_type": issue_type,
            "priority": priority,
            "impacted_area": impacted_area,
            "recommended_team": recommended_team,
            "troubleshooting_steps": troubleshooting_steps,
            "confidence_score": confidence,
            "reasoning_summary": reasoning,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _fallback_analysis(self, title: str, description: str, error: str) -> dict:
        """Fallback analysis when LLM fails."""
        return {
            "ticket_id": f"ticket-{uuid.uuid4().hex[:8]}",
            "issue_type": "unknown",
            "priority": "medium",
            "impacted_area": "Analysis failed",
            "recommended_team": "Manual Review",
            "troubleshooting_steps": [
                "Review ticket manually",
                "Contact IT team for assistance"
            ],
            "confidence_score": 0.1,
            "reasoning_summary": f"Analysis failed due to error: {error}. Ticket routed to Manual Review.",
            "timestamp": datetime.utcnow().isoformat()
        }


# Singleton instance
analyzer = TicketAnalyzer()