import os
import sys
from google import genai
from config import GEMINI_API_KEY, DEFAULT_GEMINI_MODEL, FALLBACK_GEMINI_MODELS

# Ensure UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

_client = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing. Please set it in your .env file.")
        _client = genai.Client(api_key=api_key)
    return _client


def call_gemini(prompt: str, model: str = DEFAULT_GEMINI_MODEL) -> str:
    """Call Google GenAI Interactions API with fallback support."""
    client = get_client()
    models_to_try = [model] + [m for m in FALLBACK_GEMINI_MODELS if m != model]

    last_error = None
    for m in models_to_try:
        try:
            response = client.interactions.create(
                model=m,
                input=prompt
            )
            output = getattr(response, "output_text", None)
            if output:
                return output.strip()
            return str(response).strip()
        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")
