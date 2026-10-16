"""Unit tests for scripts.seed_bigquery."""

from datetime import date
from unittest.mock import MagicMock

from gsd_agent.config import GSDConfig
from scripts.seed_bigquery import BILLING_SCHEMA, build_mock_billing_rows, seed_bigquery_billing_table


def test_build_mock_billing_rows_schema_and_coverage():
    """Verify mock rows include Project A/B/C, US & Argentina consultants, and expected columns."""
    ref = date(2026, 10, 15)
    rows = build_mock_billing_rows(reference_date=ref)
    assert len(rows) > 50

    expected_cols = {field.name for field in BILLING_SCHEMA}
    for row in rows:
        assert set(row.keys()) == expected_cols

    projects = {r["project_name"] for r in rows}
    assert {"Project A", "Project B", "Project C"}.issubset(projects)

    countries = {r["country"] for r in rows}
    assert countries == {"US", "Argentina"}

    # Ensure unique entry_ids
    entry_ids = [r["entry_id"] for r in rows]
    assert len(entry_ids) == len(set(entry_ids))


def test_seed_bigquery_billing_table_uses_write_truncate():
    """Verify seed_bigquery_billing_table creates dataset and loads rows idempotently."""
    cfg = GSDConfig(
        project_id="fedex-mlops",
        location="us-central1",
        bq_dataset_id="gsd_billing",
        bq_table_id="project_billing_hours",
    )
    mock_bq = MagicMock()
    mock_job = MagicMock()
    mock_bq.load_table_from_json.return_value = mock_job
    mock_table = MagicMock()
    mock_table.num_rows = 92
    mock_bq.get_table.return_value = mock_table

    result = seed_bigquery_billing_table(
        config=cfg,
        bq_client=mock_bq,
        reference_date=date(2026, 10, 15),
    )

    mock_bq.create_dataset.assert_called_once()
    mock_bq.load_table_from_json.assert_called_once()
    assert result["table_fqn"] == "fedex-mlops.gsd_billing.project_billing_hours"
    assert result["table_num_rows"] == 92

