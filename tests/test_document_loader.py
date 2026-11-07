from unittest.mock import MagicMock

import pytest

import src.document_loader as loader


def test_pdf_not_found():
    with pytest.raises(FileNotFoundError):
        loader.load_pdf("missing.pdf")


def test_reject_non_pdf_file(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("Sample text")

    with pytest.raises(ValueError, match="Only PDF files"):
        loader.load_pdf(file_path)


def test_reject_empty_pdf(tmp_path):
    file_path = tmp_path / "empty.pdf"
    file_path.write_bytes(b"")

    with pytest.raises(ValueError, match="is empty"):
        loader.load_pdf(file_path)


def test_load_pdf_extracts_text(tmp_path, monkeypatch):
    file_path = tmp_path / "sample.pdf"
    file_path.write_bytes(b"fake pdf")

    page = MagicMock()
    page.extract_text.return_value = (
        "This is a sufficiently long sample PDF text for testing."
    )

    reader = MagicMock()
    reader.is_encrypted = False
    reader.pages = [page]

    monkeypatch.setattr(loader, "PdfReader", lambda *args, **kwargs: reader)

    documents = loader.load_pdf(file_path)

    assert len(documents) == 1
    assert documents[0].page_content.startswith("This is")
    assert documents[0].metadata["source"] == "sample.pdf"
    assert documents[0].metadata["page"] == 1


def test_ocr_used_when_extracted_text_is_short(tmp_path, monkeypatch):
    file_path = tmp_path / "scanned.pdf"
    file_path.write_bytes(b"fake pdf")

    page = MagicMock()
    page.extract_text.return_value = "Short"

    reader = MagicMock()
    reader.is_encrypted = False
    reader.pages = [page]

    monkeypatch.setattr(loader, "PdfReader", lambda *args, **kwargs: reader)
    monkeypatch.setattr(
        loader,
        "extract_text_with_ocr",
        lambda path, page_number: "Text extracted using OCR successfully."
    )

    documents = loader.load_pdf(file_path)

    assert len(documents) == 1
    assert "OCR" in documents[0].page_content


def test_load_multiple_pdfs(tmp_path, monkeypatch):
    first = tmp_path / "first.pdf"
    second = tmp_path / "second.pdf"

    first.write_bytes(b"fake")
    second.write_bytes(b"fake")

    monkeypatch.setattr(
        loader,
        "load_pdf",
        lambda path: [
            loader.Document(
                page_content=f"Content from {path.name}",
                metadata={"source": path.name, "page": 1}
            )
        ]
    )

    documents = loader.load_multiple_pdfs([first, second])

    assert len(documents) == 2


def test_load_multiple_pdfs_with_no_documents(monkeypatch):
    monkeypatch.setattr(loader, "load_pdf", lambda path: [])

    with pytest.raises(ValueError, match="No readable text"):
        loader.load_multiple_pdfs(["sample.pdf"])