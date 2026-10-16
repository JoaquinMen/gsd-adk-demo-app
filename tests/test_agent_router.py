"""Unit tests for the GSD root router agent (`gsd_agent.agent`)."""

from unittest.mock import MagicMock

from google.adk.agents import LlmAgent
from google.adk.tools import VertexAiSearchTool
from google.auth.credentials import Credentials

try:
    from google.adk.integrations.bigquery import BigQueryToolset
except ImportError:  # pragma: no cover
    from google.adk.tools.bigquery import BigQueryToolset

import gsd_agent
from gsd_agent.agent import build_root_agent


def test_root_agent_exported_and_uses_gemini_3_5_flash():
    """Verify gsd_agent exports root_agent configured with gemini-3.5-flash and both tools."""
    mock_creds = MagicMock(spec=Credentials)
    agent = build_root_agent(bq_credentials=mock_creds)

    assert isinstance(agent, LlmAgent)
    assert agent.name == "gsd_operations_router_agent"
    assert agent.model == "gemini-3.5-flash"
    assert len(agent.tools) == 2

    tool_types = {type(t) for t in agent.tools}
    assert VertexAiSearchTool in tool_types
    assert BigQueryToolset in tool_types

    # Verify instruction contains both datastore path and BigQuery table FQN
    assert "gsd-hr-policies-ds" in agent.instruction
    assert "fedex-mlops.gsd_billing.project_billing_hours" in agent.instruction
    assert "READ-ONLY" in agent.instruction

    # Verify package-level export for `adk web`
    assert isinstance(gsd_agent.root_agent, LlmAgent)
    assert gsd_agent.root_agent.model == "gemini-3.5-flash"
    assert gsd_agent.root_agent.canonical_model.client_kwargs == {"location": "global"}

