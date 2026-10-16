# Design

## Context

The repository is currently a greenfield workspace containing `.env` (`GOOGLE_CLOUD_PROJECT=fedex-mlops`, `GOOGLE_CLOUD_LOCATION=us-central1`) and an initialized OpenSpec directory. In the `fedex-mlops` GCP project, neither the GSD project billing BigQuery dataset nor the HR PDF bucket/Vertex AI Search datastore exists yet. See `proposal.md` (Why & What Changes) for motivation and capability scope, and `specs/` for behavioral requirements.

Two technical constraints in Google Cloud and the Google Agent Development Kit (`google-adk`) shape this design:
1. **Gemini Grounding + Function Calling Constraint**: `VertexAiSearchTool` uses Gemini's native grounding retrieval, which cannot be combined directly in the same raw model request with standard function-calling tools (`BigQueryToolset`) unless `bypass_multi_tools_limit=True` (ADK Python v1.16+) or an `AgentTool` wrapper is used.
2. **Vertex AI Search Regional vs. Global Location**: While Gemini and BigQuery operate in `us-central1`, Vertex AI Search (`discoveryengine`) data stores default to multi-region `global` (with `projects/<project>/locations/<location>/collections/default_collection/dataStores/<datastore_id>` resource paths).

## Goals / Non-Goals

**Goals:**
- Provide an idempotent, one-command provisioning pipeline (`scripts/setup_all.py`) that generates the 3 mock GSD HR PDFs, uploads them to GCS, creates/imports into a Vertex AI Search datastore, and seeds the BigQuery billing table.
- Deliver a clean ADK Web package (`gsd_agent/`) discoverable by `adk web` from the workspace root, powered by `gemini-3.5-flash`.
- Enable single-agent tool routing across both `VertexAiSearchTool` and `BigQueryToolset` without Gemini multi-tool API errors, while keeping tool definitions modular so they can be promoted to `sub_agents` in future multi-agent iterations.
- Centralize all environment configuration in `.env`.

**Non-Goals:**
- Custom frontend UI development outside the official `adk web` interface.
- Write/mutation capabilities on BigQuery billing tables from the conversational agent.
- Terraform/IaC state management (provisioning is handled via lightweight Python SDK scripts for demo portability).

## Architecture & Directory Layout

```text
sdd-demo/
|-- .env                         # Runtime & provisioning configuration
|-- .env.example                 # Template configuration
|-- pyproject.toml               # Python dependencies (google-adk, GCP SDKs, fpdf2)
|-- gsd_agent/                   # ADK Web discoverable agent package
|   |-- __init__.py              # Exports root_agent
|   |-- agent.py                 # Defines root_agent (LlmAgent, gemini-3.5-flash)
|   |-- config.py                # Loads and validates .env settings
|   |-- prompts.py               # System instructions for GSD router & tools
|   +-- tools/
|       |-- __init__.py
|       |-- hr_search.py         # VertexAiSearchTool / AgentTool builder
|       +-- billing_bq.py        # BigQueryToolset (read-only) builder
+-- scripts/
    |-- generate_hr_pdfs.py      # Generates 3 mock GSD PDFs into data/hr_pdfs/
    |-- seed_bigquery.py         # Creates & populates gsd_billing.project_billing_hours
    |-- setup_vertex_search.py   # Creates GCS bucket, uploads PDFs, provisions Data Store
    +-- setup_all.py             # Orchestrates all 3 provisioning steps
```

## Decisions

### Decision 1: Single-Agent Multi-Tool Routing via `VertexAiSearchTool(bypass_multi_tools_limit=True)` (with `AgentTool` fallback)
- **Choice**: Configure `root_agent` as a single `LlmAgent` (`model="gemini-3.5-flash"`) and instantiate `VertexAiSearchTool(data_store_id=..., bypass_multi_tools_limit=True)` alongside `BigQueryToolset`. In ADK Python v1.16+, `bypass_multi_tools_limit=True` automatically wraps the grounding tool in an internal sub-agent tool call so it coexists cleanly with `BigQueryToolset`.
- **Rationale**: Preserves a single unified conversational agent in `adk web` that can call either tool—or both tools sequentially on hybrid prompts (e.g., correlating holiday dates from HR PDFs with logged hours in BigQuery)—while keeping each capability in its own module (`tools/hr_search.py` and `tools/billing_bq.py`) for easy future promotion to `sub_agents`.
- **Alternatives Considered**:
  - *Coordinator with `sub_agents` transfer (`transfer_to_agent`)*: Rejected as primary design because sub-agents take over the conversation turn, making single-agent synthesis across both tools clumsy.
  - *Raw `VertexAiSearchTool` without bypass*: Rejected because Gemini API returns a `400 INVALID_ARGUMENT` error when mixing native grounding retrieval and function declarations in the same request.

