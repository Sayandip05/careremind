"""
Ingestion Graph — LangGraph state machine for the upload pipeline.

Flow (normal):
  route_input → extract_excel / extract_ocr → deduplicate → save_to_db → END

Flow (human-in-the-loop confirm — rows pre-injected):
  route_input → deduplicate → save_to_db → END  (extraction skipped)
"""

from langgraph.graph import END, StateGraph

from app.agents.state import IngestionState
from app.agents.nodes.extraction import extract_excel_node, extract_ocr_node
from app.agents.nodes.dedup import deduplicate_node
from app.agents.nodes.persistence import save_to_db_node


def _route_by_file_type(state: IngestionState) -> str:
    """
    Router: decides which extraction node to run.
    If extracted_rows are already in state (injected by the confirm endpoint),
    skip extraction entirely and go straight to deduplication.
    """
    # Human-in-the-loop confirm path: rows already reviewed by doctor
    if state.get("extracted_rows") is not None:
        return "deduplicate"

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
                           ↘ (skip extraction if rows pre-injected) ↗
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
            "deduplicate": "deduplicate",  # bypass route
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
