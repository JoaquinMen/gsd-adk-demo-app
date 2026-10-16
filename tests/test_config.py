"""Unit tests for gsd_agent.config."""

from pathlib import Path
import pytest

from gsd_agent.config import GSDConfig, load_config


def test_load_config_from_repo_env():
    """Verify that the repository .env loads expected GSD defaults including gemini-3.5-flash."""
    cfg = load_config(override=True)
    assert cfg.project_id == "fedex-mlops"
    assert cfg.location == "us-central1"
    assert cfg.use_vertexai is True
    assert cfg.gemini_model == "gemini-3.5-flash"
    assert cfg.bq_dataset_id == "gsd_billing"
    assert cfg.bq_table_id == "project_billing_hours"
    assert cfg.gcs_hr_bucket == "fedex-mlops-gsd-hr-docs"
    assert cfg.vertex_search_location == "global"
    assert cfg.vertex_search_datastore_id == "gsd-hr-policies-ds"
    assert cfg.bq_table_fqn == "fedex-mlops.gsd_billing.project_billing_hours"
    assert (
        cfg.vertex_search_datastore_path
        == "projects/fedex-mlops/locations/global/collections/default_collection/dataStores/gsd-hr-policies-ds"
    )


def test_vertex_search_datastore_path_preserves_full_resource_name():
    """If a full resource path is already provided, do not double-prefix it."""
    full_path = "projects/my-proj/locations/us/collections/default_collection/dataStores/custom-ds"
    cfg = GSDConfig(project_id="my-proj", vertex_search_datastore_id=full_path)
    assert cfg.vertex_search_datastore_path == full_path


def test_config_validation_raises_on_missing_project_id(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Ensure missing GOOGLE_CLOUD_PROJECT raises a clear ValueError."""
    empty_env = tmp_path / ".env"
    empty_env.write_text("GOOGLE_CLOUD_PROJECT=\n", encoding="utf-8")
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)

    with pytest.raises(ValueError, match="GOOGLE_CLOUD_PROJECT"):
        load_config(env_path=empty_env, override=True)

