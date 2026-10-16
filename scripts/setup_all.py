"""Unified provisioning and data seeding runner for the GSD ADK Web application."""

from __future__ import annotations

import argparse
from typing import Any, Dict

from gsd_agent.config import load_config
from scripts.generate_hr_pdfs import DEFAULT_OUTPUT_DIR, generate_all_hr_pdfs
from scripts.seed_bigquery import seed_bigquery_billing_table
from scripts.setup_vertex_search import setup_vertex_search_pipeline


def run_all_setup(
    skip_vertex_search: bool = False,
    skip_bigquery: bool = False,
    wait_for_import: bool = False,
) -> Dict[str, Any]:
    """Execute PDF generation, Vertex AI Search provisioning, and BigQuery seeding in sequence."""
    config = load_config()
    summary: Dict[str, Any] = {"project_id": config.project_id}

    print("=== Step 1/3: Generating GSD Mock HR PDFs ===")
    pdfs = generate_all_hr_pdfs(output_dir=DEFAULT_OUTPUT_DIR)
    summary["pdfs"] = {name: str(path) for name, path in pdfs.items()}

    if not skip_vertex_search:
        print("\n=== Step 2/3: Provisioning GCS Bucket & Vertex AI Search DataStore ===")
        summary["vertex_search"] = setup_vertex_search_pipeline(
            config=config,
            pdf_dir=DEFAULT_OUTPUT_DIR,
            wait_for_import=wait_for_import,
        )
    else:
        print("\n=== Step 2/3: Skipped Vertex AI Search provisioning ===")

    if not skip_bigquery:
        print("\n=== Step 3/3: Provisioning & Seeding BigQuery Billing Table ===")
        summary["bigquery"] = seed_bigquery_billing_table(config=config)
    else:
        print("\n=== Step 3/3: Skipped BigQuery seeding ===")

    print("\n=== GSD Setup Complete ===")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Provision all GSD demo data: generate 3 HR PDFs, setup Vertex AI Search, and seed BigQuery."
    )
    parser.add_argument(
        "--skip-vertex-search",
        action="store_true",
        help="Skip GCS upload and Vertex AI Search datastore creation/import.",
    )
    parser.add_argument(
        "--skip-bigquery",
        action="store_true",
        help="Skip BigQuery dataset/table creation and seeding.",
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait for the Vertex AI Search document import operation to finish.",
    )
    args = parser.parse_args()
    run_all_setup(
        skip_vertex_search=args.skip_vertex_search,
        skip_bigquery=args.skip_bigquery,
        wait_for_import=args.wait,
    )


if __name__ == "__main__":
    main()

