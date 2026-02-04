"""
Research tools for the Blog Writing Agent.

Provides web search functionality using Tavily.
"""

from typing import List, Optional
from datetime import date

from langchain_community.tools.tavily_search import TavilySearchResults

from blog_agent.config import get_settings


def tavily_search(query: str, max_results: int = 5) -> List[dict]:
    """
    Search the web using Tavily.
    
    Args:
        query: Search query string.
        max_results: Maximum number of results to return.
        
    Returns:
        List of normalized search result dictionaries.
    """
    settings = get_settings()
    
    if not settings.tavily_api_key:
        print("Warning: TAVILY_API_KEY not set. Skipping search.")
        return []
    
    try:
        tool = TavilySearchResults(max_results=max_results)
        results = tool.invoke({"query": query})
        
        normalized: List[dict] = []
        for r in results or []:
            normalized.append({
                "title": r.get("title") or "",
                "url": r.get("url") or "",
                "snippet": r.get("content") or r.get("snippet") or "",
                "published_at": r.get("published_date") or r.get("published_at"),
                "source": r.get("source"),
            })
        return normalized
        
    except Exception as e:
        print(f"Warning: Search failed for query '{query}': {e}")
        return []


def iso_to_date(date_string: Optional[str]) -> Optional[date]:
    """
    Convert ISO date string to date object.
    
    Args:
        date_string: ISO format date string (YYYY-MM-DD).
        
    Returns:
        date object or None if parsing fails.
    """
    if not date_string:
        return None
    try:
        return date.fromisoformat(date_string[:10])
    except Exception:
        return None
