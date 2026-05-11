"""
LangSmith initialization and configuration.
Provides tracing and monitoring for LangGraph agents.
"""

import logging
import os
from typing import Optional

from app.core.config import settings

logger = logging.getLogger("careremind.langsmith")


def initialize_langsmith() -> bool:
    """
    Initialize LangSmith tracing if enabled.

    Sets environment variables that LangChain/LangGraph automatically detect.

    Returns:
        bool: True if LangSmith was initialized, False otherwise
    """
    if not settings.ENABLE_LANGSMITH:
        logger.info("LangSmith tracing disabled (ENABLE_LANGSMITH=False)")
        return False

    if not settings.LANGSMITH_API_KEY:
        logger.warning(
            "LangSmith enabled but LANGSMITH_API_KEY not set — tracing will not work"
        )
        return False

    # Set environment variables for LangChain/LangGraph auto-detection
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT
    os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGSMITH_ENDPOINT

    logger.info(
        "LangSmith tracing enabled — project: %s, endpoint: %s",
        settings.LANGSMITH_PROJECT,
        settings.LANGSMITH_ENDPOINT,
    )

    return True


def get_langsmith_metadata(
    tenant_id: Optional[str] = None, user_id: Optional[str] = None, **extra_metadata
) -> dict:
    """
    Generate metadata dict for LangSmith traces.

    Use this to add context to your agent runs:

    ```python
    result = await graph.ainvoke(
        state,
        config={"metadata": get_langsmith_metadata(tenant_id="123", operation="upload")}
    )
    ```

    Args:
        tenant_id: Doctor/clinic ID
        user_id: Patient or user ID
        **extra_metadata: Additional key-value pairs

    Returns:
        dict: Metadata for LangSmith trace
    """
    metadata = {
        "environment": settings.ENVIRONMENT,
        "service": "careremind-api",
    }

    if tenant_id:
        metadata["tenant_id"] = tenant_id

    if user_id:
        metadata["user_id"] = user_id

    metadata.update(extra_metadata)

    return metadata


def get_langsmith_tags(*tags: str) -> list[str]:
    """
    Generate tags list for LangSmith traces.

    Use this to categorize your agent runs:

    ```python
    result = await graph.ainvoke(
        state,
        config={"tags": get_langsmith_tags("ingestion", "excel", "production")}
    )
    ```

    Args:
        *tags: Tag strings

    Returns:
        list[str]: Tags for LangSmith trace
    """
    base_tags = [settings.ENVIRONMENT]
    return base_tags + list(tags)
