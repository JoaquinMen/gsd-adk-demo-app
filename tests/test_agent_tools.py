"""Unit tests for gsd_agent.tools (VertexAiSearchTool and BigQueryToolset)."""

from unittest.mock import MagicMock

from google.auth.credentials import Credentials

try:
    from google.adk.integrations.bigquery.config import WriteMode
except ImportError:  # pragma: no cover
    from google.adk.tools.bigquery.config import WriteMode

from gsd_agent.config import GSDConfig
from gsd_agent.tools.billing_bq import build_bigquery_toolset
from gsd_agent.tools.hr_search import build_hr_search_tool


def _sample_config() -> GSDConfig:
    return GSDConfig(
        project_id="fedex-mlops",
        location="us-central1",
        gemini_model="gemini-3.5-flash",
        bq_dataset_id="gsd_billing",
        bq_table_id="project_billing_hours",
        gcs_hr_bucket="fedex-mlops-gsd-hr-docs",
        vertex_search_location="global",
        vertex_search_datastore_id="gsd-hr-policies-ds",
    )


def test_build_hr_search_tool_sets_datastore_and_bypass():
    """Verify VertexAiSearchTool uses full datastore path and bypass_multi_tools_limit=True."""
    cfg = _sample_config()
    tool = build_hr_search_tool(config=cfg)

    assert tool.data_store_id == (
        "projects/fedex-mlops/locations/global/collections/default_collection/dataStores/gsd-hr-policies-ds"
    )
    assert tool.bypass_multi_tools_limit is True


def test_build_bigquery_toolset_enforces_read_only_write_mode():
    """Verify BigQueryToolset is configured with WriteMode.BLOCKED and compute_project_id."""
    cfg = _sample_config()
    mock_creds = MagicMock(spec=Credentials)
    bq_toolset = build_bigquery_toolset(config=cfg, credentials=mock_creds)

    assert bq_toolset._tool_settings.write_mode == WriteMode.BLOCKED
    assert bq_toolset._tool_settings.compute_project_id == "fedex-mlops"

