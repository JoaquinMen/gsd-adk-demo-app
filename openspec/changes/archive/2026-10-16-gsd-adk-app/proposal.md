# Proposal

## Why

Consultants and operations staff at **GSD** (a tech consulting firm operating in the US and Argentina) need a unified conversational interface to answer both unstructured HR policy questions (holidays, parental leave, vacation, health benefits, and workplace videos) and quantitative project billing questions (logged hours by project, consultant, country, or date range). Building a single-agent web application on the Google Agent Development Kit (ADK) Web framework—with automated data seeding and multi-agent-ready tool routing—enables immediate end-to-end interactive querying without manually switching between PDF repositories and SQL consoles.

## What Changes

- Introduce an automated data and infrastructure seeding pipeline for **GSD** that:
  - Generates 3 mock HR policy PDF documents covering GSD's US and Argentina operations:
    1. `gsd_holidays_us_argentina.pdf` (holidays calendar and policy for the US and Argentina, including company onboarding/policy videos).
    2. `gsd_benefits_usa.pdf` (US paternal/parental leave, vacation/PTO, health coverage, and workplace policies/videos).
    3. `gsd_benefits_argentina.pdf` (Argentina paternal/parental leave, vacation days, health/prepaga coverage, and workplace policies/videos).
  - Uploads the generated PDFs to a Google Cloud Storage (GCS) bucket and automatically provisions a Vertex AI Search (`discoveryengine`) unstructured data store and triggers document import.
  - Creates and populates a BigQuery dataset and table (`gsd_billing.project_billing_hours`) with realistic mock project tracking and consultant billing hours across US and Argentina projects.
- Introduce a Google ADK Web application package (`gsd_agent`) featuring a single router agent (`root_agent`) defaulting to `gemini-3.5-flash`:
  - Integrates the **Vertex AI Search Tool** (`VertexAiSearchTool`) for grounded natural-language retrieval over the HR PDFs while bypassing single-tool-per-agent constraints so the root agent can route across multiple tools and remain ready for future multi-agent expansion.
  - Integrates the **BigQuery Tool** (`BigQueryToolset` in read-only mode) to execute quantitative SQL queries over GSD's project tracking and billing hours dataset.
- Expand `.env` (and `.env.example`) configuration to centralize GCP project/location, default model (`gemini-3.5-flash`), BigQuery dataset/table identifiers, GCS bucket name, and Vertex AI Search datastore identifiers.

## Capabilities

### New Capabilities
- `hr-policy-search`: Generation of GSD mock HR PDF documents (US/Argentina holidays and country-specific benefits/workplace policies), GCS storage upload, automated Vertex AI Search datastore provisioning/import, and ADK grounded search tool integration.
- `project-billing-analytics`: Schema definition, automated BigQuery dataset/table seeding with mock GSD consulting billing hours, and read-only ADK BigQuery tool integration for quantitative project and time-tracking queries.
- `adk-web-router-agent`: Single-agent ADK Web application (`root_agent` using `gemini-3.5-flash`) that routes user intents between the Vertex AI Search HR tool and the BigQuery billing tool in a modular, multi-agent-ready structure.

### Modified Capabilities
<!-- None - greenfield project with no existing specs. -->

## Impact

- **New Code & Scripts**:
  - `gsd_agent/` package (`__init__.py`, `agent.py`, `config.py`, `tools/`) exposing `root_agent` for `adk web`.
  - `scripts/` provisioning and seeding utilities (`generate_hr_pdfs.py`, `seed_bigquery.py`, `setup_vertex_search.py`, and unified runner `setup_all.py`).
  - `pyproject.toml` / `requirements.txt` declaring `google-adk`, `google-cloud-bigquery`, `google-cloud-storage`, `google-cloud-discoveryengine`, `reportlab` (or `fpdf2`), and `python-dotenv`.
- **Configuration**:
  - Updates `.env` with `GEMINI_MODEL=gemini-3.5-flash`, `BQ_DATASET_ID`, `BQ_TABLE_ID`, `GCS_HR_BUCKET`, `VERTEX_SEARCH_LOCATION`, and `VERTEX_SEARCH_DATASTORE_ID`.
- **Cloud Resources (`fedex-mlops`)**:
  - BigQuery dataset `gsd_billing` and table `project_billing_hours`.
  - GCS bucket for GSD HR PDFs and Vertex AI Search Data Store in Discovery Engine.

