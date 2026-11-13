import io
import os
import zipfile
from pathlib import PurePosixPath
from typing import TypedDict

import fitz
from docx import Document
from docx.opc.exceptions import OpcError, PackageNotFoundError
from lxml.etree import XMLSyntaxError


MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
MAX_PDF_PAGES = int(os.getenv("MAX_PDF_PAGES", "200"))
MIN_PDF_PAGE_TEXT_CHARACTERS = 20
MAX_DOCX_UNCOMPRESSED_BYTES = 50 * 1024 * 1024
MAX_DOCX_MEMBERS = 2_000

ALLOWED_CONTENT_TYPES = {
    ".txt": {"text/plain", "application/octet-stream"},
    ".pdf": {"application/pdf", "application/octet-stream"},
    ".docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/zip",
        "application/octet-stream",
    },
}


class UnsupportedDocumentError(ValueError):
    pass


class InvalidDocumentError(ValueError):
    pass


class EmptyDocumentError(InvalidDocumentError):
    pass


class DocumentLimitError(ValueError):
    pass


class ExtractedDocument(TypedDict):
    filename: str
    file_type: str
    extracted_text: str
    character_count: int
    pages_requiring_ocr: list[int]
    warnings: list[str]


def extract_document(
    filename: str | None,
    content_type: str | None,
    content: bytes,
) -> ExtractedDocument:
    safe_filename = _safe_filename(filename)
    extension = PurePosixPath(safe_filename).suffix.lower()
    if extension not in ALLOWED_CONTENT_TYPES:
        raise UnsupportedDocumentError("Only TXT, PDF, and DOCX files are supported.")

    normalized_content_type = (content_type or "").split(";", 1)[0].strip().lower()
    if normalized_content_type not in ALLOWED_CONTENT_TYPES[extension]:
        raise UnsupportedDocumentError(
            f"The content type does not match the .{extension[1:]} file format."
        )
    if not content:
        raise EmptyDocumentError("The uploaded file is empty.")

    if extension == ".txt":
        extracted_text = _extract_txt(content)
        pages_requiring_ocr: list[int] = []
        warnings: list[str] = []
    elif extension == ".pdf":
        extracted_text, pages_requiring_ocr = _extract_pdf(content)
        warnings = _ocr_warnings(pages_requiring_ocr)
    else:
        extracted_text = _extract_docx(content)
        pages_requiring_ocr = []
        warnings = []

    if not extracted_text.strip() and not pages_requiring_ocr:
        raise EmptyDocumentError("No readable text was found in the uploaded file.")

    return {
        "filename": safe_filename,
        "file_type": extension[1:],
        "extracted_text": extracted_text,
        "character_count": len(extracted_text),
        "pages_requiring_ocr": pages_requiring_ocr,
        "warnings": warnings,
    }


def _safe_filename(filename: str | None) -> str:
    basename = (filename or "").replace("\\", "/").rsplit("/", 1)[-1]
    safe_name = "".join(character for character in basename if character.isprintable())
    if not safe_name or len(safe_name) > 255:
        raise InvalidDocumentError("The uploaded filename is missing or invalid.")
    return safe_name


def _extract_txt(content: bytes) -> str:
    if b"\x00" in content:
        raise InvalidDocumentError("The TXT file contains binary data.")
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise InvalidDocumentError("The TXT file must use UTF-8 encoding.") from exc
    if content.startswith(b"%PDF-") or content.startswith(b"PK\x03\x04"):
        raise InvalidDocumentError("The file contents do not match the .txt extension.")
    return text


def _extract_pdf(content: bytes) -> tuple[str, list[int]]:
    if b"%PDF-" not in content[:1024]:
        raise InvalidDocumentError("The file contents are not a valid PDF.")

    try:
        with fitz.open(stream=content, filetype="pdf") as document:
            if document.needs_pass:
                raise InvalidDocumentError("Password-protected PDFs are not supported.")
            if document.page_count == 0:
                raise InvalidDocumentError("The PDF contains no pages.")
            if document.page_count > MAX_PDF_PAGES:
                raise DocumentLimitError(
                    f"The PDF exceeds the {MAX_PDF_PAGES}-page processing limit."
                )

            page_texts: list[str] = []
            pages_requiring_ocr: list[int] = []
            for page_number, page in enumerate(document, start=1):
                page_text = page.get_text("text")
                page_texts.append(page_text)
                if len(page_text.strip()) < MIN_PDF_PAGE_TEXT_CHARACTERS:
                    pages_requiring_ocr.append(page_number)
    except (InvalidDocumentError, DocumentLimitError):
        raise
    except (fitz.FileDataError, fitz.EmptyFileError, RuntimeError, ValueError) as exc:
        raise InvalidDocumentError("The PDF is corrupt or could not be read.") from exc

    return "\n\n".join(page_texts).strip(), pages_requiring_ocr


def _extract_docx(content: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            members = archive.infolist()
            if (
                len(members) > MAX_DOCX_MEMBERS
                or sum(member.file_size for member in members)
                > MAX_DOCX_UNCOMPRESSED_BYTES
            ):
                raise InvalidDocumentError("The DOCX archive exceeds processing limits.")
            member_names = set(archive.namelist())
            if not {
                "[Content_Types].xml",
                "word/document.xml",
            }.issubset(member_names):
                raise InvalidDocumentError("The file contents are not a valid DOCX.")

        document = Document(io.BytesIO(content))
    except InvalidDocumentError:
        raise
    except (
        zipfile.BadZipFile,
        KeyError,
        OpcError,
        PackageNotFoundError,
        ValueError,
        OSError,
        XMLSyntaxError,
    ) as exc:
        raise InvalidDocumentError("The DOCX is corrupt or could not be read.") from exc

    parts = [paragraph.text for paragraph in document.paragraphs]
    for table in document.tables:
        parts.extend(
            " | ".join(cell.text for cell in row.cells)
            for row in table.rows
        )
    return "\n".join(parts).strip()


def _ocr_warnings(pages_requiring_ocr: list[int]) -> list[str]:
    if not pages_requiring_ocr:
        return []
    pages = ", ".join(str(page) for page in pages_requiring_ocr)
    return [
        f"Pages {pages} contain little or no extractable text and require OCR. "
        "OCR has not been run."
    ]
