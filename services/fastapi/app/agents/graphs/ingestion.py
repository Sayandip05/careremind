"""
Ingestion Graph — LangGraph state machine for the upload pipeline.

Flow: route_input → extract_excel/extract_ocr → deduplicate → save_to_db

Replaces the old Orchestrator class with a proper state graph.
"""

from langgraph.graph import END, StateGraph

from app.agents.state import IngestionState
from app.agents.nodes.extraction import extract_excel_node, extract_ocr_node
from app.agents.nodes.dedup import deduplicate_node
from app.agents.nodes.persistence import save_to_db_node


def _route_by_file_type(state: IngestionState) -> str:
    """Router: send to the correct extraction node based on file type."""
    file_type = state.get("file_type", "")
    if file_type == "excel":
        return "extract_excel"
    elif file_type == "photo":
        return "extract_ocr"
    return END  # Unknown file type — skip


def build_ingestion_graph() -> StateGraph:
    """
    Build and compile the ingestion state graph.

    Graph:
        START → route_input → extract_excel / extract_ocr → deduplicate → save_to_db → END
    """
    graph = StateGraph(IngestionState)

    # ── Add nodes ────────────────────────────────────────────
    graph.add_node("extract_excel", extract_excel_node)
    graph.add_node("extract_ocr", extract_ocr_node)
    graph.add_node("deduplicate", deduplicate_node)
    graph.add_node("save_to_db", save_to_db_node)

    # ── Entry point: conditional routing ─────────────────────
    graph.set_conditional_entry_point(
        _route_by_file_type,
        {
            "extract_excel": "extract_excel",
            "extract_ocr": "extract_ocr",
            END: END,
        },
    )

    # ── Edges ────────────────────────────────────────────────
    graph.add_edge("extract_excel", "deduplicate")
    graph.add_edge("extract_ocr", "deduplicate")
    graph.add_edge("deduplicate", "save_to_db")
    graph.add_edge("save_to_db", END)

    return graph.compile()


# Pre-built graph instance
ingestion_graph = build_ingestion_graph()
