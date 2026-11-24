import os
import sys
import re
from datetime import datetime
from typing import Dict, List, Optional, TypedDict

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from langgraph.graph import StateGraph, START, END
from config import REPORTS_DIR
from agents import (
    run_researcher_agent,
    run_extractor_agent,
    run_fact_checker_agent,
    run_analysis_agent,
    run_report_generator_agent
)


class ResearchState(TypedDict):
    topic: str
    max_sources: int
    raw_sources: List[Dict[str, str]]
    research_data: str
    extracted_facts: str
    fact_check_results: str
    analysis: str
    final_report: str
    report_path: Optional[str]
    agent_logs: List[Dict[str, str]]
    error: Optional[str]


# ============================================================================
# AGENT NODES
# ============================================================================

def researcher_node(state: ResearchState) -> Dict:
    """Agent 1: Researcher Agent (Tavily API)"""
    topic = state.get("topic", "").strip()
    max_sources = state.get("max_sources", 3)
    logs = list(state.get("agent_logs", []))

    print(f"\n[Agent 1: Researcher Agent] Searching web for: '{topic}'...")

    try:
        sources, research_data = run_researcher_agent(topic, max_results=max_sources)
        if not sources:
            msg = "No web search results could be retrieved for this topic."
            logs.append({"agent": "Researcher Agent", "status": "warning", "message": msg})
            return {
                "raw_sources": [],
                "research_data": "",
                "error": msg,
                "agent_logs": logs
            }

        logs.append({
            "agent": "Researcher Agent",
            "status": "success",
            "message": f"Successfully retrieved {len(sources)} relevant web articles and sources."
        })
        return {
            "raw_sources": sources,
            "research_data": research_data,
            "error": None,
            "agent_logs": logs
        }
    except Exception as e:
        msg = f"Search failed: {e}"
        print(f"[Error in Researcher Agent]: {msg}")
        logs.append({"agent": "Researcher Agent", "status": "error", "message": msg})
        return {
            "raw_sources": [],
            "research_data": "",
            "error": msg,
            "agent_logs": logs
        }


def extractor_node(state: ResearchState) -> Dict:
    """Agent 2: Information Extraction Agent (Gemini API)"""
    if state.get("error"):
        return {}

    topic = state.get("topic", "")
    research_data = state.get("research_data", "")
    logs = list(state.get("agent_logs", []))

    print(f"\n[Agent 2: Information Extraction Agent] Extracting key facts, statistics, and dates...")

    try:
        extracted = run_extractor_agent(topic, research_data)
        logs.append({
            "agent": "Information Extraction Agent",
            "status": "success",
            "message": "Extracted key facts, data metrics, statistics, and timelines from sources."
        })
        return {
            "extracted_facts": extracted,
            "agent_logs": logs
        }
    except Exception as e:
        msg = f"Extraction failed: {e}"
        print(f"[Error in Extraction Agent]: {msg}")
        logs.append({"agent": "Information Extraction Agent", "status": "error", "message": msg})
        return {
            "error": msg,
            "agent_logs": logs
        }


def fact_checker_node(state: ResearchState) -> Dict:
    """Agent 3: Fact Checker Agent (Gemini API)"""
    if state.get("error"):
        return {}

    topic = state.get("topic", "")
    extracted_facts = state.get("extracted_facts", "")
    research_data = state.get("research_data", "")
    logs = list(state.get("agent_logs", []))

    print(f"\n[Agent 3: Fact Checker Agent] Verifying claims against sources and flagging unsupported data...")

    try:
        fact_check = run_fact_checker_agent(topic, extracted_facts, research_data)
        logs.append({
            "agent": "Fact Checker Agent",
            "status": "success",
            "message": "Verified claims against source text; flagged uncertainties and hallucinations."
        })
        return {
            "fact_check_results": fact_check,
            "agent_logs": logs
        }
    except Exception as e:
        msg = f"Fact checking failed: {e}"
        print(f"[Error in Fact Checker Agent]: {msg}")
        logs.append({"agent": "Fact Checker Agent", "status": "error", "message": msg})
        return {
            "error": msg,
            "agent_logs": logs
        }


def analysis_node(state: ResearchState) -> Dict:
    """Agent 4: Analysis Agent (Gemini API)"""
    if state.get("error"):
        return {}

    topic = state.get("topic", "")
    verified_facts = state.get("fact_check_results", state.get("extracted_facts", ""))
    logs = list(state.get("agent_logs", []))

    print(f"\n[Agent 4: Analysis Agent] Identifying trends, opportunities, and challenges...")

    try:
        analysis = run_analysis_agent(topic, verified_facts)
        logs.append({
            "agent": "Analysis Agent",
            "status": "success",
            "message": "Identified technological/industry trends, comparative dynamics, and strategic opportunities."
        })
        return {
            "analysis": analysis,
            "agent_logs": logs
        }
    except Exception as e:
        msg = f"Analysis failed: {e}"
        print(f"[Error in Analysis Agent]: {msg}")
        logs.append({"agent": "Analysis Agent", "status": "error", "message": msg})
        return {
            "error": msg,
            "agent_logs": logs
        }


