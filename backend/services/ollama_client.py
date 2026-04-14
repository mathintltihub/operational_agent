"""
Ollama LLM client for local inference (llama3 model).
"""
import os
import platform
import requests
import json
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_API_URL = f"{OLLAMA_BASE_URL}/api/generate"
OLLAMA_TAGS_URL = f"{OLLAMA_BASE_URL}/api/tags"

MODEL_BY_OS = {
    "Windows": "llama3.2:3b",
    "Darwin": "phi3",
    "Linux": "llama3.2:3b",
}

# Backward-compatible constant for existing imports.
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", MODEL_BY_OS.get(platform.system(), "llama3.2:3b"))
DEFAULT_TIMEOUT = 90


def get_active_model() -> str:
    """Resolve active model from env override or OS-specific defaults."""
    system_name = platform.system()

    global_override = os.getenv("OLLAMA_MODEL")
    if global_override:
        return global_override

    if system_name == "Windows":
        return os.getenv("OLLAMA_MODEL_WINDOWS", MODEL_BY_OS["Windows"])
    if system_name == "Darwin":
        return os.getenv("OLLAMA_MODEL_MAC", MODEL_BY_OS["Darwin"])
    if system_name == "Linux":
        return os.getenv("OLLAMA_MODEL_LINUX", MODEL_BY_OS["Linux"])

    return MODEL_BY_OS["Linux"]


def get_available_models() -> List[str]:
    """Return local Ollama model names, or an empty list if unavailable."""
    try:
        response = requests.get(OLLAMA_TAGS_URL, timeout=5)
        response.raise_for_status()
        payload = response.json()
        models = payload.get("models", [])
        return [model.get("name", "") for model in models if model.get("name")]
    except Exception:
        return []


def check_ollama_health() -> bool:
    """Check if Ollama service is running and accessible."""
    try:
        response = requests.get(OLLAMA_TAGS_URL, timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def get_ollama_runtime_status() -> dict:
    """Get Ollama connectivity and active model availability details."""
    connected = check_ollama_health()
    active_model = get_active_model()
    available_models = get_available_models() if connected else []
    model_available = active_model in available_models

    return {
        "status": "connected" if connected else "disconnected",
        "model": active_model,
        "model_available": model_available,
        "available_models": available_models,
        "detected_os": platform.system(),
        "endpoint": OLLAMA_BASE_URL,
    }


def query_ollama(prompt: str, model: Optional[str] = None, stream: bool = False,
                  timeout: int = DEFAULT_TIMEOUT) -> str:
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
    active_model = model or get_active_model()

    payload = {
        "model": active_model,
        "prompt": prompt,
        "stream": stream,
        "options": {
            "temperature": 0.3,
            "top_p": 0.9,
            "num_ctx": 4096,
        }
    }

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
