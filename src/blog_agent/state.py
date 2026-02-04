"""
LangGraph State Definition for the Blog Writing Agent.

The State is the shared memory that flows through all nodes in the graph.
"""

from typing import TypedDict, List, Optional, Annotated
import operator

from blog_agent.models import Plan, EvidenceItem


class State(TypedDict):
    """
    Shared state for the blog writing agent graph.
    
    Attributes:
        topic: The user's input topic for the blog
        mode: Research mode (closed_book, hybrid, open_book)
        needs_research: Whether web research is required
        queries: Search queries for research
        evidence: Collected evidence from web search
        plan: The blog outline/plan
        as_of: Current date (ISO format) for recency control
        recency_days: How many days back to consider for research
        sections: Written sections as (task_id, markdown) tuples
        final: The combined final blog post
    """
    
    # User input
    topic: str

    # Routing / research
    mode: str
    needs_research: bool
    queries: List[str]
    evidence: List[EvidenceItem]
    plan: Optional[Plan]

    # Recency control
    as_of: str           # ISO date, e.g. "2025-01-29"
    recency_days: int    # 7 for weekly news, 30 for hybrid, etc.

    # Workers output - uses operator.add to accumulate from parallel workers
    sections: Annotated[List[tuple[int, str]], operator.add]  # (task_id, section_md)
    
    # Final output
    final: str
