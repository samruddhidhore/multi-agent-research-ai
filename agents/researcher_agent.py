from typing import List, Dict, Tuple
from tools.search_tool import search_web_tool


def run_researcher_agent(topic: str, max_results: int = 5) -> Tuple[List[Dict[str, str]], str]:
    """
    Agent 1: Researcher Agent (Tavily API)
    Searches the internet and collects relevant articles, facts, and URLs.
    """
    sources, research_data = search_web_tool(query=topic, max_results=max_results)
    return sources, research_data
