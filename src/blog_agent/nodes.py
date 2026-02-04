"""
Graph nodes for the Blog Writing Agent.

Each node is a function that takes state and returns updates to the state.
"""

from typing import List
from datetime import date, timedelta
from pathlib import Path

from langchain_core.messages import SystemMessage, HumanMessage

from blog_agent.state import State
from blog_agent.models import (
    Task, Plan, RouterDecision, EvidenceItem, EvidencePack
)
from blog_agent.prompts import (
    ROUTER_SYSTEM, RESEARCH_SYSTEM, ORCHESTRATOR_SYSTEM, WORKER_SYSTEM
)
from blog_agent.llm import get_llm, get_llm_with_structured_output
from blog_agent.tools import tavily_search, iso_to_date
from blog_agent.config import get_settings


def router_node(state: State) -> dict:
    """
    Router node - decides if research is needed and sets the mode.
    
    Analyzes the topic and determines:
    - Whether web research is needed
    - Which mode to use (closed_book, hybrid, open_book)
    - What search queries to run if research is needed
    
    Args:
        state: Current graph state.
        
    Returns:
        State updates with routing decision.
    """
    settings = get_settings()
    topic = state["topic"]
    
    decider = get_llm_with_structured_output(RouterDecision)
    decision = decider.invoke([
        SystemMessage(content=ROUTER_SYSTEM),
        HumanMessage(content=f"Topic: {topic}\nAs-of date: {state['as_of']}"),
    ])

    # Set recency window based on mode
    if decision.mode == "open_book":
        recency_days = settings.open_book_recency_days
    elif decision.mode == "hybrid":
        recency_days = settings.hybrid_recency_days
    else:
        recency_days = settings.closed_book_recency_days

    return {
        "needs_research": decision.needs_research,
        "mode": decision.mode,
        "queries": decision.queries,
        "recency_days": recency_days,
    }


def route_next(state: State) -> str:
    """
    Conditional edge function - determines next node based on research needs.
    
    Args:
        state: Current graph state.
        
    Returns:
        Name of the next node ("research" or "orchestrator").
    """
    return "research" if state["needs_research"] else "orchestrator"


def research_node(state: State) -> dict:
    """
    Research node - performs web searches and collects evidence.
    
    Executes search queries, normalizes results, and filters by recency.
    
    Args:
        state: Current graph state.
        
    Returns:
        State updates with collected evidence.
    """
    settings = get_settings()
    llm = get_llm()
    
    queries = (state.get("queries", []) or [])[:settings.max_search_queries]
    max_results = settings.max_results_per_query

    # Collect raw search results
    raw_results: List[dict] = []
    for q in queries:
        raw_results.extend(tavily_search(q, max_results=max_results))

    if not raw_results:
        return {"evidence": []}

    # Use LLM to normalize and deduplicate results
    extractor = llm.with_structured_output(EvidencePack)
    pack = extractor.invoke([
        SystemMessage(content=RESEARCH_SYSTEM),
        HumanMessage(
            content=(
                f"As-of date: {state['as_of']}\n"
                f"Recency days: {state['recency_days']}\n\n"
                f"Raw results:\n{raw_results}"
            )
        ),
    ])

    # Deduplicate by URL
    dedup = {}
    for e in pack.evidence:
        if e.url:
            dedup[e.url] = e
    evidence = list(dedup.values())

    # Apply hard recency filter for open_book mode
    mode = state.get("mode", "closed_book")
    if mode == "open_book":
        as_of = date.fromisoformat(state["as_of"])
        cutoff = as_of - timedelta(days=int(state["recency_days"]))
        fresh: List[EvidenceItem] = []
        for e in evidence:
            d = iso_to_date(e.published_at)
            if d and d >= cutoff:
                fresh.append(e)
        evidence = fresh

    return {"evidence": evidence}


