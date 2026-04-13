"""
Ollama LLM client for local inference (llama3 model).
"""
import json
import logging
import os
from typing import Optional

import requests

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_API_URL = f"{OLLAMA_BASE_URL}/api/generate"
OLLAMA_TAGS_URL = f"{OLLAMA_BASE_URL}/api/tags"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
DEFAULT_TIMEOUT = 90


def check_ollama_health() -> bool:
    """Check if Ollama service is running and accessible."""
    try:
        response = requests.get(OLLAMA_TAGS_URL, timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def query_ollama(prompt: str, model: str = OLLAMA_MODEL, stream: bool = False,
                  timeout: int = DEFAULT_TIMEOUT, response_format: Optional[str] = None) -> str:
    """
    Query the local Ollama model and return the response text.

    Args:
        prompt: The full prompt including system message and user input
        model: Ollama model to use (default: llama3)
        stream: Whether to stream the response
        timeout: Request timeout in seconds

    Returns:
        Model response text or error message
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream,
        "options": {
            "temperature": 0.3,
            "top_p": 0.9,
            "num_ctx": 4096,
        }
    }

    if response_format:
        payload["format"] = response_format

    try:
        if stream:
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=timeout, stream=True)
            response.raise_for_status()
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        if chunk.get("done"):
                            break
                        full_response += chunk.get("response", "")
                    except json.JSONDecodeError:
                        continue
            return full_response.strip()
        else:
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()

    except requests.exceptions.Timeout:
        logger.error(f"Ollama request timed out after {timeout}s")
        return "[ERROR] Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Ollama. Is it running?")
        return "[ERROR] Cannot connect to Ollama. Please ensure Ollama is running on localhost:11434"
    except Exception as e:
        logger.error(f"Ollama request failed: {e}")
        return f"[ERROR] {e}"
