import re
from typing import List, Dict
from agents.gemini_client import call_gemini


def strip_markdown(text: str) -> str:
    """Safely strip any markdown syntax and emojis to ensure pure clean plain text."""
    if not text:
        return ""
    # Remove all emojis
    cleaned = re.sub(r'[\U00010000-\U0010ffff]', '', text)
    # Convert markdown links [text](url) -> text (url)
    cleaned = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1 (\2)', cleaned)
    # Remove heading hash symbols (# Heading -> Heading)
    cleaned = re.sub(r'^#{1,6}\s*', '', cleaned, flags=re.MULTILINE)
    # Remove bold/italic markers (**text**, *text*, __text__, _text_)
    cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)
    cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)
    cleaned = re.sub(r'__(.*?)__', r'\1', cleaned)
    cleaned = re.sub(r'_(.*?)_', r'\1', cleaned)
    # Remove code backticks (`code` -> code)
    cleaned = re.sub(r'`(.*?)`', r'\1', cleaned)
    return cleaned.strip()


def run_report_generator_agent(
    topic: str,
    verified_facts: str,
    analysis: str,
    sources: List[Dict[str, str]]
) -> str:
    """
    Agent 5: Report Generator Agent (Gemini API)
    Fast, executive plain text research report generation (NO Markdown, NO Emojis).
    """
    sources_text = "\n".join([
        f"- {s.get('title', 'Source ' + str(idx))}: {s.get('url', 'N/A')}"
        for idx, s in enumerate(sources, start=1)
    ])

    prompt = f"""
You are the Executive Report Generator Agent.
Synthesize an executive research report in pure, clean PLAIN TEXT.

STRICT RULES:
- Absolutely NO emojis anywhere in the report.
- Absolutely NO markdown hash symbols (#, ##).
- Absolutely NO asterisks for bold or italic (**, *).
- Use clear uppercase headings and divider lines.

Topic: {topic}

Verified Findings:
{verified_facts}

Strategic Analysis:
{analysis}

Sources:
{sources_text}

Format the report exactly as follows:

======================================================================
RESEARCH REPORT: {topic.upper()}
======================================================================

1. EXECUTIVE SUMMARY
(2 to 3 concise sentences summarizing the core state and impact)

----------------------------------------------------------------------
2. KEY VERIFIED FINDINGS AND DATA POINTS
----------------------------------------------------------------------
- (Bulleted verified facts and metrics)

----------------------------------------------------------------------
3. INDUSTRY TRENDS AND DYNAMICS
----------------------------------------------------------------------
- (Bulleted top trends shaping this field)

----------------------------------------------------------------------
4. STRATEGIC OPPORTUNITIES AND USE-CASES
----------------------------------------------------------------------
- (High-potential application areas)

----------------------------------------------------------------------
5. CHALLENGES AND RISK FACTORS
----------------------------------------------------------------------
- (Key bottlenecks and considerations)

----------------------------------------------------------------------
6. ACTIONABLE RECOMMENDATIONS
----------------------------------------------------------------------
- (3 concise, practical next steps)

----------------------------------------------------------------------
7. REFERENCES AND VERIFIED SOURCES
----------------------------------------------------------------------
(List the sources with titles and URLs)
"""
    raw_output = call_gemini(prompt)
    clean_report = strip_markdown(raw_output)
    return clean_report
