"""
Pytest configuration and fixtures.
"""

import pytest
import os


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("GROQ_API_KEY", "test_groq_key")
    monkeypatch.setenv("TAVILY_API_KEY", "test_tavily_key")


@pytest.fixture
def sample_task():
    """Create a sample task for testing."""
    from blog_agent.models import Task
    
    return Task(
        id=1,
        title="Introduction to Self Attention",
        goal="Understand the basics of self attention mechanisms",
        bullets=[
            "Define self attention and its purpose",
            "Explain the relationship between queries, keys, and values",
            "Compare self attention with traditional RNN approaches",
        ],
        target_words=200,
        tags=["intro", "fundamentals"],
        requires_code=False,
    )


@pytest.fixture
def sample_plan(sample_task):
    """Create a sample plan for testing."""
    from blog_agent.models import Plan
    
    return Plan(
        blog_title="Understanding Self Attention: A Complete Guide",
        audience="developers",
        tone="technical",
        blog_kind="explainer",
        constraints=["Keep examples simple", "Focus on intuition"],
        tasks=[sample_task],
    )


@pytest.fixture
def sample_evidence():
    """Create sample evidence items for testing."""
    from blog_agent.models import EvidenceItem
    
    return [
        EvidenceItem(
            title="Attention Is All You Need",
            url="https://arxiv.org/abs/1706.03762",
            published_at="2017-06-12",
            snippet="The dominant sequence transduction models...",
            source="arXiv",
        ),
        EvidenceItem(
            title="The Illustrated Transformer",
            url="https://jalammar.github.io/illustrated-transformer/",
            published_at="2018-06-27",
            snippet="A visual guide to understanding transformers...",
            source="Jay Alammar",
        ),
    ]
