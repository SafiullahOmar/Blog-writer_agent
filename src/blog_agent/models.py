"""
Pydantic models for the Blog Writing Agent.

This module defines all data structures used throughout the agent:
- Task: Individual blog section specification
- Plan: Complete blog outline
- RouterDecision: Routing logic output
- EvidenceItem: Search result item
- EvidencePack: Collection of evidence items
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class Task(BaseModel):
    """Represents one section of the blog to write."""
    
    id: int = Field(..., description="Section number for ordering")
    title: str = Field(..., description="Section heading")
    goal: str = Field(
        ...,
        description="One sentence describing what the reader should be able to do/understand after this section.",
    )
    bullets: List[str] = Field(
        ...,
        min_length=3,
        max_length=6,
        description="3–6 concrete, non-overlapping subpoints to cover in this section.",
    )
    target_words: int = Field(
        ..., 
        ge=120,
        le=550,
        description="Target word count for this section (120–550)."
    )
    tags: List[str] = Field(default_factory=list, description="Optional labels for categorization")
    requires_research: bool = Field(default=False, description="Whether this section needs external citations")
    requires_citations: bool = Field(default=False, description="Whether to include source citations")
    requires_code: bool = Field(default=False, description="Whether to include code snippets")


class Plan(BaseModel):
    """The complete blog outline with all sections."""
    
    blog_title: str = Field(..., description="Title of the blog post")
    audience: str = Field(..., description="Target audience (e.g., 'developers', 'beginners')")
    tone: str = Field(..., description="Writing tone (e.g., 'technical', 'conversational')")
    blog_kind: Literal["explainer", "tutorial", "news_roundup", "comparison", "system_design"] = Field(
        default="explainer",
        description="Type of blog post"
    )
    constraints: List[str] = Field(default_factory=list, description="Additional constraints for writing")
    tasks: List[Task] = Field(..., description="List of sections to write")


class RouterDecision(BaseModel):
    """Output from the router node - determines if research is needed."""
    
    needs_research: bool = Field(..., description="Whether web research is required")
    mode: Literal["closed_book", "hybrid", "open_book"] = Field(
        ...,
        description="Research mode: closed_book (no research), hybrid (some research), open_book (heavy research)"
    )
    reason: str = Field(..., description="Explanation for the routing decision")
    queries: List[str] = Field(
        default_factory=list,
        description="Search queries if research is needed"
    )
    max_results_per_query: int = Field(
        default=5,
        ge=3,
        le=8,
        description="How many results to fetch per query (3–8)."
    )


class EvidenceItem(BaseModel):
    """A single piece of evidence from web search."""
    
    title: str = Field(..., description="Title of the source")
    url: str = Field(..., description="URL of the source")
    published_at: Optional[str] = Field(None, description="Publication date (ISO format)")
    snippet: Optional[str] = Field(None, description="Relevant excerpt from the source")
    source: Optional[str] = Field(None, description="Source name/domain")


class EvidencePack(BaseModel):
    """Collection of evidence items from research."""
    
    evidence: List[EvidenceItem] = Field(
        default_factory=list,
        description="List of evidence items gathered from research"
    )
