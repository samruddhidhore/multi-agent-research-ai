from agents.gemini_client import call_gemini
from agents.report_generator_agent import strip_markdown


def run_extractor_agent(topic: str, research_data: str) -> str:
    """
    Agent 2: Information Extraction Agent (Gemini API) - Fast & Concise.
    """
    prompt = f"""
You are the Information Extraction Agent.
Topic: {topic}

Sources:
{research_data}

Task: Extract essential information in concise plain text bullets (NO markdown symbols like # or **):
1. CORE FACTS:
- (List 3 to 4 essential facts)
2. KEY METRICS & STATS:
- (List 2 to 3 key numbers, percentages, or milestones)
3. KEY PLAYERS & TECH:
- (List main companies or technologies mentioned)

Keep it brief, sharp, and factual.
"""
    raw_output = call_gemini(prompt)
    return strip_markdown(raw_output)
