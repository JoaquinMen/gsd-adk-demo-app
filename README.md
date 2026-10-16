# GSD Single-Agent ADK Web Application

A single-agent, multi-agent-ready web application built on the **Google Agent Development Kit (ADK)** Web framework (`adk web`) for **GSD** (a tech consulting firm operating in the United States and Argentina).

The root router agent (`root_agent`, powered by `gemini-3.5-flash`) manages two core tools:
1. **Vertex AI Search Tool (`VertexAiSearchTool`)** — Answers unstructured HR policy questions using three GSD HR PDF documents:
   - `gsd_holidays_us_argentina.pdf`: Official 2026 US and Argentina holiday calendars, holiday billing rules, and onboarding videos.
   - `gsd_benefits_usa.pdf`: US paternal/parental leave (12 weeks paid), PTO (20 days), BCBS health plans & HSA, 401(k) match, and workplace policies.
   - `gsd_benefits_argentina.pdf`: Argentina paternal/parental leave (6 weeks paid paternal leave), business-day vacation policy, OSDE 410 / Swiss Medical prepaga coverage, and connectivity stipends.
2. **BigQuery Tool (`BigQueryToolset`)** — Runs read-only SQL queries against `fedex-mlops.gsd_billing.project_billing_hours` to answer quantitative questions about project tracking and logged consultant hours across US and Argentina teams.

---

## 1. Environment Configuration (`.env`)

Copy `.env.example` to `.env` (already pre-configured in this repository):

```dotenv
GOOGLE_CLOUD_PROJECT=fedex-mlops
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GEMINI_MODEL=gemini-3.5-flash

# BigQuery Configuration (Structured Billing Data)
BQ_DATASET_ID=gsd_billing
BQ_TABLE_ID=project_billing_hours

# GCS & Vertex AI Search Configuration (Unstructured HR Data)
GCS_HR_BUCKET=fedex-mlops-gsd-hr-docs
VERTEX_SEARCH_LOCATION=global
VERTEX_SEARCH_DATASTORE_ID=gsd-hr-policies-ds
```

---

## 2. Installation & Data Provisioning

Install dependencies into the local virtual environment:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Run the unified setup pipeline to generate the 3 mock HR PDFs, upload them to GCS, provision/import the Vertex AI Search datastore, and seed the BigQuery billing table:

```bash
.venv/bin/python -m scripts.setup_all
```

Or run individual provisioning steps:

```bash
# Generate the 3 mock HR PDFs locally into data/hr_pdfs/
.venv/bin/python -m scripts.generate_hr_pdfs

# Upload PDFs to GCS and create/import the Vertex AI Search datastore
.venv/bin/python -m scripts.setup_vertex_search

# Create and seed the BigQuery project billing hours table
.venv/bin/python -m scripts.seed_bigquery
```

---

## 3. Running the ADK Web Application

Launch the ADK Web interface from the repository root:

```bash
.venv/bin/adk web
```

Open the URL printed in your terminal (default `http://127.0.0.1:8000`) and select **`gsd_agent`** from the agent dropdown.

### Example Prompts to Try

**Unstructured HR Policy Questions (routed to Vertex AI Search):**
- *"What is GSD's paternal leave policy in Argentina compared to the US?"*
- *"How many vacation days do employees get in Argentina and how are they counted?"*
- *"What are the official GSD company holidays in the US and Argentina in May and July 2026?"*
- *"What health insurance plans does GSD provide in the US and in Argentina, and what onboarding videos are available?"*

**Quantitative Billing Questions (routed to BigQuery):**
- *"How many billing hours are logged for Project A?"*
- *"Give me the total hours billed over the last week across all projects."*
- *"Break down total billable vs non-billable hours and total revenue by country (US vs Argentina)."*

**Cross-Tool Hybrid Questions (routed across both tools):**
- *"Were any billing hours logged on Argentina national holidays in May or July 2026, and what is GSD's policy on holiday billing rates?"*

