"""
Blog Writing Agent - A LangGraph-based technical blog generator.

This package provides an AI-powered agent that can:
- Research topics using web search
- Create detailed blog outlines
- Generate complete technical blog posts
- Handle different content types (explainers, tutorials, news roundups)

Example usage:
    from blog_agent import BlogAgent, run
    
    # Using the class
    agent = BlogAgent()
    result = agent.run("Write a blog on Self Attention")
    
    # Using the convenience function
    result = run("Write a blog on RAG pipelines")
    
    # Access the generated content
    print(result["final"])
"""

from blog_agent.agent import BlogAgent, run
from blog_agent.models import Task, Plan, EvidenceItem, RouterDecision
from blog_agent.graph import app, build_graph
from blog_agent.config import Settings, get_settings

__version__ = "0.1.0"

__all__ = [
    # Main interface
    "BlogAgent",
    "run",
    
    # Graph
    "app",
    "build_graph",
    
    # Models
    "Task",
    "Plan",
    "EvidenceItem",
    "RouterDecision",
    
    # Config
    "Settings",
    "get_settings",
]
