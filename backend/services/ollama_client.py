"""
Ollama LLM client for local inference (phi3 model).
"""
import requests

OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3"

def query_ollama(prompt: str, model: str = OLLAMA_MODEL, stream: bool = False) -> str:
    """
    Query the local Ollama model and return the response text.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        # Ollama returns streaming chunks if stream=True, else a single response
        if stream:
            return "".join(chunk.get("response", "") for chunk in data)
        return data.get("response", "")
    except Exception as e:
        return f"[Ollama ERROR] {e}"
