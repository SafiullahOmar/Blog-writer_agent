"""
Blog Writing Agent - Main entry point.

This module provides the BlogAgent class for easy interaction with the agent.
"""

from datetime import date
from typing import Optional, Dict, Any

from blog_agent.graph import app
from blog_agent.models import Plan


class BlogAgent:
    """
    Blog Writing Agent that generates technical blog posts.
    
    Example usage:
        agent = BlogAgent()
        result = agent.run("Write a blog on Self Attention")
        print(result["final"])
    """
    
    def __init__(self):
        """Initialize the blog agent."""
        self.app = app
    
    def run(
        self,
        topic: str,
        as_of: Optional[str] = None,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a blog post for the given topic.
        
        Args:
            topic: The topic for the blog post.
            as_of: Optional date string (ISO format). Defaults to today.
            verbose: Whether to print progress information.
            
        Returns:
            Dictionary containing the final state with:
            - topic: The input topic
            - mode: The research mode used
            - plan: The blog plan
            - evidence: Collected evidence (if any)
            - sections: Written sections
            - final: The complete blog post markdown
        """
        if as_of is None:
            as_of = date.today().isoformat()

        # Initial state
        initial_state = {
            "topic": topic,
            "mode": "",
            "needs_research": False,
            "queries": [],
            "evidence": [],
            "plan": None,
            "as_of": as_of,
            "recency_days": 7,  # Router may overwrite
            "sections": [],
            "final": "",
        }

        # Run the graph
        result = self.app.invoke(initial_state)

        if verbose:
            self._print_summary(result)

        return result
    
    def _print_summary(self, result: Dict[str, Any]) -> None:
        """Print a summary of the generation results."""
        plan: Plan = result["plan"]
        
        print("\n" + "=" * 80)
        print("BLOG GENERATION COMPLETE")
        print("=" * 80)
        print(f"Topic: {result['topic']}")
        print(f"Mode: {result.get('mode')}")
        print(f"Blog Kind: {plan.blog_kind}")
        print(f"As-of Date: {result.get('as_of')}")
        print(f"Recency Days: {result.get('recency_days')}")
        print(f"Needs Research: {result.get('needs_research')}")
        
        if result.get("queries"):
            print(f"Queries Used: {len(result['queries'])}")
            for i, q in enumerate(result["queries"][:5], 1):
                print(f"  {i}. {q}")
        
        if result.get("evidence"):
            print(f"Evidence Collected: {len(result['evidence'])} items")
        
        print(f"Sections Written: {len(plan.tasks)}")
        for task in plan.tasks:
            print(f"  - {task.title} ({task.target_words} words)")
        
        print(f"Total Characters: {len(result.get('final', ''))}")
        print("=" * 80 + "\n")


def run(topic: str, as_of: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to run the blog agent.
    
    Args:
        topic: The topic for the blog post.
        as_of: Optional date string (ISO format).
        
    Returns:
        Result dictionary from the agent.
    """
    agent = BlogAgent()
    return agent.run(topic, as_of=as_of)
