import os
from typing import Dict, List, Tuple
from tavily import TavilyClient
from config import TAVILY_API_KEY


def get_tavily_client() -> TavilyClient:
    api_key = TAVILY_API_KEY or os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("Tavily API key not found. Please set TAVILY_API_KEY in your .env file.")
    return TavilyClient(api_key=api_key)


def search_web_tool(query: str, max_results: int = 5) -> Tuple[List[Dict[str, str]], str]:
    """
    Retrieves multiple research papers, journal articles, and academic studies (>2 sources).
    """
    client = get_tavily_client()

    # Target scholarly research studies, whitepapers, and scientific articles
    enhanced_query = query
    lower_q = query.lower()
    if not any(term in lower_q for term in ["research", "paper", "study", "journal"]):
        enhanced_query = f"{query} research paper study analysis"

    response = client.search(
        query=enhanced_query,
        max_results=max_results,
        search_depth="basic"
    )

    results = response.get("results", [])
    if not results:
        # Fallback to direct query if enhanced query had no results
        fallback_resp = client.search(query=query, max_results=max_results, search_depth="basic")
        results = fallback_resp.get("results", [])

    if not results:
        return [], "No research papers or sources found for this topic."

    formatted_text = ""
    clean_results = []

    for index, item in enumerate(results, start=1):
        title = item.get("title", f"Research Paper {index}")
        # Capture deep content snippet (up to 1200 chars) for accurate information extraction
        content = item.get("content", "")[:1200]
        url = item.get("url", "")

        clean_results.append({
            "index": index,
            "title": title,
            "content": content,
            "url": url
        })

        formatted_text += f"\nRESEARCH PAPER / SOURCE #{index}:\nTitle: {title}\nURL: {url}\nDetailed Content:\n{content}\n"

    return clean_results, formatted_text
