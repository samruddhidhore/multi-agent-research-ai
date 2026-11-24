from agents.gemini_client import call_gemini
from agents.report_generator_agent import strip_markdown


def run_fact_checker_agent(topic: str, extracted_facts: str, research_data: str) -> str:
    """
    Agent 3: Fact Checker Agent (Gemini API) - Fast verification.
    """
    prompt = f"""
You are the Fact Checker Agent.
Topic: {topic}

Extracted Claims:
{extracted_facts}

Sources:
{research_data}

Task: Verify each claim against the sources. Output in concise plain text (NO markdown # or **):
- [VERIFIED] Claim: brief note on source support.
- [FLAGGED] Claim: if unsupported or ambiguous.
End with: Overall Confidence: (High / Medium / Low).
"""
    raw_output = call_gemini(prompt)
    return strip_markdown(raw_output)
