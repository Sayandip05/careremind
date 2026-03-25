"""
Extraction nodes — wrap ExcelAgent and OcrAgent for the ingestion graph.
Logic is identical to the original agents; these are thin LangGraph node wrappers.
"""

import logging

from app.agents.excel_agent import ExcelAgent
from app.agents.ocr_agent import OcrAgent
from app.agents.state import IngestionState

logger = logging.getLogger("careremind.agents.nodes.extraction")

_excel_agent = ExcelAgent()
_ocr_agent = OcrAgent()


async def extract_excel_node(state: IngestionState) -> dict:
    """Node: parse Excel file and return extracted rows."""
    result = await _excel_agent.extract(state["file_bytes"])

    return {
        "extracted_rows": result["rows"],
        "extraction_errors": result.get("errors", []),
        "extraction_skipped": result.get("skipped", 0),
        "total_rows": result.get("total_rows", 0),
        "source": "excel",
    }


async def extract_ocr_node(state: IngestionState) -> dict:
    """Node: run vision OCR on photo and return extracted rows."""
    result = await _ocr_agent.extract(state["file_bytes"])

    return {
        "extracted_rows": result["rows"],
        "extraction_errors": result.get("errors", []),
        "extraction_skipped": result.get("skipped", 0),
        "total_rows": result.get("total_rows", 0),
        "source": "photo",
    }
