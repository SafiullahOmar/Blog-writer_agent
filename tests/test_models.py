"""
Tests for Pydantic models.
"""

import pytest
from pydantic import ValidationError

from blog_agent.models import Task, Plan, RouterDecision, EvidenceItem, EvidencePack


class TestTask:
    """Tests for the Task model."""
    
    def test_valid_task(self):
        """Test creating a valid task."""
        task = Task(
            id=1,
            title="Introduction",
            goal="Understand the basics of self attention",
            bullets=[
                "Define self attention",
                "Explain why it matters",
                "Compare with RNNs",
            ],
            target_words=200,
        )
        
        assert task.id == 1
        assert task.title == "Introduction"
        assert len(task.bullets) == 3
        assert task.requires_code is False
    
    def test_task_with_all_fields(self):
        """Test task with all optional fields."""
        task = Task(
            id=2,
            title="Implementation",
            goal="Implement self attention in PyTorch",
            bullets=["Setup", "Forward pass", "Backward pass"],
            target_words=300,
            tags=["code", "pytorch"],
            requires_research=True,
            requires_citations=True,
            requires_code=True,
        )
        
        assert task.requires_code is True
        assert "code" in task.tags
    
    def test_task_invalid_bullets_too_few(self):
        """Test that task requires at least 3 bullets."""
        with pytest.raises(ValidationError):
            Task(
                id=1,
                title="Test",
                goal="Test goal",
                bullets=["One", "Two"],  # Only 2 bullets
                target_words=200,
            )
    
    def test_task_invalid_bullets_too_many(self):
        """Test that task allows at most 6 bullets."""
        with pytest.raises(ValidationError):
            Task(
                id=1,
                title="Test",
                goal="Test goal",
                bullets=["1", "2", "3", "4", "5", "6", "7"],  # 7 bullets
                target_words=200,
            )


class TestPlan:
    """Tests for the Plan model."""
    
    def test_valid_plan(self):
        """Test creating a valid plan."""
        task = Task(
            id=1,
            title="Intro",
            goal="Goal",
            bullets=["A", "B", "C"],
            target_words=200,
        )
        
        plan = Plan(
            blog_title="Understanding Self Attention",
            audience="developers",
            tone="technical",
            tasks=[task],
        )
        
        assert plan.blog_title == "Understanding Self Attention"
        assert plan.blog_kind == "explainer"  # Default
        assert len(plan.tasks) == 1
    
    def test_plan_with_blog_kind(self):
        """Test plan with different blog kinds."""
        task = Task(
            id=1,
            title="News",
            goal="Summarize",
            bullets=["A", "B", "C"],
            target_words=200,
        )
        
        plan = Plan(
            blog_title="AI News Roundup",
            audience="general",
            tone="conversational",
            blog_kind="news_roundup",
            tasks=[task],
        )
        
        assert plan.blog_kind == "news_roundup"


class TestRouterDecision:
    """Tests for the RouterDecision model."""
    
    def test_closed_book_decision(self):
        """Test closed_book routing decision."""
        decision = RouterDecision(
            needs_research=False,
            mode="closed_book",
            reason="Evergreen topic about fundamentals",
        )
        
        assert decision.needs_research is False
        assert decision.queries == []
    
    def test_open_book_decision(self):
        """Test open_book routing decision with queries."""
        decision = RouterDecision(
            needs_research=True,
            mode="open_book",
            reason="Weekly news roundup needs fresh data",
            queries=["AI news January 2025", "LLM releases this week"],
            max_results_per_query=8,
        )
        
        assert decision.needs_research is True
        assert len(decision.queries) == 2


class TestEvidenceItem:
    """Tests for the EvidenceItem model."""
    
    def test_evidence_item(self):
        """Test creating an evidence item."""
        item = EvidenceItem(
            title="OpenAI Releases GPT-5",
            url="https://example.com/news",
            published_at="2025-01-15",
            snippet="OpenAI announced...",
            source="TechNews",
        )
        
        assert item.url == "https://example.com/news"
        assert item.published_at == "2025-01-15"
    
    def test_evidence_item_minimal(self):
        """Test evidence item with only required fields."""
        item = EvidenceItem(
            title="Article",
            url="https://example.com",
        )
        
        assert item.published_at is None
        assert item.snippet is None


class TestEvidencePack:
    """Tests for the EvidencePack model."""
    
    def test_empty_pack(self):
        """Test empty evidence pack."""
        pack = EvidencePack()
        assert pack.evidence == []
    
    def test_pack_with_items(self):
        """Test evidence pack with items."""
        items = [
            EvidenceItem(title="A", url="https://a.com"),
            EvidenceItem(title="B", url="https://b.com"),
        ]
        pack = EvidencePack(evidence=items)
        
        assert len(pack.evidence) == 2