### Decision 2: Read-Only `BigQueryToolset` Scoped by System Instructions
- **Choice**: Use `google.adk.tools.bigquery.BigQueryToolset` configured with Application Default Credentials (`google.auth.default()`) and `BigQueryToolConfig(write_mode=WriteMode.BLOCKED)`, paired with explicit dataset/table schema context in the root agent's system prompt (`fedex-mlops.gsd_billing.project_billing_hours`).
- **Rationale**: `BigQueryToolset` gives the agent full flexibility to answer arbitrary quantitative questions ("total hours for Project A", "hours billed over the last week", "breakdown by US vs Argentina consultants") while `WriteMode.BLOCKED` guarantees read-only safety. Injecting the table name and column schema into the agent instruction avoids unnecessary `list_dataset_ids` / `get_table_info` round-trips on every query.
- **Alternatives Considered**:
  - *Hardcoded Python query functions*: Rejected because natural-language analytical queries vary widely in grouping, filtering, and time windows.

### Decision 3: BigQuery Schema for `gsd_billing.project_billing_hours`
- **Choice**: Define the table with the following schema and seed ~60–100 rows spanning recent weeks (relative to execution date so "last week" and "this month" queries always return rich data) as well as 2026 holiday dates:
  - `entry_id` (`STRING`, REQUIRED)
  - `work_date` (`DATE`, REQUIRED)
  - `project_id` (`STRING`, REQUIRED) — e.g., `PRJ-A`, `PRJ-B`, `PRJ-C`
  - `project_name` (`STRING`, REQUIRED) — e.g., `Project A`, `Project B`, `Project C`
  - `client_name` (`STRING`, REQUIRED)
  - `consultant_name` (`STRING`, REQUIRED)
  - `country` (`STRING`, REQUIRED) — `US` or `Argentina`
  - `role` (`STRING`, REQUIRED)
  - `hours_billed` (`FLOAT64`, REQUIRED)
  - `hourly_rate_usd` (`FLOAT64`, REQUIRED)
  - `is_billable` (`BOOL`, REQUIRED)
  - `task_category` (`STRING`, REQUIRED)
  - `notes` (`STRING`, NULLABLE)
- **Rationale**: Generating dates dynamically relative to `datetime.date.today()` ensures time-relative prompts like *"Give me the total hours billed over the last week"* always produce non-empty, deterministic answers whenever the demo is run.

### Decision 4: Programmatic PDF Generation (`fpdf2` / `reportlab`) & Discovery Engine Provisioning
- **Choice**: Generate the 3 PDFs (`gsd_holidays_us_argentina.pdf`, `gsd_benefits_usa.pdf`, `gsd_benefits_argentina.pdf`) in Python with clear section headings, tables, and policy text for GSD, upload them to `gs://<GCS_HR_BUCKET>/`, and use `google-cloud-discoveryengine` (`DataStoreServiceClient` and `DocumentServiceClient`) to create the unstructured datastore (`SOLUTION_TYPE_SEARCH`, `CONTENT_CONFIG_CONTENT_REQUIRED`) and trigger `import_documents` with `ReconciliationMode.INCREMENTAL`.
- **Rationale**: Keeps the repository free of opaque binary blobs, makes policy text easy to inspect and tweak in code, and automates the entire GCP setup.

### Decision 5: Environment Variable Contract (`.env`)
- **Choice**: Standardize on the following keys in `.env` (and symlink or load into `gsd_agent/` so `adk web` picks them up automatically):
  ```dotenv
  GOOGLE_CLOUD_PROJECT=fedex-mlops
  GOOGLE_CLOUD_LOCATION=us-central1
  GOOGLE_GENAI_USE_VERTEXAI=TRUE
  GEMINI_MODEL=gemini-3.5-flash

  BQ_DATASET_ID=gsd_billing
  BQ_TABLE_ID=project_billing_hours

  GCS_HR_BUCKET=fedex-mlops-gsd-hr-docs
  VERTEX_SEARCH_LOCATION=global
  VERTEX_SEARCH_DATASTORE_ID=gsd-hr-policies-ds
  ```

## Risks / Trade-offs

- **[Risk] Vertex AI Search initial indexing latency** -> Document import into a freshly created Discovery Engine datastore can take 3–10 minutes before chunks become searchable. **Mitigation**: `setup_vertex_search.py` will poll/log operation status clearly and support `--wait` or status-check flags so the operator knows when indexing is complete.
- **[Risk] `gemini-3.5-flash` model availability in target region** -> If a specific Vertex AI region does not yet serve the exact `gemini-3.5-flash` endpoint identifier, model calls could fail. **Mitigation**: Configure `GEMINI_MODEL=gemini-3.5-flash` as the default in `.env` and `config.py` so it is honored everywhere while remaining configurable via `.env` without code edits.
- **[Risk] Relative date drift in BigQuery demo queries** -> Static seed dates go stale for prompts like "over the last week". **Mitigation**: `seed_bigquery.py` anchors generated `work_date` values relative to the current date (`today - N days`) using `WRITE_TRUNCATE` for idempotent refreshes.

## Migration Plan

1. Install project dependencies in a virtual environment (`uv` or `venv`).
2. Populate `.env` with the GSD resource variables.
3. Run `python -m scripts.setup_all` to generate the 3 PDFs, upload to GCS, create/import the Vertex AI Search datastore, and seed the BigQuery table.
4. Launch `adk web` from `/Users/joaquinmen/Desktop/sdd-demo` and select `gsd_agent` in the browser UI.
5. **Rollback**: Delete the `gsd_billing` BigQuery dataset, the `fedex-mlops-gsd-hr-docs` GCS bucket, and the `gsd-hr-policies-ds` Vertex AI Search datastore if teardown is desired.

