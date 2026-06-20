import os
import requests

MODEL_NAME = "gemma3:4b"
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")


def generate_response(prompt: str) -> str:
    response = requests.post(
        f"{OLLAMA_HOST}/api/chat",
        json={
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0.1},
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]