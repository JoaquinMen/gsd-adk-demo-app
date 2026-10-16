# project-billing-analytics Specification

## Purpose

Provides structured BigQuery dataset and table provisioning, mock GSD consulting billing-hours seeding across US and Argentina teams, and read-only quantitative query execution for project tracking and logged hours.

## Requirements

### Requirement: Automated BigQuery billing dataset and table seeding
The system SHALL create a BigQuery dataset and table configured via environment variables and populate it with mock consulting billing records for GSD projects across the US and Argentina.

#### Scenario: Seed billing table with GSD project data
- **WHEN** the BigQuery seeding process is executed
- **THEN** the system creates the target dataset and table (if not already present) with schema columns covering `entry_id`, `work_date`, `project_id`, `project_name`, `client_name`, `consultant_name`, `country`, `role`, `hours_billed`, `hourly_rate_usd`, `is_billable`, `task_category`, and `notes`, and inserts mock rows covering multiple projects (including Project A, Project B, and Project C), recent weeks, and both US and Argentina consultants

#### Scenario: Idempotent BigQuery seeding
- **WHEN** the BigQuery seeding process is executed multiple times
- **THEN** the system replaces or cleanly refreshes the mock table rows without duplicating existing `entry_id` records

### Requirement: Quantitative querying of project billing hours
The system SHALL execute SQL queries against the GSD BigQuery billing table to answer quantitative user questions about logged hours, project totals, date ranges, and consultant or country breakdowns.

#### Scenario: Query total billing hours for a specific project
- **WHEN** a user asks "How many billing hours are logged for Project A?"
- **THEN** the system queries the BigQuery billing table filtered to Project A and returns the accurate sum of logged hours

#### Scenario: Query billing hours over a relative time window
- **WHEN** a user asks for total hours billed over a specific period such as the last week or current month
- **THEN** the system executes a date-filtered aggregation query on `work_date` and returns the total hours for that period

### Requirement: Read-only BigQuery enforcement
The system SHALL restrict all agent-initiated BigQuery operations to read-only queries and block any data mutation or DDL statements.

#### Scenario: Attempt to mutate billing data via agent
- **WHEN** a user prompt asks the agent to insert, update, delete, or drop records in the BigQuery billing table
- **THEN** the BigQuery tool blocks the write operation and the agent informs the user that billing records are read-only

