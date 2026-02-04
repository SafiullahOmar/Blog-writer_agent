"""
LangGraph graph definition for the Blog Writing Agent.

This module constructs and compiles the agent graph.
"""

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from blog_agent.state import State
from blog_agent.nodes import (
    router_node,
    route_next,
    research_node,
    orchestrator_node,
    worker_node,
    reducer_node,
)


def fanout(state: State):
    """
    Fan-out function for parallel worker execution.
    
    Creates a Send object for each task in the plan, enabling parallel
    section writing.
    
    Args:
        state: Current graph state with plan.
        
    Returns:
        List of Send objects, one per task.
    """
    assert state["plan"] is not None, "Plan must be set before fanout"
    
    return [
        Send(
            "worker",
            {
                "task": task.model_dump(),
                "topic": state["topic"],
                "mode": state["mode"],
                "as_of": state["as_of"],
                "recency_days": state["recency_days"],
                "plan": state["plan"].model_dump(),
                "evidence": [e.model_dump() for e in state.get("evidence", [])],
            },
        )
        for task in state["plan"].tasks
    ]


def build_graph() -> StateGraph:
    """
    Build the blog writing agent graph.
    
    Returns:
        Compiled LangGraph StateGraph.
    """
    g = StateGraph(State)
    
    # Add nodes
    g.add_node("router", router_node)
    g.add_node("research", research_node)
    g.add_node("orchestrator", orchestrator_node)
    g.add_node("worker", worker_node)
    g.add_node("reducer", reducer_node)

    # Add edges
    g.add_edge(START, "router")
    
    # Conditional edge: router -> research OR orchestrator
    g.add_conditional_edges(
        "router",
        route_next,
        {
            "research": "research",
            "orchestrator": "orchestrator"
        }
    )
    
    # Research always flows to orchestrator
    g.add_edge("research", "orchestrator")

    # Orchestrator fans out to workers
    g.add_conditional_edges("orchestrator", fanout, ["worker"])
    
    # All workers flow to reducer
    g.add_edge("worker", "reducer")
    
    # Reducer ends the graph
    g.add_edge("reducer", END)

    return g.compile()


# Create the compiled app
app = build_graph()
