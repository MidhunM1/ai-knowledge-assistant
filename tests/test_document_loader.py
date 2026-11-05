
import pytest

from pathlib import Path
from pypdf import PdfWriter

from src.document_loader import load_pdf, load_multiple_pdfs


def create_test_pdf(file_path):

    writer = PdfWriter()

    writer.add_blank_page(
        width=300,
        height=300
    )

    with open(file_path, "wb") as file:
        writer.write(file)


def test_pdf_not_found():

    with pytest.raises(FileNotFoundError):

        load_pdf("missing_file.pdf")


def test_wrong_file_type(tmp_path):

    file_path = tmp_path / "sample.txt"

    file_path.write_text("This is not a PDF.")

    with pytest.raises(ValueError):

        load_pdf(file_path)


def test_empty_file(tmp_path):

    file_path = tmp_path / "empty.pdf"

    file_path.write_bytes(b"")

    with pytest.raises(ValueError):

        load_pdf(file_path)


def test_load_multiple_pdfs_empty():

    with pytest.raises(ValueError):

        load_multiple_pdfs([])


def test_blank_pdf_has_no_text(tmp_path):

    file_path = tmp_path / "blank.pdf"

    create_test_pdf(file_path)

    documents = load_pdf(file_path)

    assert documents == []
