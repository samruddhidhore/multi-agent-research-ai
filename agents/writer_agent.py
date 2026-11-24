from typing import List, Dict
from agents.research_agent import generate_with_gemini


def write_final_report(topic: str, analysis: str, sources: List[Dict[str, str]]) -> str:
    """Format and synthesize a polished, executive-ready research report."""
    sources_text = "\n".join([
        f"- [{s.get('title', 'Source ' + str(idx))}]({s.get('url', '#')}): {s.get('content', '')[:180]}..."
        for idx, s in enumerate(sources, start=1)
    ])

    prompt = f"""
You are an expert Report Writer Agent.

Topic: {topic}

Analysis from Research Agent:
{analysis}

Available Sources:
{sources_text}

Transform this analysis into a publication-grade Executive Research Report with the following markdown structure:

# Comprehensive Research Report: {topic}

## 1. Executive Summary
Brief high-level overview of the topic and main takeaways.

## 2. Key Findings & Breakthroughs
Detailed findings with bullet points and concrete details.

## 3. Industry Trends & Dynamics
What is shaping the landscape today and moving forward.

## 4. Strategic Opportunities
High-value applications, solutions, and potential upside.

## 5. Critical Challenges & Risks
Key hurdles, technical limitations, regulatory or implementation risks.

## 6. Strategic Recommendations
Actionable next steps or guidance based on the findings.

## 7. References & Sources
List each source clearly as a clickable markdown link using the URLs provided above.

Formatting Rules:
- Output clean, professional GitHub-flavored Markdown.
- Ensure all references match the provided source URLs.
- Do not make up non-existent facts or URLs.
"""
    return generate_with_gemini(prompt)
