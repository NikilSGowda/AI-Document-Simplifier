from io import BytesIO

import fitz
from docx import Document
from fastapi.testclient import TestClient

import backend.app.document_extractor as extractor_module
import backend.app.main as main_module
from backend.app.main import app


client = TestClient(app)


def _upload(filename: str, content: bytes, content_type: str):
    return client.post(
        "/api/upload-document",
        files={"file": (filename, content, content_type)},
    )


def _make_pdf(text: str | None) -> bytes:
    document = fitz.open()
    page = document.new_page()
    if text:
        page.insert_text((72, 72), text)
    content = document.tobytes()
    document.close()
    return content


def _make_pdf_with_pages(page_count: int) -> bytes:
    document = fitz.open()
    for _ in range(page_count):
        document.new_page()
    content = document.tobytes()
    document.close()
    return content


def _make_docx() -> bytes:
    document = Document()
    document.add_paragraph("DOCX extraction works.")
    table = document.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "First cell"
    table.cell(0, 1).text = "Second cell"
    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def test_upload_extracts_utf8_txt() -> None:
    response = _upload("notes.txt", "Résumé details.".encode(), "text/plain")

    assert response.status_code == 200
    assert response.json() == {
        "filename": "notes.txt",
        "file_type": "txt",
        "extracted_text": "Résumé details.",
        "character_count": len("Résumé details."),
        "pages_requiring_ocr": [],
        "warnings": [],
    }


def test_upload_extracts_text_pdf_without_ocr_warning() -> None:
    response = _upload(
        "report.pdf",
        _make_pdf("This PDF has enough readable text to avoid OCR."),
        "application/pdf",
    )

    assert response.status_code == 200
    result = response.json()
    assert result["file_type"] == "pdf"
    assert "enough readable text" in result["extracted_text"]
    assert result["pages_requiring_ocr"] == []


def test_upload_reports_pdf_pages_that_need_ocr_without_running_it() -> None:
    response = _upload("scan.pdf", _make_pdf(None), "application/pdf")

    assert response.status_code == 200
    result = response.json()
    assert result["extracted_text"] == ""
    assert result["pages_requiring_ocr"] == [1]
    assert "OCR has not been run" in result["warnings"][0]


def test_upload_extracts_docx_paragraphs_and_tables() -> None:
    response = _upload(
        "report.docx",
        _make_docx(),
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

    assert response.status_code == 200
    result = response.json()
    assert result["file_type"] == "docx"
    assert "DOCX extraction works." in result["extracted_text"]
    assert "First cell | Second cell" in result["extracted_text"]


def test_upload_rejects_unsupported_extension() -> None:
    response = _upload("notes.rtf", b"some text", "text/plain")

    assert response.status_code == 415
    assert "Only TXT, PDF, and DOCX" in response.json()["detail"]


def test_upload_rejects_content_type_mismatch() -> None:
    response = _upload("notes.txt", b"plain text", "application/pdf")

    assert response.status_code == 415


def test_upload_rejects_empty_file() -> None:
    response = _upload("empty.txt", b"", "text/plain")

    assert response.status_code == 400
    assert response.json()["detail"] == "The uploaded file is empty."


def test_upload_rejects_oversized_file(monkeypatch) -> None:
    monkeypatch.setattr(main_module, "MAX_UPLOAD_BYTES", 8)

    response = _upload("large.txt", b"123456789", "text/plain")

    assert response.status_code == 413


def test_upload_rejects_pdf_over_page_limit(monkeypatch) -> None:
    monkeypatch.setattr(extractor_module, "MAX_PDF_PAGES", 1)

    response = _upload(
        "too-many-pages.pdf",
        _make_pdf_with_pages(2),
        "application/pdf",
    )

    assert response.status_code == 413
    assert "1-page processing limit" in response.json()["detail"]


def test_upload_rejects_corrupted_pdf() -> None:
    response = _upload("broken.pdf", b"%PDF-1.7\nnot a real PDF", "application/pdf")

    assert response.status_code == 422
    assert "corrupt or could not be read" in response.json()["detail"]


def test_upload_does_not_trust_filename_extension_alone() -> None:
    response = _upload("fake.pdf", b"this is actually text", "application/pdf")

    assert response.status_code == 422
    assert "not a valid PDF" in response.json()["detail"]
