"""Provision GCS bucket, upload GSD HR PDFs, create Vertex AI Search DataStore, and import documents."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional

from google.api_core.client_options import ClientOptions
from google.api_core.exceptions import AlreadyExists, NotFound
from google.cloud import discoveryengine_v1 as discoveryengine
from google.cloud import storage

from gsd_agent.config import GSDConfig, load_config
from scripts.generate_hr_pdfs import DEFAULT_OUTPUT_DIR, EXPECTED_PDF_FILENAMES, generate_all_hr_pdfs


def _discovery_client_options(location: str) -> Optional[ClientOptions]:
    """Return regional ClientOptions when location is not 'global'."""
    if location and location != "global":
        return ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
    return None


def ensure_gcs_bucket_and_upload_pdfs(
    config: GSDConfig,
    pdf_dir: Path = DEFAULT_OUTPUT_DIR,
    storage_client: Optional[storage.Client] = None,
) -> List[str]:
    """Idempotently create the GCS HR bucket and upload the 3 GSD HR PDFs."""
    # Ensure local PDFs exist first
    missing_local = [name for name in EXPECTED_PDF_FILENAMES if not (pdf_dir / name).exists()]
    if missing_local:
        generate_all_hr_pdfs(output_dir=pdf_dir)

    client = storage_client or storage.Client(project=config.project_id)
    bucket = client.lookup_bucket(config.gcs_hr_bucket)
    if bucket is None:
        bucket = client.create_bucket(config.gcs_hr_bucket, location=config.location)
        print(f"Created GCS bucket: gs://{config.gcs_hr_bucket} (location={config.location})")
    else:
        print(f"Reusing existing GCS bucket: gs://{config.gcs_hr_bucket}")

    uploaded_uris: List[str] = []
    for filename in EXPECTED_PDF_FILENAMES:
        local_path = pdf_dir / filename
        blob = bucket.blob(filename)
        blob.upload_from_filename(str(local_path), content_type="application/pdf")
        uri = f"gs://{config.gcs_hr_bucket}/{filename}"
        uploaded_uris.append(uri)
        print(f"  Uploaded {local_path.name} -> {uri}")

    return uploaded_uris


def ensure_vertex_search_datastore(
    config: GSDConfig,
    ds_client: Optional[discoveryengine.DataStoreServiceClient] = None,
) -> str:
    """Idempotently create the unstructured Vertex AI Search datastore and return its resource name."""
    client = ds_client or discoveryengine.DataStoreServiceClient(
        client_options=_discovery_client_options(config.vertex_search_location)
    )
    datastore_name = config.vertex_search_datastore_path

    try:
        existing = client.get_data_store(name=datastore_name)
        print(f"Reusing existing Vertex AI Search DataStore: {existing.name}")
        return existing.name
    except NotFound:
        pass

    parent = (
        f"projects/{config.project_id}/locations/{config.vertex_search_location}"
        "/collections/default_collection"
    )
    data_store = discoveryengine.DataStore(
        display_name="GSD HR Policies and Holidays (US & Argentina)",
        industry_vertical=discoveryengine.IndustryVertical.GENERIC,
        solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
        content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
    )
    request = discoveryengine.CreateDataStoreRequest(
        parent=parent,
        data_store=data_store,
        data_store_id=config.vertex_search_datastore_id,
    )

    try:
        print(f"Creating Vertex AI Search DataStore: {datastore_name} ...")
        operation = client.create_data_store(request=request)
        response = operation.result(timeout=300)
        print(f"Created Vertex AI Search DataStore: {response.name}")
        return response.name
    except AlreadyExists:
        print(f"Vertex AI Search DataStore already exists: {datastore_name}")
        return datastore_name


def import_pdfs_into_datastore(
    config: GSDConfig,
    doc_client: Optional[discoveryengine.DocumentServiceClient] = None,
    wait_for_completion: bool = False,
    timeout_seconds: int = 600,
) -> str:
    """Trigger a GCS unstructured document import job into the Vertex AI Search datastore."""
    client = doc_client or discoveryengine.DocumentServiceClient(
        client_options=_discovery_client_options(config.vertex_search_location)
    )
    branch_parent = f"{config.vertex_search_datastore_path}/branches/default_branch"
    gcs_uri_pattern = f"gs://{config.gcs_hr_bucket}/*.pdf"

    request = discoveryengine.ImportDocumentsRequest(
        parent=branch_parent,
        gcs_source=discoveryengine.GcsSource(
            input_uris=[gcs_uri_pattern],
            data_schema="content",
        ),
        reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
    )

    print(f"Triggering document import from {gcs_uri_pattern} into {branch_parent} ...")
    operation = client.import_documents(request=request)
    op_name = operation.operation.name
    print(f"Started Vertex AI Search import operation: {op_name}")

    if wait_for_completion:
        print("Waiting for document import operation to finish...")
        operation.result(timeout=timeout_seconds)
        print("Document import completed.")

    return op_name


def setup_vertex_search_pipeline(
    config: Optional[GSDConfig] = None,
    pdf_dir: Path = DEFAULT_OUTPUT_DIR,
    wait_for_import: bool = False,
    storage_client: Optional[storage.Client] = None,
    ds_client: Optional[discoveryengine.DataStoreServiceClient] = None,
    doc_client: Optional[discoveryengine.DocumentServiceClient] = None,
) -> Dict[str, Any]:
    """Run the full GCS upload + Vertex AI Search datastore provisioning and import pipeline."""
    cfg = config or load_config()
    uploaded_uris = ensure_gcs_bucket_and_upload_pdfs(
        config=cfg,
        pdf_dir=pdf_dir,
        storage_client=storage_client,
    )
    datastore_name = ensure_vertex_search_datastore(
        config=cfg,
        ds_client=ds_client,
    )
    import_operation_name = import_pdfs_into_datastore(
        config=cfg,
        doc_client=doc_client,
        wait_for_completion=wait_for_import,
    )
    return {
        "bucket": cfg.gcs_hr_bucket,
        "uploaded_uris": uploaded_uris,
        "datastore_name": datastore_name,
        "import_operation_name": import_operation_name,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload GSD HR PDFs to GCS and provision/import Vertex AI Search datastore."
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait for the Vertex AI Search document import operation to complete.",
    )
    args = parser.parse_args()
    setup_vertex_search_pipeline(wait_for_import=args.wait)


if __name__ == "__main__":
    main()

