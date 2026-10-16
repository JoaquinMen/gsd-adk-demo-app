"""Environment configuration loader and validator for the GSD ADK application."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

DEFAULT_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


@dataclass(frozen=True)
class GSDConfig:
    """Typed configuration for GSD ADK agent and data provisioning scripts."""

    project_id: str
    location: str = "us-central1"
    use_vertexai: bool = True
    gemini_model: str = "gemini-3.5-flash"
    bq_dataset_id: str = "gsd_billing"
    bq_table_id: str = "project_billing_hours"
    gcs_hr_bucket: str = "fedex-mlops-gsd-hr-docs"
    vertex_search_location: str = "global"
    vertex_search_datastore_id: str = "gsd-hr-policies-ds"

    def validate(self) -> "GSDConfig":
        """Validate that all required fields are non-empty."""
        required_fields = {
            "GOOGLE_CLOUD_PROJECT": self.project_id,
            "GOOGLE_CLOUD_LOCATION": self.location,
            "GEMINI_MODEL": self.gemini_model,
            "BQ_DATASET_ID": self.bq_dataset_id,
            "BQ_TABLE_ID": self.bq_table_id,
            "GCS_HR_BUCKET": self.gcs_hr_bucket,
            "VERTEX_SEARCH_LOCATION": self.vertex_search_location,
            "VERTEX_SEARCH_DATASTORE_ID": self.vertex_search_datastore_id,
        }
        missing = [key for key, value in required_fields.items() if not str(value).strip()]
        if missing:
            raise ValueError(f"Missing required configuration variable(s): {', '.join(missing)}")
        return self

    @property
    def bq_table_fqn(self) -> str:
        """Return the fully qualified BigQuery table identifier (`project.dataset.table`)."""
        return f"{self.project_id}.{self.bq_dataset_id}.{self.bq_table_id}"

    @property
    def vertex_search_datastore_path(self) -> str:
        """Return the full Discovery Engine DataStore resource path required by VertexAiSearchTool."""
        if self.vertex_search_datastore_id.startswith("projects/"):
            return self.vertex_search_datastore_id
        return (
            f"projects/{self.project_id}/locations/{self.vertex_search_location}"
            f"/collections/default_collection/dataStores/{self.vertex_search_datastore_id}"
        )


def _ensure_ssl_cert_file() -> None:
    """Ensure SSL_CERT_FILE points to a valid CA bundle (fixes macOS Python 3.13 httpx ConnectError)."""
    current = os.environ.get("SSL_CERT_FILE", "").strip()
    if current and Path(current).exists():
        return
    try:
        import certifi

        ca_bundle = certifi.where()
        if Path(ca_bundle).exists():
            os.environ["SSL_CERT_FILE"] = ca_bundle
            os.environ.setdefault("REQUESTS_CA_BUNDLE", ca_bundle)
            return
    except ImportError:  # pragma: no cover
        pass
    if Path("/etc/ssl/cert.pem").exists():
        os.environ["SSL_CERT_FILE"] = "/etc/ssl/cert.pem"


_ensure_ssl_cert_file()


def load_config(env_path: Optional[Path] = None, override: bool = False) -> GSDConfig:
    """Load `.env` variables and return a validated `GSDConfig` instance."""
    target_env = env_path if env_path is not None else DEFAULT_ENV_PATH
    if target_env.exists():
        load_dotenv(dotenv_path=target_env, override=override)

    _ensure_ssl_cert_file()

    # Ensure google-genai / google-adk sees Vertex AI configuration in os.environ
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")

    use_vertex_str = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "TRUE").strip().upper()
    use_vertexai = use_vertex_str in {"1", "TRUE", "YES"}

    config = GSDConfig(
        project_id=os.getenv("GOOGLE_CLOUD_PROJECT", "").strip(),
        location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1").strip(),
        use_vertexai=use_vertexai,
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash").strip(),
        bq_dataset_id=os.getenv("BQ_DATASET_ID", "gsd_billing").strip(),
        bq_table_id=os.getenv("BQ_TABLE_ID", "project_billing_hours").strip(),
        gcs_hr_bucket=os.getenv("GCS_HR_BUCKET", "fedex-mlops-gsd-hr-docs").strip(),
        vertex_search_location=os.getenv("VERTEX_SEARCH_LOCATION", "global").strip(),
        vertex_search_datastore_id=os.getenv("VERTEX_SEARCH_DATASTORE_ID", "gsd-hr-policies-ds").strip(),
    )
    return config.validate()

