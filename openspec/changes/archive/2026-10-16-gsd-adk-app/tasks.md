# Tasks

## 1. Environment & Project Scaffolding

- [x] 1.1 Create `pyproject.toml` and `requirements.txt` declaring `google-adk`, `google-cloud-bigquery`, `google-cloud-storage`, `google-cloud-discoveryengine`, `fpdf2`, `python-dotenv`, and `pytest`, and verify dependencies install cleanly into a local virtual environment
- [x] 1.2 Update `.env` and create `.env.example` with `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `GOOGLE_GENAI_USE_VERTEXAI=TRUE`, `GEMINI_MODEL=gemini-3.5-flash`, `BQ_DATASET_ID=gsd_billing`, `BQ_TABLE_ID=project_billing_hours`, `GCS_HR_BUCKET=fedex-mlops-gsd-hr-docs`, `VERTEX_SEARCH_LOCATION=global`, and `VERTEX_SEARCH_DATASTORE_ID=gsd-hr-policies-ds`, and verify all keys are present
- [x] 1.3 Implement `gsd_agent/config.py` to load and validate `.env` configuration settings (including constructing the full Vertex AI Search datastore path and BigQuery table FQN) and verify via unit tests in `tests/test_config.py`

## 2. Unstructured HR PDF Generation & Vertex AI Search Provisioning

- [x] 2.1 Implement `scripts/generate_hr_pdfs.py` to generate the 3 mock GSD PDFs (`gsd_holidays_us_argentina.pdf`, `gsd_benefits_usa.pdf`, and `gsd_benefits_argentina.pdf`) covering US and Argentina holidays, paternal/parental leave, vacation/PTO, health coverage, workplace policies, and company videos, and verify via `tests/test_generate_hr_pdfs.py` that all 3 non-empty PDF files are created
- [x] 2.2 Implement `scripts/setup_vertex_search.py` to idempotently create the GCS bucket (`GCS_HR_BUCKET`), upload the 3 generated HR PDFs, create the Vertex AI Search unstructured datastore (`VERTEX_SEARCH_DATASTORE_ID`), and trigger a GCS document import job, and verify with unit/mock tests and live execution against `fedex-mlops`

## 3. Structured BigQuery Billing Table Provisioning & Seeding

- [x] 3.1 Implement `scripts/seed_bigquery.py` to idempotently create dataset `BQ_DATASET_ID` and table `BQ_TABLE_ID` (`gsd_billing.project_billing_hours`) and populate mock GSD consulting billing rows across Project A, Project B, Project C, US and Argentina consultants, and recent relative dates, and verify via `tests/test_seed_bigquery.py` and a live BigQuery row-count query
- [x] 3.2 Create `scripts/setup_all.py` to orchestrate PDF generation, Vertex AI Search provisioning, and BigQuery seeding in sequence, and document the setup commands in `README.md`, verifying `python -m scripts.setup_all --help` runs cleanly

## 4. ADK Web Single-Agent Router & Tools Implementation

- [x] 4.1 Implement `gsd_agent/tools/hr_search.py` to instantiate `VertexAiSearchTool` configured with the full datastore resource path and `bypass_multi_tools_limit=True`, and verify tool initialization in `tests/test_agent_tools.py`
- [x] 4.2 Implement `gsd_agent/tools/billing_bq.py` to instantiate `BigQueryToolset` with Application Default Credentials and `WriteMode.BLOCKED` (read-only enforcement), and verify read-only configuration in `tests/test_agent_tools.py`
- [x] 4.3 Implement `gsd_agent/prompts.py`, `gsd_agent/agent.py`, and `gsd_agent/__init__.py` exporting `root_agent` (`LlmAgent` with default model `gemini-3.5-flash`, routing instructions for GSD HR PDFs and BigQuery billing table, and both tools attached), and verify via `tests/test_agent_router.py` that `root_agent` loads with model `gemini-3.5-flash` and both tools registered
- [x] 4.4 Update `README.md` with instructions for launching `adk web` and example HR policy and BigQuery billing prompts, and verify the documented commands match the package structure

## 5. End-to-End Integration Verification

- [x] 5.1 Execute the provisioning pipeline against `fedex-mlops` and verify the BigQuery table `gsd_billing.project_billing_hours` returns expected aggregations and the Vertex AI Search datastore `gsd-hr-policies-ds` has imported the 3 GSD HR PDFs
- [x] 5.2 Run an end-to-end ADK Runner / `adk web` smoke check verifying that `root_agent` routes HR questions (US/Argentina holidays and benefits) to Vertex AI Search and quantitative billing questions (Project A hours, last week's billed hours) to BigQuery

## Workflow follow-up

- Archive the change with `/opsx-archive` after implementation and verification are complete.

