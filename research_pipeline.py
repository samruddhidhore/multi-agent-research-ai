import os
import sys
import re
import time
from datetime import datetime

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import REPORTS_DIR
from tools.search_tool import search_web_tool
from agents.gemini_client import call_gemini
from agents.report_generator_agent import strip_markdown


def fast_research(topic: str, max_sources: int = 5) -> dict:
    """
    Academic Research Paper Engine (3-4 full pages of deep, publication-grade content).
    Synthesizes multiple research papers (>2 sources) with formal academic formatting.
    Zero emojis, zero markdown symbols.
    """
    t0 = time.time()

    # Retrieve multiple research papers / academic studies (default: 5 papers)
    sources, data = search_web_tool(topic, max_results=max_sources)
    if not sources or not data:
        return {
            "success": False,
            "error": "No research papers or academic sources could be found for this topic.",
            "report": "",
            "sources": [],
            "duration": time.time() - t0
        }

    sources_text = ""
    for idx, s in enumerate(sources, start=1):
        sources_text += f"\n--- RESEARCH PAPER {idx} ---\nTitle: {s.get('title', 'N/A')}\nURL: {s.get('url', 'N/A')}\nExtracted Content:\n{s.get('content', '')}\n"

    current_year = datetime.now().year

    prompt = f"""
You are a Principal Scientific Investigator and Senior Academic Reviewer.
Your goal is to author an exhaustive, publication-grade, formal ACADEMIC RESEARCH PAPER reviewing current literature on: {topic}.

VOLUME AND EXTENSION REQUIREMENT:
- The paper MUST be comprehensive, rigorous, and extensive in volume (at least 3 to 4 full pages, approximately 2,000 to 2,500 words).
- Provide deep academic prose, multi-sentence analytical paragraphs, detailed explanations, and complete statistical extractions.
- Do NOT produce a short summary or brief bullet lists. Write an extensive, fully articulated research paper.

FORMATTING RULES:
- Absolutely NO EMOJIS anywhere.
- Absolutely NO MARKDOWN SYNTAX (strictly NO hash symbols #, ##, NO asterisks **, *).
- Pure, formal academic plain text document format with standard capitalized section headers and divider lines.

TOPIC: {topic}
DATE: {current_year}
NUMBER OF REVIEWED PAPERS: {len(sources)}

COLLECTED RESEARCH PAPERS AND LITERATURE EVIDENCE:
{sources_text}

Author the comprehensive academic paper using this exact formal structure:

================================================================================
ACADEMIC RESEARCH PAPER: {topic.upper()}
================================================================================
Document Type: Systematic Literature Review and Meta-Analysis
Publication Date: {current_year}
Scope: In-Depth Evaluation of {len(sources)} Published Research Studies
================================================================================

ABSTRACT
(Provide a comprehensive, multi-paragraph academic abstract detailing Background, Research Objective, Methodologies Examined, Primary Empirical Findings, and Overarching Conclusions across all reviewed literature)

KEYWORDS
(List 5 to 7 formal academic index keywords separated by commas)

--------------------------------------------------------------------------------
1.0 INTRODUCTION AND THEORETICAL FOUNDATION
--------------------------------------------------------------------------------
1.1 Historical Context and Background
(Thorough historical context, evolution of paradigms, and foundational theories leading to the present state)
1.2 Problem Statement and Research Motivation
(Detailed examination of the core operational, theoretical, or physical bottlenecks driving contemporary research)
1.3 Review Scope and Analytical Framework
(Explicit delineation of this systematic review's focus, comparative criteria, and evaluation methodology)

--------------------------------------------------------------------------------
2.0 COMPREHENSIVE PAPER-BY-PAPER EVIDENCE AND DATA EXTRACTION
--------------------------------------------------------------------------------
(Dedicate an extensive, structured sub-section for EACH reviewed research paper)
For each paper (Paper 1 through Paper {len(sources)}):
- Study Title and Source / Journal:
- Core Objective and Investigated Hypotheses:
- Technical Methodology, Algorithm, or Framework:
- Detailed Quantitative Findings and Empirical Metrics (exact percentages, performance benchmarks, sample sizes, numerical gains, and dates):
- Critical Findings and Author Conclusions:

--------------------------------------------------------------------------------
3.0 METHODOLOGICAL AND ARCHITECTURAL ANALYSIS
--------------------------------------------------------------------------------
(Deep technical analysis of the underlying computational models, algorithms, experimental baselines, datasets, and physical or simulation architectures utilized across the studies)

--------------------------------------------------------------------------------
4.0 CROSS-PAPER COMPARATIVE SYNTHESIS AND BENCHMARKING
--------------------------------------------------------------------------------
4.1 Points of Methodological and Empirical Consensus
(Where the reviewed research papers agree and validate each other)
4.2 Divergent Findings, Discrepancies, and Conflicting Results
(Where methodologies, assumptions, or performance outcomes conflict)
4.3 Theoretical Projections versus Empirical Hardware Reality
(Critical auditing of theoretical claims versus actual real-world hardware or experimental performance)

--------------------------------------------------------------------------------
5.0 CRITICAL CHALLENGES, BOTTLENECKS AND RISK DIMENSIONS
--------------------------------------------------------------------------------
5.1 Technical, Hardware, and Scalability Limitations
(In-depth analysis of computational bottlenecks, physical hardware limits, and implementation hurdles)
5.2 Data Quality, Memory Architecture, and Environmental Constraints
(Data availability, specialized memory requirements, noise factors, and bandwidth)
5.3 Governance, Security, and Ethical Dimensions
(Safety, operational robustness, and societal/regulatory considerations)

--------------------------------------------------------------------------------
6.0 STRATEGIC OPPORTUNITIES AND FUTURE RESEARCH DIRECTIONS
--------------------------------------------------------------------------------
(Thorough academic exploration of emerging high-impact trajectories, theoretical breakthroughs on the horizon, hybrid architectures, and novel application frontiers)

--------------------------------------------------------------------------------
7.0 ACTIONABLE RECOMMENDATIONS FOR PRACTITIONERS AND RESEARCHERS
--------------------------------------------------------------------------------
(Provide 5 to 7 concrete, technically rigorous recommendations for system designers, researchers, and engineers)

--------------------------------------------------------------------------------
8.0 CONCLUSION
--------------------------------------------------------------------------------
(Exhaustive synthesis consolidating the state of the art, definitive findings, and long-term outlook for the field)

--------------------------------------------------------------------------------
9.0 BIBLIOGRAPHIC REFERENCES AND CITED SOURCES
--------------------------------------------------------------------------------
(List formal bibliographic citation entries for each reviewed paper including Title, Source, and Full URL)
"""

    raw_output = call_gemini(prompt)
    clean_report = strip_markdown(raw_output)

    # Save report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = re.sub(r"[^\w\-]", "_", topic)[:30].strip("_")
    dated_file = REPORTS_DIR / f"{timestamp}_{slug}.txt"
    latest_file = REPORTS_DIR / "research_report.txt"

    with open(dated_file, "w", encoding="utf-8") as f:
        f.write(clean_report)
    with open(latest_file, "w", encoding="utf-8") as f:
        f.write(clean_report)

    duration = time.time() - t0
    return {
        "success": True,
        "topic": topic,
        "report": clean_report,
        "sources": sources,
        "report_path": str(dated_file),
        "duration": duration,
        "error": None
    }


def run_research():
    """CLI Runner."""
    print("=================================================================")
    print("RESEARCHMATE - ACADEMIC RESEARCH PAPER ENGINE")
    print("=================================================================")

    topic = input("\nEnter research topic: ").strip()
    if not topic:
        print("Please enter a valid research topic.")
        return

    print(f"\n[Initiating Systematic Review] Topic: '{topic}'...")
    res = fast_research(topic, max_sources=5)

    if not res["success"]:
        print(f"\n[ERROR] {res['error']}")
        return

    word_count = len(res['report'].split())
    approx_pages = max(1, round(word_count / 550, 1))

    print(f"\n[SUCCESS] Completed in {res['duration']:.2f} seconds.")
    print(f"Volume: {word_count} words (~{approx_pages} full pages), {len(res['sources'])} research papers analyzed.")
    print("\n" + "=" * 80)
    print(res["report"])
    print("\n" + "=" * 80)
    print(f"Report saved to: {res['report_path']}")


if __name__ == "__main__":
    run_research()
