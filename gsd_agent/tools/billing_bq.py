"""BigQuery toolset factory for GSD structured project billing data."""

from __future__ import annotations

from typing import Optional

import google.auth
from google.auth.credentials import Credentials

try:
    from google.adk.integrations.bigquery import BigQueryCredentialsConfig, BigQueryToolset
    from google.adk.integrations.bigquery.config import BigQueryToolConfig, WriteMode
except ImportError:  # pragma: no cover
    from google.adk.tools.bigquery import BigQueryCredentialsConfig, BigQueryToolset
    from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode

from gsd_agent.config import GSDConfig, load_config


def build_bigquery_toolset(
    config: Optional[GSDConfig] = None,
    credentials: Optional[Credentials] = None,
) -> BigQueryToolset:
    """Create a read-only BigQueryToolset scoped to GSD project billing analytics."""
    cfg = config or load_config()

    creds = credentials
    if creds is None:
        try:
            creds, _ = google.auth.default()
        except Exception:
            creds = None

    credentials_config = BigQueryCredentialsConfig(credentials=creds) if creds is not None else None
    tool_config = BigQueryToolConfig(
        write_mode=WriteMode.BLOCKED,
        compute_project_id=cfg.project_id,
    )

    return BigQueryToolset(
        credentials_config=credentials_config,
        bigquery_tool_config=tool_config,
    )

