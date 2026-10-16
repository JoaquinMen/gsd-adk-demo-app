"""Create and seed the GSD BigQuery project billing hours dataset and table."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from google.cloud import bigquery

from gsd_agent.config import GSDConfig, load_config

BILLING_SCHEMA: List[bigquery.SchemaField] = [
    bigquery.SchemaField("entry_id", "STRING", mode="REQUIRED", description="Unique billing log entry ID"),
    bigquery.SchemaField("work_date", "DATE", mode="REQUIRED", description="Date the hours were logged"),
    bigquery.SchemaField("project_id", "STRING", mode="REQUIRED", description="Project identifier (e.g., PRJ-A)"),
    bigquery.SchemaField("project_name", "STRING", mode="REQUIRED", description="Project name (e.g., Project A)"),
    bigquery.SchemaField("client_name", "STRING", mode="REQUIRED", description="Client organization name"),
    bigquery.SchemaField("consultant_name", "STRING", mode="REQUIRED", description="GSD consultant full name"),
    bigquery.SchemaField("country", "STRING", mode="REQUIRED", description="Consultant country (US or Argentina)"),
    bigquery.SchemaField("role", "STRING", mode="REQUIRED", description="Consultant role on the project"),
    bigquery.SchemaField("hours_billed", "FLOAT64", mode="REQUIRED", description="Number of hours logged"),
    bigquery.SchemaField("hourly_rate_usd", "FLOAT64", mode="REQUIRED", description="Billing rate in USD per hour"),
    bigquery.SchemaField("is_billable", "BOOL", mode="REQUIRED", description="True if client-billable, False if internal"),
    bigquery.SchemaField("task_category", "STRING", mode="REQUIRED", description="Work category (Architecture, Engineering, QA, etc.)"),
    bigquery.SchemaField("notes", "STRING", mode="NULLABLE", description="Summary of work completed"),
]


def build_mock_billing_rows(reference_date: Optional[date] = None) -> List[Dict[str, Any]]:
    """Build deterministic mock billing records anchored to `reference_date` (defaults to today)."""
    base_date = reference_date or date.today()

    consultants = [
        # US Team
        {
            "name": "Alice Johnson",
            "country": "US",
            "role": "Principal Cloud Architect",
            "rate": 195.0,
            "project_id": "PRJ-A",
            "project_name": "Project A",
            "client_name": "Apex Retail Corp",
        },
        {
            "name": "Marcus Vance",
            "country": "US",
            "role": "Senior ML Engineer",
            "rate": 175.0,
            "project_id": "PRJ-B",
            "project_name": "Project B",
            "client_name": "Andes FinTech S.A.",
        },
        {
            "name": "Elena Rostova",
            "country": "US",
            "role": "Staff Data Engineer",
            "rate": 165.0,
            "project_id": "PRJ-C",
            "project_name": "Project C",
            "client_name": "Global Logistics Hub",
        },
        # Argentina Team
        {
            "name": "Mateo Gomez",
            "country": "Argentina",
            "role": "Tech Lead & Backend Architect",
            "rate": 135.0,
            "project_id": "PRJ-A",
            "project_name": "Project A",
            "client_name": "Apex Retail Corp",
        },
        {
            "name": "Valentina Morales",
            "country": "Argentina",
            "role": "Senior AI Engineer",
            "rate": 130.0,
            "project_id": "PRJ-B",
            "project_name": "Project B",
            "client_name": "Andes FinTech S.A.",
        },
        {
            "name": "Santiago Alvarez",
            "country": "Argentina",
            "role": "Senior Data Platform Engineer",
            "rate": 125.0,
            "project_id": "PRJ-A",
            "project_name": "Project A",
            "client_name": "Apex Retail Corp",
        },
    ]

    categories = [
        ("Architecture", "Designed Vertex AI & BigQuery integration patterns"),
        ("Development", "Implemented core data pipeline and ADK agent tools"),
        ("Analytics", "Built executive KPI queries and schema validation"),
        ("Discovery", "Client stakeholder workshop and technical scoping"),
        ("Testing", "End-to-end integration testing and latency tuning"),
    ]

    rows: List[Dict[str, Any]] = []
    entry_counter = 1001

    # Generate 21 days of recent billing logs (covering last week and prior two weeks)
    for day_offset in range(0, 21):
        work_day = base_date - timedelta(days=day_offset)
        # Skip Sundays; keep Saturdays empty for normal work
        if work_day.weekday() >= 5:
            continue

        for idx, c in enumerate(consultants):
            cat, desc = categories[(day_offset + idx) % len(categories)]
            # Deterministic hours between 6.0 and 8.5
            hours = 8.0 if (day_offset + idx) % 3 != 0 else 6.5
            is_billable = True if (day_offset + idx) % 7 != 0 else False

            rows.append(
                {
                    "entry_id": f"LOG-{entry_counter}",
                    "work_date": work_day.isoformat(),
                    "project_id": c["project_id"],
                    "project_name": c["project_name"],
                    "client_name": c["client_name"],
                    "consultant_name": c["name"],
                    "country": c["country"],
                    "role": c["role"],
                    "hours_billed": hours,
                    "hourly_rate_usd": c["rate"],
                    "is_billable": is_billable,
                    "task_category": cat,
                    "notes": f"{desc} for {c['project_name']}",
                }
            )
            entry_counter += 1

    # Also add a few explicit holiday-emergency records on 2026 holidays for cross-tool queries
    special_entries = [
        {
            "entry_id": f"LOG-{entry_counter}",
            "work_date": "2026-05-25",
            "project_id": "PRJ-A",
            "project_name": "Project A",
            "client_name": "Apex Retail Corp",
            "consultant_name": "Mateo Gomez",
            "country": "Argentina",
            "role": "Tech Lead & Backend Architect",
            "hours_billed": 4.0,
            "hourly_rate_usd": 135.0,
            "is_billable": True,
            "task_category": "Support",
            "notes": "Pre-authorized holiday cutover support on May 25 (Dia de la Revolucion de Mayo / Memorial Day)",
        },
        {
            "entry_id": f"LOG-{entry_counter + 1}",
            "work_date": "2026-07-09",
            "project_id": "PRJ-B",
            "project_name": "Project B",
            "client_name": "Andes FinTech S.A.",
            "consultant_name": "Valentina Morales",
            "country": "Argentina",
            "role": "Senior AI Engineer",
            "hours_billed": 5.0,
            "hourly_rate_usd": 130.0,
            "is_billable": True,
            "task_category": "Support",
            "notes": "Pre-authorized production deployment on Argentina Independence Day (July 9)",
        },
    ]
    rows.extend(special_entries)
    return rows


def seed_bigquery_billing_table(
    config: Optional[GSDConfig] = None,
    bq_client: Optional[bigquery.Client] = None,
    reference_date: Optional[date] = None,
) -> Dict[str, Any]:
    """Idempotently create dataset/table and load GSD mock project billing rows."""
    cfg = config or load_config()
    client = bq_client or bigquery.Client(project=cfg.project_id, location=cfg.location)

    dataset_ref = f"{cfg.project_id}.{cfg.bq_dataset_id}"
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = cfg.location
    dataset.description = "GSD Consulting project tracking and billing hours dataset"
    client.create_dataset(dataset, exists_ok=True)
    print(f"Ensured BigQuery dataset exists: {dataset_ref} (location={cfg.location})")

    table_fqn = cfg.bq_table_fqn
    rows = build_mock_billing_rows(reference_date=reference_date)

    job_config = bigquery.LoadJobConfig(
        schema=BILLING_SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    print(f"Loading {len(rows)} mock billing rows into {table_fqn} (WRITE_TRUNCATE) ...")
    load_job = client.load_table_from_json(
        rows,
        destination=table_fqn,
        job_config=job_config,
    )
    load_job.result()

    destination_table = client.get_table(table_fqn)
    print(f"Loaded {destination_table.num_rows} rows into {table_fqn}.")
    return {
        "table_fqn": table_fqn,
        "rows_loaded": len(rows),
        "table_num_rows": destination_table.num_rows,
    }


def main() -> None:
    seed_bigquery_billing_table()


if __name__ == "__main__":
    main()

