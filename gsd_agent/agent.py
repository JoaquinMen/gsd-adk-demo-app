"""ADK Web entrypoint defining the GSD single-agent router (`root_agent`)."""

from __future__ import annotations

from typing import Optional

from google.adk.agents import LlmAgent
from google.auth.credentials import Credentials

from gsd_agent.config import GSDConfig, load_config
from gsd_agent.prompts import build_router_instruction
from gsd_agent.tools.billing_bq import build_bigquery_toolset
from gsd_agent.tools.hr_search import build_hr_search_tool


def build_root_agent(
    config: Optional[GSDConfig] = None,
    bq_credentials: Optional[Credentials] = None,
) -> LlmAgent:
    """Instantiate the single-agent router (`root_agent`) for the GSD ADK Web application."""
    cfg = config or load_config()
    hr_search_tool = build_hr_search_tool(config=cfg)
    bigquery_toolset = build_bigquery_toolset(config=cfg, credentials=bq_credentials)

    agent = LlmAgent(
        name="gsd_operations_router_agent",
        model=cfg.gemini_model,
        description=(
            "GSD Consulting single-agent router that answers unstructured HR policy questions "
            "(US & Argentina holidays, parental leave, vacation, health benefits, company videos) "
            "via Vertex AI Search and quantitative project billing questions via BigQuery."
        ),
        instruction=build_router_instruction(cfg),
        tools=[hr_search_tool, bigquery_toolset],
    )
    if cfg.use_vertexai and cfg.gemini_model.startswith("gemini-3"):
        agent.canonical_model.client_kwargs = {"location": "global"}
    return agent


root_agent: LlmAgent = build_root_agent()

