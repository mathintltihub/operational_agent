"""
Ticket analyzer service using LangChain + OpenAI.
"""
import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from langchain_openai import ChatOpenAI

import os
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


class TicketAnalyzer:
    """Analyzes IT support tickets using OpenAI via LangChain."""

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,
            api_key=OPENAI_API_KEY
        )
        self.system_prompt = self._load_prompt()

    def _load_prompt(self) -> str:
        prompt_file = Path(__file__).parent.parent / "prompts" / "operations_agent_prompt.txt"
        return prompt_file.read_text()

    def analyze(self, title: str, description: str) -> dict:
        prompt = self.system_prompt.replace("{title}", title).replace("{description}", description)

        try:
            response = self.llm.invoke(prompt)
            result = self._parse_json(response.content)
            result["ticket_id"] = f"ticket-{uuid.uuid4().hex[:8]}"
            result["timestamp"] = datetime.utcnow().isoformat()
            return result
        except Exception as e:
            print(f"[TicketAnalyzer ERROR] {e}")
            return self._fallback(title, description, str(e))

    def _parse_json(self, content: str) -> dict:
        content = content.strip()

        # Strip markdown code fences
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()

        # Extract JSON object
        match = re.search(r'\{[\s\S]*\}', content)
        if match:
            content = match.group(0)

        return json.loads(content)

    def _fallback(self, title: str, description: str, error: str) -> dict:
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
            "reasoning_summary": f"OpenAI analysis failed: {error}",
            "timestamp": datetime.utcnow().isoformat()
        }


# Singleton instance
analyzer = TicketAnalyzer()
