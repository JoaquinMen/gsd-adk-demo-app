"""Unit tests for scripts.setup_vertex_search."""

from pathlib import Path
from unittest.mock import MagicMock

from google.api_core.exceptions import NotFound

from gsd_agent.config import GSDConfig
from scripts.generate_hr_pdfs import EXPECTED_PDF_FILENAMES
from scripts.setup_vertex_search import (
    ensure_gcs_bucket_and_upload_pdfs,
    ensure_vertex_search_datastore,
    import_pdfs_into_datastore,
    setup_vertex_search_pipeline,
)


def _sample_config() -> GSDConfig:
    return GSDConfig(
        project_id="fedex-mlops",
        location="us-central1",
        gcs_hr_bucket="fedex-mlops-gsd-hr-docs",
        vertex_search_location="global",
        vertex_search_datastore_id="gsd-hr-policies-ds",
    )


def test_ensure_gcs_bucket_creates_bucket_and_uploads_three_pdfs(tmp_path: Path):
    """Verify bucket creation when missing and upload of all 3 generated PDFs."""
    cfg = _sample_config()
    mock_storage = MagicMock()
    mock_storage.lookup_bucket.return_value = None
    mock_bucket = MagicMock()
    mock_storage.create_bucket.return_value = mock_bucket

    uris = ensure_gcs_bucket_and_upload_pdfs(
        config=cfg,
        pdf_dir=tmp_path,
        storage_client=mock_storage,
    )

    mock_storage.create_bucket.assert_called_once_with("fedex-mlops-gsd-hr-docs", location="us-central1")
    assert len(uris) == 3
    for name in EXPECTED_PDF_FILENAMES:
        assert f"gs://fedex-mlops-gsd-hr-docs/{name}" in uris


def test_ensure_vertex_search_datastore_idempotent_when_existing():
    """Verify that an existing datastore is reused without calling create_data_store."""
    cfg = _sample_config()
    mock_ds_client = MagicMock()
    mock_existing = MagicMock()
    mock_existing.name = cfg.vertex_search_datastore_path
    mock_ds_client.get_data_store.return_value = mock_existing

    name = ensure_vertex_search_datastore(config=cfg, ds_client=mock_ds_client)

    assert name == cfg.vertex_search_datastore_path
    mock_ds_client.create_data_store.assert_not_called()


def test_ensure_vertex_search_datastore_creates_when_not_found():
    """Verify datastore creation when get_data_store raises NotFound."""
    cfg = _sample_config()
    mock_ds_client = MagicMock()
    mock_ds_client.get_data_store.side_effect = NotFound("DataStore not found")

    mock_op = MagicMock()
    mock_created = MagicMock()
    mock_created.name = cfg.vertex_search_datastore_path
    mock_op.result.return_value = mock_created
    mock_ds_client.create_data_store.return_value = mock_op

    name = ensure_vertex_search_datastore(config=cfg, ds_client=mock_ds_client)

    assert name == cfg.vertex_search_datastore_path
    mock_ds_client.create_data_store.assert_called_once()


def test_setup_vertex_search_pipeline_end_to_end_mock(tmp_path: Path):
    """Verify the full pipeline wires GCS upload, datastore creation, and document import."""
    cfg = _sample_config()
    mock_storage = MagicMock()
    mock_bucket = MagicMock()
    mock_storage.lookup_bucket.return_value = mock_bucket

    mock_ds_client = MagicMock()
    mock_existing = MagicMock()
    mock_existing.name = cfg.vertex_search_datastore_path
    mock_ds_client.get_data_store.return_value = mock_existing

    mock_doc_client = MagicMock()
    mock_import_op = MagicMock()
    mock_import_op.operation.name = "projects/fedex-mlops/locations/global/operations/import-123"
    mock_doc_client.import_documents.return_value = mock_import_op

    result = setup_vertex_search_pipeline(
        config=cfg,
        pdf_dir=tmp_path,
        wait_for_import=False,
        storage_client=mock_storage,
        ds_client=mock_ds_client,
        doc_client=mock_doc_client,
    )

    assert result["bucket"] == "fedex-mlops-gsd-hr-docs"
    assert len(result["uploaded_uris"]) == 3
    assert result["datastore_name"] == cfg.vertex_search_datastore_path
    assert result["import_operation_name"] == "projects/fedex-mlops/locations/global/operations/import-123"