def orchestrator_node(state: State) -> dict:
    """
    Orchestrator node - creates the blog outline/plan.
    
    Uses the LLM to generate a structured plan with sections, goals, and bullets.
    
    Args:
        state: Current graph state.
        
    Returns:
        State updates with the blog plan.
    """
    llm = get_llm()
    planner = llm.with_structured_output(Plan)
    
    evidence = state.get("evidence", [])
    mode = state.get("mode", "closed_book")

    # Force blog_kind for open_book mode
    forced_kind = "news_roundup" if mode == "open_book" else None

    plan = planner.invoke([
        SystemMessage(content=ORCHESTRATOR_SYSTEM),
        HumanMessage(
            content=(
                f"Topic: {state['topic']}\n"
                f"Mode: {mode}\n"
                f"As-of: {state['as_of']} (recency_days={state['recency_days']})\n"
                f"{'Force blog_kind=news_roundup' if forced_kind else ''}\n\n"
                f"Evidence (ONLY use for fresh claims; may be empty):\n"
                f"{[e.model_dump() for e in evidence][:16]}\n\n"
                f"Instruction: If mode=open_book, your plan must NOT drift into a tutorial."
            )
        ),
    ])

    # Ensure open_book forces the kind even if model forgets
    if forced_kind:
        plan.blog_kind = "news_roundup"

    return {"plan": plan}


def worker_node(payload: dict) -> dict:
    """
    Worker node - writes one section of the blog.
    
    Takes a task specification and produces markdown content for that section.
    
    Args:
        payload: Dictionary containing task, plan, evidence, and context.
        
    Returns:
        State updates with the written section.
    """
    llm = get_llm()
    
    task = Task(**payload["task"])
    plan = Plan(**payload["plan"])
    evidence = [EvidenceItem(**e) for e in payload.get("evidence", [])]
    topic = payload["topic"]
    mode = payload.get("mode", "closed_book")
    as_of = payload.get("as_of")
    recency_days = payload.get("recency_days")

    # Format bullets for the prompt
    bullets_text = "\n- " + "\n- ".join(task.bullets)

    # Format evidence for citation use
    evidence_text = ""
    if evidence:
        evidence_text = "\n".join(
            f"- {e.title} | {e.url} | {e.published_at or 'date:unknown'}".strip()
            for e in evidence[:20]
        )

    # Generate section content
    section_md = llm.invoke([
        SystemMessage(content=WORKER_SYSTEM),
        HumanMessage(
            content=(
                f"Blog title: {plan.blog_title}\n"
                f"Audience: {plan.audience}\n"
                f"Tone: {plan.tone}\n"
                f"Blog kind: {plan.blog_kind}\n"
                f"Constraints: {plan.constraints}\n"
                f"Topic: {topic}\n"
                f"Mode: {mode}\n"
                f"As-of: {as_of} (recency_days={recency_days})\n\n"
                f"Section title: {task.title}\n"
                f"Goal: {task.goal}\n"
                f"Target words: {task.target_words}\n"
                f"Tags: {task.tags}\n"
                f"requires_research: {task.requires_research}\n"
                f"requires_citations: {task.requires_citations}\n"
                f"requires_code: {task.requires_code}\n"
                f"Bullets:{bullets_text}\n\n"
                f"Evidence (ONLY use these URLs when citing):\n{evidence_text}\n"
            )
        ),
    ]).content.strip()

    # Return with task ID for deterministic ordering
    return {"sections": [(task.id, section_md)]}


def reducer_node(state: State) -> dict:
    """
    Reducer node - combines all sections into the final blog post.
    
    Sorts sections by task ID and assembles the complete markdown document.
    
    Args:
        state: Current graph state.
        
    Returns:
        State updates with the final blog post.
    """
    settings = get_settings()
    plan = state["plan"]
    
    if plan is None:
        raise ValueError("Reducer called without a plan.")

    # Sort sections by task ID for correct ordering
    ordered_sections = [md for _, md in sorted(state["sections"], key=lambda x: x[0])]
    body = "\n\n".join(ordered_sections).strip()
    final_md = f"# {plan.blog_title}\n\n{body}\n"

    # Save to output directory
    output_dir = Path(settings.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Sanitize filename
    safe_title = "".join(c for c in plan.blog_title if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_title = safe_title.replace(' ', '_')[:100]
    filename = output_dir / f"{safe_title}.md"
    
    filename.write_text(final_md, encoding="utf-8")
    print(f"Blog saved to: {filename}")

    return {"final": final_md}
