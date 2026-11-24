import os
from google import genai
from config import GEMINI_API_KEY, DEFAULT_GEMINI_MODEL, FALLBACK_GEMINI_MODELS


def get_gemini_client() -> genai.Client:
    api_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY in your .env file.")
    return genai.Client(api_key=api_key)


def generate_with_gemini(prompt: str, preferred_model: str = DEFAULT_GEMINI_MODEL) -> str:
    """Generate response using Google GenAI Interactions API with fallback support."""
    client = get_gemini_client()
    models_to_try = [preferred_model] + [m for m in FALLBACK_GEMINI_MODELS if m != preferred_model]

    last_error = None
    for model in models_to_try:
        try:
            response = client.interactions.create(
                model=model,
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


def analyze_findings(topic: str, research_data: str) -> str:
    """Analyze web research findings and synthesize key points."""
    prompt = f"""
You are an expert Research Analyst Agent.

Research Topic: {topic}

Here is information gathered from web sources:
{research_data}

Please perform an in-depth analysis of this information:
1. Executive Summary: Core takeaway on this topic.
2. Key Findings & Data Points: Concrete facts, metrics, and breakthroughs extracted from the sources.
3. Emerging Trends: Notable shifts, technological directions, or industry movements.
4. Opportunities & Applications: Practical areas of implementation and value creation.
5. Challenges & Risks: Bottlenecks, limitations, ethical or technical concerns.

Guidelines:
- Ground your analysis firmly in the provided web sources.
- Highlight any ambiguities or gaps in the sources.
- Use clear, professional, and concise language.
"""
    return generate_with_gemini(prompt)
