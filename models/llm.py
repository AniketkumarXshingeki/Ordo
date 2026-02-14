import subprocess
import json

MODEL = "phi"   # your ollama model name


def ask_llm(prompt: str) -> str:
    """
    Send prompt to Ollama and return raw text response.
    """
    result = subprocess.run(
        ["ollama", "run", MODEL],
        input=prompt,
        text=True,
        capture_output=True
    )

    return result.stdout.strip()