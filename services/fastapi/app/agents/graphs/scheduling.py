"""
Scheduling Graph — LangGraph state machine for creating reminder records.

Flow: resolve_specialty → create_reminders

Replaces the old ReminderAgent.schedule_reminders() method.
"""

from langgraph.graph import END, StateGraph

from app.agents.state import SchedulingState
from app.agents.nodes.scheduling import (
    resolve_specialty_node,
    create_reminders_node,
)


def _should_create_reminders(state: SchedulingState) -> str:
    """Router: skip creation if no timings resolved."""
    timings = state.get("timings", [])
    if not timings:
        return END
    return "create_reminders"


def build_scheduling_graph() -> StateGraph:
    """
    Build and compile the scheduling state graph.

    Graph:
        START → resolve_specialty → create_reminders → END
    """
    graph = StateGraph(SchedulingState)

    # ── Add nodes ────────────────────────────────────────────
    graph.add_node("resolve_specialty", resolve_specialty_node)
    graph.add_node("create_reminders", create_reminders_node)

    # ── Entry ────────────────────────────────────────────────
    graph.set_entry_point("resolve_specialty")

    # ── Edges ────────────────────────────────────────────────
    graph.add_conditional_edges("resolve_specialty", _should_create_reminders)
    graph.add_edge("create_reminders", END)

    return graph.compile()


# Pre-built graph instance
scheduling_graph = build_scheduling_graph()
