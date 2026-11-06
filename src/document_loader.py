
from pypdf import PdfReader
from langchain_core.documents import Document
from pathlib import Path


def extract_text_with_ocr(file_path, page_number):

    try:
        import pymupdf
        import pytesseract
        from PIL import Image
        from io import BytesIO

        # Connect Python to the Windows Tesseract installation
        pytesseract.pytesseract.tesseract_cmd = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )

        pdf = pymupdf.open(str(file_path))

        try:
            page = pdf[page_number]

            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(2, 2),
                alpha=False
            )

            image = Image.open(
                BytesIO(pixmap.tobytes("png"))
            )

            text = pytesseract.image_to_string(image)

            return text.strip()

        finally:
            pdf.close()

    except Exception as error:

        raise ValueError(
            f"OCR failed on page {page_number + 1} "
            f"of {file_path.name}: {error}. "
            "Check that Tesseract OCR is installed."
        )


def load_pdf(file_path):

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {file_path}"
        )

    if file_path.suffix.lower() != ".pdf":
        raise ValueError(
            "Only PDF files are supported."
        )

    if file_path.stat().st_size == 0:
        raise ValueError(
            f"{file_path.name} is empty."
        )

    try:

        reader = PdfReader(
            str(file_path),
            strict=False
        )

        if reader.is_encrypted:

            try:
                result = reader.decrypt("")

                if result == 0:
                    raise ValueError(
                        f"PDF is password protected: {file_path.name}"
                    )

            except Exception as error:
                raise ValueError(
                    f"Unable to open PDF {file_path.name}: {error}"
                )

        documents = []

        for page_number, page in enumerate(reader.pages):

            text = ""

            try:
                extracted_text = page.extract_text()

                if extracted_text:
                    text = extracted_text.strip()

            except Exception:
                text = ""

            # Use OCR when normal text extraction finds too little text
            if len(text) < 30:

                text = extract_text_with_ocr(
                    file_path,
                    page_number
                )

            if text:

                document = Document(
                    page_content=text,
                    metadata={
                        "source": file_path.name,
                        "page": page_number + 1
                    }
                )

                documents.append(document)

        return documents

    except Exception as error:

        if isinstance(
            error,
            (ValueError, FileNotFoundError)
        ):
            raise

        raise ValueError(
            f"Unable to read PDF {file_path.name}: {error}"
        )


def load_multiple_pdfs(file_paths):

    all_documents = []

    for file_path in file_paths:

        documents = load_pdf(file_path)

        all_documents.extend(documents)

    if not all_documents:

        raise ValueError(
            "No readable text found in the uploaded PDFs."
        )

    return all_documents
