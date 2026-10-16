"""End-to-end verification of BigQuery billing table, Vertex AI Search documents, and ADK Web agent."""

from __future__ import annotations

import asyncio
from google.cloud import bigquery
from google.cloud import discoveryengine_v1 as discoveryengine
from google.genai import types
from google.adk.runners import InMemoryRunner

from gsd_agent.agent import build_root_agent, root_agent
from gsd_agent.config import load_config


def verify_bigquery_aggregations() -> None:
    """Verify BigQuery table exists and returns expected quantitative aggregations."""
    cfg = load_config()
    client = bigquery.Client(project=cfg.project_id, location=cfg.location)

    query_project_a = f"""
        SELECT
            project_name,
            COUNT(*) AS entry_count,
            ROUND(SUM(hours_billed), 2) AS total_hours,
            ROUND(SUM(CASE WHEN is_billable THEN hours_billed ELSE 0 END), 2) AS billable_hours
        FROM `{cfg.bq_table_fqn}`
        WHERE project_name = 'Project A'
        GROUP BY project_name
    """
    rows_a = list(client.query(query_project_a).result())
    assert len(rows_a) == 1, "Expected rows for Project A"
    row_a = rows_a[0]
    print(
        f"[BigQuery] Project A -> entries={row_a.entry_count}, "
        f"total_hours={row_a.total_hours}, billable_hours={row_a.billable_hours}"
    )

    query_last_week = f"""
        SELECT
            COUNT(*) AS entry_count,
            ROUND(SUM(hours_billed), 2) AS total_hours_last_7d
        FROM `{cfg.bq_table_fqn}`
        WHERE work_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
    """
    rows_week = list(client.query(query_last_week).result())[0]
    print(
        f"[BigQuery] Last 7 Days -> entries={rows_week.entry_count}, "
        f"total_hours={rows_week.total_hours_last_7d}"
    )
    assert rows_week.total_hours_last_7d and rows_week.total_hours_last_7d > 0


def verify_vertex_search_documents() -> None:
    """Verify the Vertex AI Search datastore exists and lists imported HR PDF documents."""
    cfg = load_config()
    ds_client = discoveryengine.DataStoreServiceClient()
    ds = ds_client.get_data_store(name=cfg.vertex_search_datastore_path)
    print(f"[Vertex AI Search] DataStore verified: {ds.name} ({ds.display_name})")

    doc_client = discoveryengine.DocumentServiceClient()
    branch = f"{cfg.vertex_search_datastore_path}/branches/default_branch"
    docs = list(doc_client.list_documents(parent=branch))
    print(f"[Vertex AI Search] Indexed documents count in default_branch: {len(docs)}")
    for d in docs:
        uri = getattr(d.content, "uri", "") if d.content else ""
        print(f"  - doc id={d.id} uri={uri}")


async def verify_adk_agent_smoke() -> None:
    """Verify ADK Runner and agent routing for quantitative BigQuery and unstructured HR prompts."""
    print(f"[ADK] Loaded root_agent name={root_agent.name} model={root_agent.model}")
    assert root_agent.model == "gemini-3.5-flash"

    runner = InMemoryRunner(agent=root_agent, app_name="gsd_smoke_app")
    session = await runner.session_service.create_session(
        app_name="gsd_smoke_app",
        user_id="smoke_user",
    )

    test_cases = [
        {
            "prompt": "How many billing hours are logged for Project A, and how many hours were billed over the last 7 days?",
            "expected_tool": "execute_sql",
            "expected_substrings": ["341.5", "296.5", "225"],
        },
        {
            "prompt": "What is GSD's paternal leave policy in the US and in Argentina, and what holiday falls on May 25?",
            "expected_tool": "discovery_engine_search",
            "expected_substrings": ["12", "6", "May 25"],
        },
    ]

    for case in test_cases:
        prompt = case["prompt"]
        print(f"\n[ADK Smoke Prompt] {prompt}")
        content = types.Content(role="user", parts=[types.Part(text=prompt)])
        called_tools: list[str] = []
        final_text = ""

        async for event in runner.run_async(
            user_id="smoke_user",
            session_id=session.id,
            new_message=content,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.function_call and part.function_call.name:
                        called_tools.append(part.function_call.name)
                        print(f"  [Tool Call] {part.function_call.name}")
                if event.is_final_response():
                    final_text = "".join(p.text or "" for p in event.content.parts).strip()

        print(f"[ADK Final Response ({root_agent.model})]:\n{final_text[:500]}...")
        assert case["expected_tool"] in called_tools, (
            f"Expected tool {case['expected_tool']} in {called_tools}"
        )
        for substr in case["expected_substrings"]:
            assert substr in final_text, f"Expected '{substr}' in response: {final_text}"


def main() -> None:
    verify_bigquery_aggregations()
    verify_vertex_search_documents()
    asyncio.run(verify_adk_agent_smoke())


if __name__ == "__main__":
    main()