def report_generator_node(state: ResearchState) -> Dict:
    """Agent 5: Report Generator Agent (Gemini API)"""
    if state.get("error"):
        return {}

    topic = state.get("topic", "")
    verified_facts = state.get("fact_check_results", state.get("extracted_facts", ""))
    analysis = state.get("analysis", "")
    sources = state.get("raw_sources", [])
    logs = list(state.get("agent_logs", []))

    print(f"\n[Agent 5: Report Generator Agent] Creating structured research report with findings & citations...")

    try:
        report = run_report_generator_agent(topic, verified_facts, analysis, sources)

        # Save report
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = re.sub(r"[^\w\-]", "_", topic)[:30].strip("_")
        dated_path = REPORTS_DIR / f"{timestamp}_{slug}.txt"
        latest_path = REPORTS_DIR / "research_report.txt"

        with open(dated_path, "w", encoding="utf-8") as f:
            f.write(report)
        with open(latest_path, "w", encoding="utf-8") as f:
            f.write(report)

        logs.append({
            "agent": "Report Generator Agent",
            "status": "success",
            "message": f"Successfully compiled and saved full executive report to {dated_path.name}."
        })

        return {
            "final_report": report,
            "report_path": str(dated_path),
            "agent_logs": logs
        }
    except Exception as e:
        msg = f"Report generation failed: {e}"
        print(f"[Error in Report Generator Agent]: {msg}")
        logs.append({"agent": "Report Generator Agent", "status": "error", "message": msg})
        return {
            "error": msg,
            "agent_logs": logs
        }


# ============================================================================
# ORCHESTRATOR DECISION LOGIC (ROUTING)
# ============================================================================

def orchestrator_search_router(state: ResearchState) -> str:
    """Orchestrator decides if we can proceed to extraction or must abort on error."""
    if state.get("error") or not state.get("raw_sources"):
        print("[Orchestrator] Halting workflow: Search returned no usable sources.")
        return END
    return "extractor_agent"


def orchestrator_pipeline_router(state: ResearchState) -> str:
    """Orchestrator checks for errors at each subsequent agent transition."""
    if state.get("error"):
        print(f"[Orchestrator] Halting workflow due to error: {state.get('error')}")
        return END
    return "continue"


# ============================================================================
# LANGGRAPH WORKFLOW DEFINITION
# ============================================================================

def build_orchestrator_graph():
    """Build and compile the 5-Agent LangGraph Research Workflow."""
    workflow = StateGraph(ResearchState)

    # 1. Register all 5 agents as nodes
    workflow.add_node("researcher_agent", researcher_node)
    workflow.add_node("extractor_agent", extractor_node)
    workflow.add_node("fact_checker_agent", fact_checker_node)
    workflow.add_node("analysis_agent", analysis_node)
    workflow.add_node("report_generator_agent", report_generator_node)

    # 2. Define Orchestrator flow
    workflow.add_edge(START, "researcher_agent")

    # Conditional router after search
    workflow.add_conditional_edges(
        "researcher_agent",
        orchestrator_search_router,
        {
            "extractor_agent": "extractor_agent",
            END: END
        }
    )

    # Pipeline transitions
    workflow.add_edge("extractor_agent", "fact_checker_agent")
    workflow.add_edge("fact_checker_agent", "analysis_agent")
    workflow.add_edge("analysis_agent", "report_generator_agent")
    workflow.add_edge("report_generator_agent", END)

    return workflow.compile()


def run_graph_research(topic: str, max_sources: int = 3) -> ResearchState:
    """Run the complete 5-agent LangGraph workflow synchronously."""
    app = build_orchestrator_graph()
    initial_state: ResearchState = {
        "topic": topic,
        "max_sources": max_sources,
        "raw_sources": [],
        "research_data": "",
        "extracted_facts": "",
        "fact_check_results": "",
        "analysis": "",
        "final_report": "",
        "report_path": None,
        "agent_logs": [],
        "error": None
    }
    final_state = app.invoke(initial_state)
    return final_state


def stream_graph_research(topic: str, max_sources: int = 3):
    """
    Stream updates from each agent node in real time.
    Yields (node_name, state_chunk).
    """
    app = build_orchestrator_graph()
    initial_state: ResearchState = {
        "topic": topic,
        "max_sources": max_sources,
        "raw_sources": [],
        "research_data": "",
        "extracted_facts": "",
        "fact_check_results": "",
        "analysis": "",
        "final_report": "",
        "report_path": None,
        "agent_logs": [],
        "error": None
    }
    for chunk in app.stream(initial_state):
        yield chunk


# ============================================================================
# CLI TEST ENTRYPOINT
# ============================================================================

if __name__ == "__main__":
    print("=" * 65)
    print("ResearchMate - 5-Agent LangGraph Research Orchestrator")
    print("=" * 65)

    user_topic = input("Enter your research topic: ").strip()
    if not user_topic:
        print("Please enter a valid research topic.")
        sys.exit(0)

    print(f"\n[Orchestrator] Starting multi-agent research workflow for: '{user_topic}'...")
    result = run_graph_research(user_topic, max_sources=5)

    if result.get("error"):
        print(f"\n[ORCHESTRATOR ERROR]: {result['error']}")
    else:
        print("\n" + "=" * 65)
        print("FINAL RESEARCH REPORT")
        print("=" * 65)
        print(result["final_report"])
        print("\n" + "=" * 65)
        print(f"Report saved to: {result.get('report_path')}")
        print("Latest copy at: reports/research_report.txt")
