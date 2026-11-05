
from pypdf import PdfReader
from langchain_core.documents import Document
from pathlib import Path


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

        reader = PdfReader(str(file_path), strict=False)

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

            try:
                text = page.extract_text()

            except Exception:
                continue

            if text and text.strip():

                document = Document(
                    page_content=text.strip(),
                    metadata={
                        "source": file_path.name,
                        "page": page_number + 1
                    }
                )

                documents.append(document)

        return documents

    except Exception as error:

        if isinstance(error, (ValueError, FileNotFoundError)):
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
