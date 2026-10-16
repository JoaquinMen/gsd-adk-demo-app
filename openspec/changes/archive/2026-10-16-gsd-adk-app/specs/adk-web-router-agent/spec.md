# Spec Delta

## Purpose

Defines the Google ADK Web application entrypoint, environment-driven configuration, and single-agent router that dispatches user queries to either the Vertex AI Search HR tool or the BigQuery billing tool using `gemini-3.5-flash`.

## ADDED Requirements

### Requirement: ADK Web interface discovery and default model configuration
The system SHALL expose a root ADK agent discoverable by the `adk web` CLI and configured to use `gemini-3.5-flash` as its default model unless overridden via `.env`.

#### Scenario: Launch agent in ADK Web
- **WHEN** an operator starts `adk web` from the workspace root
- **THEN** the ADK Web UI loads the GSD agent package, initializes `root_agent` with `gemini-3.5-flash`, and presents an interactive chat session

### Requirement: Centralized environment configuration
The system SHALL load GCP project, location, Gemini model, BigQuery dataset/table names, GCS bucket name, and Vertex AI Search datastore identifiers from the root `.env` file.

#### Scenario: Load resource identifiers from .env
- **WHEN** the agent or provisioning scripts start
- **THEN** they read `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `GEMINI_MODEL`, `BQ_DATASET_ID`, `BQ_TABLE_ID`, `GCS_HR_BUCKET`, `VERTEX_SEARCH_LOCATION`, and `VERTEX_SEARCH_DATASTORE_ID` from `.env` without requiring hardcoded resource names

### Requirement: Single-agent intent routing across HR Search and BigQuery tools
The root agent SHALL dynamically route user prompts to the Vertex AI Search HR tool for unstructured policy questions, to the BigQuery tool for structured billing/hours questions, or to both tools when a prompt spans both domains.

#### Scenario: Route HR policy question to Vertex AI Search tool
- **WHEN** a user asks a question about GSD holidays, paternal leave, vacation, health benefits, or company videos
- **THEN** the root agent invokes the Vertex AI Search tool rather than BigQuery and returns a grounded policy answer

#### Scenario: Route billing question to BigQuery tool
- **WHEN** a user asks a quantitative question about project tracking or logged billing hours
- **THEN** the root agent invokes the BigQuery tool rather than Vertex AI Search and returns the computed hours or breakdown

#### Scenario: Route hybrid question across both tools
- **WHEN** a user asks a question that requires both HR holiday/policy data and BigQuery project billing data in the same turn
- **THEN** the root agent invokes both tools without single-tool-per-agent API conflicts and synthesizes a unified response

