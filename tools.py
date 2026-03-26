"""
tools.py — External tool integrations for the Insurance AI Research Agent.

Currently implements DuckDuckGo web search as the sole external data source.
All tool functions include error handling and return structured results.
"""

import logging
from typing import Optional

from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web using DuckDuckGo and return structured results.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default 5).

    Returns:
        A list of dicts with keys: title, snippet, url.
        Returns an empty list on failure.
    """
    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=max_results))

        # Normalize results into a clean structure
        results = []
        for r in raw_results:
            results.append(
                {
                    "title": r.get("title", "No title"),
                    "snippet": r.get("body", "No snippet available"),
                    "url": r.get("href", ""),
                }
            )
        return results

    except Exception as e:
        logger.error(f"DuckDuckGo search failed for query '{query}': {e}")
        return []


def format_search_results(results: list[dict]) -> str:
    """
    Format search results into a text block suitable for LLM context injection.

    Args:
        results: List of search result dicts from search_web().

    Returns:
        A formatted string, or an empty string if no results.
    """
    if not results:
        return ""

    formatted_parts = []
    for i, r in enumerate(results, 1):
        formatted_parts.append(
            f"[Source {i}] {r['title']}\n{r['snippet']}\nURL: {r['url']}"
        )

    return "\n\n".join(formatted_parts)
