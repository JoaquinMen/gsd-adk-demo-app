"""Unit tests for scripts.generate_hr_pdfs."""

from pathlib import Path

from scripts.generate_hr_pdfs import EXPECTED_PDF_FILENAMES, generate_all_hr_pdfs


def test_generate_all_hr_pdfs_creates_three_valid_pdfs(tmp_path: Path):
    """Verify that all 3 GSD HR policy PDFs are generated and contain valid PDF headers."""
    result = generate_all_hr_pdfs(output_dir=tmp_path)
    assert set(result.keys()) == set(EXPECTED_PDF_FILENAMES)

    for filename, pdf_path in result.items():
        assert pdf_path.exists(), f"{filename} was not created"
        assert pdf_path.stat().st_size > 1000, f"{filename} is unexpectedly small"
        raw_bytes = pdf_path.read_bytes()
        assert raw_bytes.startswith(b"%PDF-"), f"{filename} does not have a valid PDF header"

