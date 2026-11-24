from agents.gemini_client import call_gemini
from agents.report_generator_agent import strip_markdown


def run_analysis_agent(topic: str, verified_facts: str) -> str:
    """
    Agent 4: Analysis Agent (Gemini API) - Fast strategic analysis.
    """
    prompt = f"""
You are the Strategic Analysis Agent.
Topic: {topic}

Verified Data:
{verified_facts}

Task: Provide concise strategic analysis in plain text (NO markdown # or **):
1. TOP TRENDS:
- (2-3 emerging trends)
2. STRATEGIC OPPORTUNITIES:
- (2 high-value opportunities)
3. MAJOR CHALLENGES & RISKS:
- (2 key bottlenecks or risks)
"""
    raw_output = call_gemini(prompt)
    return strip_markdown(raw_output)
