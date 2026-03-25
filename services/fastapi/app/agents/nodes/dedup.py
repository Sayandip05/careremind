"""
Dedup node — wraps DedupAgent for the ingestion graph.
"""

import logging

from app.agents.dedup_agent import DedupAgent
from app.agents.state import IngestionState

logger = logging.getLogger("careremind.agents.nodes.dedup")

_dedup_agent = DedupAgent()


async def deduplicate_node(state: IngestionState) -> dict:
    """Node: deduplicate extracted rows against existing patients in DB."""
    rows = state.get("extracted_rows", [])

    if not rows:
        return {
            "new_rows": [],
            "duplicate_rows": [],
        }

    result = await _dedup_agent.deduplicate(
        rows=rows,
        tenant_id=state["tenant_id"],
        db=state["db"],
    )

    return {
        "new_rows": result["new"],
        "duplicate_rows": result["duplicates"],
    }
