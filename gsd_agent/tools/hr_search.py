"""Vertex AI Search tool factory for GSD unstructured HR policy PDFs."""

from __future__ import annotations

from typing import Optional

from google.adk.tools import VertexAiSearchTool

from gsd_agent.config import GSDConfig, load_config


def build_hr_search_tool(config: Optional[GSDConfig] = None) -> VertexAiSearchTool:
    """Create a VertexAiSearchTool configured for GSD HR policies with multi-tool bypass enabled."""
    cfg = config or load_config()
    return VertexAiSearchTool(
        data_store_id=cfg.vertex_search_datastore_path,
        bypass_multi_tools_limit=True,
    )

