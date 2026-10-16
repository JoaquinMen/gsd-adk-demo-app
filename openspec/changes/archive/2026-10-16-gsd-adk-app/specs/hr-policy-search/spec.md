# Spec Delta

## Purpose

Provides unstructured HR policy document generation, cloud storage ingestion, automated Vertex AI Search datastore provisioning, and grounded natural-language retrieval for GSD's US and Argentina workforce policies.

## ADDED Requirements

### Requirement: Mock HR PDF document generation for GSD
The system SHALL generate three distinct PDF documents for the consulting firm GSD: one covering US and Argentina holidays, one covering US employee benefits and workplace policies, and one covering Argentina employee benefits and workplace policies.

#### Scenario: Generate holiday and benefits PDFs
- **WHEN** the HR document generation process is executed
- **THEN** the system produces `gsd_holidays_us_argentina.pdf`, `gsd_benefits_usa.pdf`, and `gsd_benefits_argentina.pdf` containing structured policy text on holidays, paternal/parental leave, vacation/PTO, health coverage, workplace policies, and company video references for both countries

### Requirement: Automated GCS upload and Vertex AI Search datastore provisioning
The system SHALL upload the generated HR PDF documents to the configured Google Cloud Storage bucket and automatically provision and populate a Vertex AI Search unstructured datastore with those documents.

#### Scenario: Provision datastore and import PDFs from GCS
- **WHEN** the Vertex AI Search provisioning process runs with valid project, bucket, and datastore environment variables
- **THEN** the system ensures the GCS bucket exists, uploads all three PDF files, ensures the target Vertex AI Search datastore exists, and triggers a document import operation from the GCS bucket URI

#### Scenario: Idempotent re-execution of datastore provisioning
- **WHEN** the provisioning process runs and the target GCS bucket or Vertex AI Search datastore already exists
- **THEN** the system reuses the existing resources without failing and refreshes or reconciles the imported PDF documents

### Requirement: Grounded natural-language retrieval over HR PDFs
The system SHALL answer natural-language questions regarding GSD holidays, paternal leave, vacation policies, health benefits, and company videos by querying the Vertex AI Search datastore.

#### Scenario: Query country-specific benefits policy
- **WHEN** a user asks a question about paternal leave, vacation days, or health benefits for either the US or Argentina
- **THEN** the search tool retrieves grounded passages from the corresponding country's GSD benefits PDF and returns policy details specific to that country

#### Scenario: Query US and Argentina holiday schedules
- **WHEN** a user asks about upcoming company holidays in the US or Argentina
- **THEN** the search tool retrieves the relevant holiday dates and policy rules from `gsd_holidays_us_argentina.pdf`

#### Scenario: Out-of-document policy inquiry
- **WHEN** a user asks an HR policy question whose answer is not present in the indexed GSD PDF documents
- **THEN** the system explicitly states that the requested information could not be found in the official GSD HR documents rather than fabricating a policy

