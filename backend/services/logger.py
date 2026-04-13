"""
Local JSON logging service for ticket analysis and audit metadata.
"""
import json
from pathlib import Path
from typing import Dict, List, Optional

from backend.schemas import TicketResponse


class AnalysisLogger:
    """Handles local logging of ticket analyses to JSON."""

    def __init__(self, log_file: str = None):
        if log_file is None:
            base_dir = Path(__file__).parent.parent
            log_file = base_dir / "data" / "logs.json"
        self.log_file = Path(log_file)
        self._ensure_log_file()

    def _ensure_log_file(self):
        """Create log file if it doesn't exist."""
        if not self.log_file.exists():
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            self._write_logs([])

    def _read_logs(self) -> List[dict]:
        """Read existing logs from file."""
        try:
            with open(self.log_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_logs(self, logs: List[dict]):
        """Write logs to file."""
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)

    def log_analysis(
        self,
        title: str,
        description: str,
        result: TicketResponse,
        metadata: Optional[Dict] = None,
    ):
        """Log a ticket analysis result with optional audit metadata."""
        logs = self._read_logs()

        log_entry = {
            "ticket_id": result.ticket_id,
            "title": title,
            "description": description,
            "analysis_result": result.model_dump(),
            "timestamp": result.timestamp,
            "metadata": metadata or {}
        }

        logs.append(log_entry)

        # Keep only last 1000 entries
        if len(logs) > 1000:
            logs = logs[-1000:]

        self._write_logs(logs)

    def get_logs(self, limit: int = 100) -> List[dict]:
        """Get recent log entries."""
        logs = self._read_logs()
        return logs[-limit:]

    def get_log_by_id(self, ticket_id: str) -> Optional[dict]:
        """Get a specific log entry by ticket ID."""
        logs = self._read_logs()
        for log in logs:
            if log.get("ticket_id") == ticket_id:
                return log
        return None

    def clear_logs(self):
        """Clear all logs."""
        self._write_logs([])


# Singleton instance
logger = AnalysisLogger()
