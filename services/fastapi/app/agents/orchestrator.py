"""
Orchestrator — Thin wrapper around the LangGraph ingestion graph.
Routes file type → correct agent → normalize → dedup → save to DB.
"""

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graphs.ingestion import ingestion_graph

logger = logging.getLogger("careremind.agents.orchestrator")


class Orchestrator:
    """
    Main pipeline controller.
    Delegates to the LangGraph ingestion graph for the full
    extract → dedup → save pipeline.
    """

    async def process(
        self,
        file_type: str,          # "excel" or "photo"
        file_bytes: bytes,
        tenant_id: str,
        db: AsyncSession,
    ) -> dict:
        """
        Full pipeline via LangGraph state graph.

        Returns:
            {
                "total_rows": int,
                "new_patients": int,
                "duplicates": int,
                "skipped": int,
                "errors": [str, ...],
            }
        """
        # Run the graph
        result = await ingestion_graph.ainvoke({
            "file_type": file_type,
            "file_bytes": file_bytes,
            "tenant_id": tenant_id,
            "db": db,
        })

        # Collect all errors
        errors = list(result.get("extraction_errors", []))
        errors.extend(result.get("save_errors", []))

        logger.info(
            "Pipeline complete: %d total, %d new, %d duplicates, %d skipped",
            result.get("total_rows", 0),
            result.get("saved_count", 0),
            len(result.get("duplicate_rows", [])),
            result.get("extraction_skipped", 0),
        )

        return {
            "total_rows": result.get("total_rows", 0),
            "new_patients": result.get("saved_count", 0),
            "duplicates": len(result.get("duplicate_rows", [])),
            "skipped": result.get("extraction_skipped", 0),
            "errors": errors,
        }
